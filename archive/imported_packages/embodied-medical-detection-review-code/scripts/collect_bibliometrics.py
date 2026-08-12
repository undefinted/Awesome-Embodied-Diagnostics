#!/usr/bin/env python3
"""Collect and classify open bibliographic records for embodied clinical detection tasks.

Primary source: OpenAlex (cross-disciplinary). Supplemental sources: Europe PMC
and the arXiv API.
The script is intentionally deterministic: exact title/abstract phrase queries, fixed
task rules, DOI/title de-duplication, and one primary task per included work.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable


CUTOFF = "2026-08-06"
START_DATE = "1900-01-01"
USER_AGENT = "EmbodiedClinicalDetectionBibliometrics/1.0 (open reproducible research)"


@dataclass(frozen=True)
class Task:
    code: str
    class_code: str
    class_en: str
    class_zh: str
    task_en: str
    task_zh: str
    phrases: tuple[str, ...]
    task_pattern: str
    definition: str
    exclusions: str


TASKS: tuple[Task, ...] = (
    Task("A1", "A", "Active observational sensing", "主动观察式检测",
         "Robotic ultrasound / sonography", "机器人超声/超声扫查",
         ("robotic ultrasound", "robot-assisted ultrasound", "robotized ultrasound",
          "robotised ultrasound", "autonomous ultrasound", "telerobotic ultrasound",
          "robotic ultrasonography", "robot-assisted ultrasonography", "robotic sonography"),
         r"ultra(?:sound|sonograph\w*)|sonograph\w*|echograph\w*",
         "机器人主动改变探头位置、姿态或接触力以获得诊断超声影像。",
         "仅做图像分割/分类、针路或治疗导航而未主动扫查；弹性成像归 R2；取样归 S 类。"),
    Task("A2", "A", "Active observational sensing", "主动观察式检测",
         "Robotic endoscopic search / navigation", "机器人内镜搜索/导航",
         ("robotic endoscopy", "robotic endoscope", "robot-assisted endoscopy",
          "autonomous endoscopy", "endoscopic robot", "robotic capsule endoscopy",
          "magnetic capsule endoscopy", "robotic colonoscopy", "autonomous colonoscopy",
          "robotic bronchoscopy", "robot-assisted bronchoscopy"),
         r"endoscop\w*|colonoscop\w*|bronchoscop\w*|capsule",
         "机器人/磁驱内镜主动改变视角、位置或路径以检查腔道和搜索病灶。",
         "纯治疗性内镜操作；带活检/针吸的主要终点归 S3/S6。"),
    Task("A3", "A", "Active observational sensing", "主动观察式检测",
         "Robotic OCT / ophthalmic imaging", "机器人 OCT/眼科成像",
         ("robotic optical coherence tomography", "robot-assisted optical coherence tomography",
          "robotic OCT", "autonomous OCT", "robotic retinal imaging",
          "robotic fundus imaging", "robotic ophthalmic imaging"),
         r"optical coherence tomography|\bOCT\b|retin\w* imag\w*|fundus imag\w*|ophthalm\w* imag\w*",
         "机器人定位 OCT、眼底或其他眼科成像传感器并主动获取诊断影像。",
         "仅做图像算法或机器人眼科治疗而无主动成像。"),
    Task("A4", "A", "Active observational sensing", "主动观察式检测",
         "Robotic dermoscopy / skin scanning", "机器人皮肤镜/全身皮肤扫描",
         ("robotic dermoscopy", "robot-assisted dermoscopy", "robotic skin imaging",
          "autonomous skin imaging", "robotic total body photography",
          "skin scanning robot", "robotic skin examination"),
         r"dermoscop\w*|skin imag\w*|skin scan\w*|total.body photograph\w*|skin examination",
         "机器人主动巡视皮肤表面、调整相机/皮肤镜位姿并采集病灶影像。",
         "固定相机皮肤分类器、纯图像诊断模型。"),
    Task("A5", "A", "Active observational sensing", "主动观察式检测",
         "Robotic auscultation", "机器人听诊",
         ("robotic auscultation", "robot-assisted auscultation", "autonomous auscultation",
          "robotic stethoscope", "robotic heart sound", "robotic lung sound"),
         r"auscultat\w*|stethoscop\w*|heart sound\w*|lung sound\w*",
         "机器人在多个解剖位置放置听诊器并采集心肺声音。",
         "固定电子听诊器和仅做声音分类的算法。"),
    Task("A6", "A", "Active observational sensing", "主动观察式检测",
         "Robotic otoscopy / oral-ENT examination", "机器人耳镜/口腔/耳鼻喉检查",
         ("robotic otoscopy", "robotic otoscope", "robot-assisted otoscopy",
          "autonomous otoscopy", "robotic oral examination", "robotic throat examination",
          "robotic ear examination", "robotic dental examination", "robotic intraoral imaging"),
         r"otoscop\w*|oral examination|throat examination|ear examination|dental examination|intraoral imag\w*",
         "机器人主动定位耳镜或口腔/咽喉相机以获得检查影像。",
         "牙科加工、手术或固定式口内扫描而无机器人主动定位。"),
    Task("A7", "A", "Active observational sensing", "主动观察式检测",
         "Robotic optical / spectral / thermal scanning", "机器人光谱/热成像/表面扫描",
         ("robotic hyperspectral imaging", "robot-assisted hyperspectral imaging",
          "robotic thermography", "robotic thermal imaging", "robotic terahertz imaging",
          "robotic Raman spectroscopy", "robotic fluorescence imaging",
          "robotic photoacoustic imaging"),
         r"hyperspectral|thermograph\w*|thermal imag\w*|terahertz|Raman|fluorescen\w* imag\w*|photoacoustic imag\w*",
         "机器人主动移动光谱、热、太赫兹、荧光或光声传感器扫描人体/组织。",
         "工业检测；主要用于切除/消融而非诊断取证。"),

    Task("R1", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic palpation / tactile stiffness mapping", "机器人触诊/触觉硬度映射",
         ("robotic palpation", "robot-assisted palpation", "autonomous palpation",
          "robot palpation", "tactile palpation robot", "robotic tactile examination"),
         r"palpat\w*|tactile examination|tactile stiff\w*",
         "机器人施加受控接触/压入并由力、位移或触觉响应定位硬结或边界。",
         "仅抓取/操作组织而不以诊断为终点。"),
    Task("R2", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic elastography / compression imaging", "机器人弹性检测/压缩成像",
         ("robotic elastography", "robot-assisted elastography", "robotic ultrasound elastography",
          "robotic compression ultrasound", "robotic tissue stiffness mapping"),
         r"elastograph\w*|compression ultrasound|tissue stiff\w* map\w*",
         "机器人施加可控压缩、振动或剪切波激励并测得组织弹性响应。",
         "无机器人施力/定位的常规弹性成像。"),
    Task("R3", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic joint provocative / laxity examination", "机器人关节激发/松弛度检查",
         ("robotic joint examination", "robotic knee examination", "robotic shoulder examination",
          "robotic ankle examination", "robotic laxity testing", "robotic arthrometer",
          "robot-assisted joint assessment"),
         r"joint examination|knee examination|shoulder examination|ankle examination|laxity test\w*|arthromet\w*|joint assessment",
         "机器人施加标准化关节载荷/运动，测量松弛度、活动度或疼痛/功能响应。",
         "康复训练、手术导航、假体测试而无诊断检查终点。"),
    Task("R4", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic diagnostic percussion", "机器人诊断性叩诊",
         ("robotic diagnostic percussion", "robot-assisted percussion examination",
          "automated percussion examination", "robotic chest percussion diagnosis"),
         r"percussion",
         "机器人执行可重复叩击并分析声学/机械响应用于体格检查。",
         "排痰、胸部物理治疗或康复性叩击。"),
    Task("R5", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic deep-tendon reflex examination", "机器人腱反射检查",
         ("robotic reflex testing", "robotic tendon reflex", "automated tendon reflex",
          "robot-assisted reflex examination", "robotic patellar reflex"),
         r"reflex test\w*|tendon reflex|reflex examination|patellar reflex",
         "机器人施加标准化叩击并测量肢体、肌电或运动学反射。",
         "康复反射训练或非诊断性控制实验。"),
    Task("R6", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robot-guided TMS / motor-response mapping", "机器人引导 TMS/运动反应映射",
         ("robotic transcranial magnetic stimulation", "robot-assisted transcranial magnetic stimulation",
          "robot-guided transcranial magnetic stimulation", "robotic TMS", "robot-assisted TMS"),
         r"transcranial magnetic stimulation|\bTMS\b",
         "机器人定位刺激线圈，通过 MEP/功能响应做皮层定位、评估或诊断映射。",
         "仅以治疗疗效为终点且未测量诊断/功能映射响应。"),
    Task("R7", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic nerve-conduction / electrical response testing", "机器人神经传导/电刺激—响应检测",
         ("robotic nerve conduction", "robot-assisted nerve conduction",
          "automated nerve conduction study", "robotic electrical stimulation response",
          "robotic neuromuscular assessment"),
         r"nerve conduction|electrical stimulation response|neuromuscular assessment",
         "机器人定位刺激/记录电极并测量神经或肌肉的诱发响应。",
         "治疗性电刺激、康复或假肢控制而无诊断测量。"),
    Task("R8", "R", "Response-based interactive diagnosis", "响应式交互检测",
         "Robotic tonometry / indentation testing", "机器人眼压/压入式检测",
         ("robotic tonometry", "robot-assisted tonometry", "robotic indentation test",
          "robotic corneal indentation", "autonomous tonometry"),
         r"tonometr\w*|indentation test\w*|corneal indentation",
         "机器人施加标准化接触或气动/机械载荷并测量眼压或组织变形。",
         "固定式商用眼压计或材料测试。"),

    Task("S1", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic venipuncture / phlebotomy", "机器人静脉穿刺/采血",
         ("robotic venipuncture", "robot-assisted venipuncture", "autonomous venipuncture",
          "robotic phlebotomy", "robotic blood draw", "venipuncture robot"),
         r"venipuncture|phlebotom\w*|blood draw",
         "机器人定位静脉、穿刺并取得血液样本。",
         "仅静脉显像、输液/置管而无采血终点。"),
    Task("S2", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic swab collection", "机器人拭子采样",
         ("robotic swab", "robot-assisted swab", "autonomous swab collection",
          "robotic nasopharyngeal swab", "robotic oropharyngeal swab", "swabbing robot"),
         r"swab\w*",
         "机器人执行鼻咽、口咽或其他表面拭子采样。",
         "清洁/消毒机器人或实验室移液拭子。"),
    Task("S3", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic bronchoscopy biopsy / TBNA", "机器人支气管镜活检/TBNA",
         ("robotic bronchoscopy biopsy", "robotic-assisted bronchoscopy biopsy",
          "robotic bronchoscopic biopsy", "robotic transbronchial biopsy",
          "robotic bronchoscopy needle aspiration", "robotic bronchoscopy sampling",
          "robotic-assisted bronchoscopy tissue acquisition"),
         r"bronchoscop\w*|transbronchial|TBNA",
         "机器人支气管镜导航至肺病灶并执行活检、刷检或针吸取样。",
         "仅导航/观察而未取样归 A2。"),
    Task("S4", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic prostate biopsy", "机器人前列腺活检",
         ("robotic prostate biopsy", "robot-assisted prostate biopsy",
          "robotic transperineal biopsy", "robotic transrectal biopsy"),
         r"prostat\w*|transperineal|transrectal",
         "机器人规划并执行经会阴/经直肠前列腺组织取样。",
         "前列腺治疗或仅影像融合而未执行取样。"),
    Task("S5", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic percutaneous core-needle biopsy", "机器人经皮粗针活检",
         ("robotic needle biopsy", "robot-assisted needle biopsy", "robotic percutaneous biopsy",
          "robotic breast biopsy", "robotic liver biopsy", "robotic lung biopsy",
          "robotic kidney biopsy", "robotic core needle biopsy"),
         r"biops\w*|core needle",
         "机器人在影像引导下执行肺、肝、乳腺、肾等经皮粗针组织取样。",
         "支气管镜、前列腺、胃肠内镜和骨髓活检分别归 S3/S4/S6/S9。"),
    Task("S6", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic GI endoscopic biopsy", "机器人胃肠内镜活检",
         ("robotic endoscopic biopsy", "robot-assisted endoscopic biopsy",
          "robotic gastrointestinal biopsy", "robotic colon biopsy", "robotic gastric biopsy"),
         r"endoscop\w*|gastrointestinal|gastric|colon",
         "机器人胃肠内镜定位病灶并夹取/切取组织。",
         "仅视觉搜索/导航而无取样归 A2。"),
    Task("S7", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic fine-needle aspiration", "机器人细针抽吸",
         ("robotic fine needle aspiration", "robot-assisted fine needle aspiration",
          "robotic FNA", "robotic aspiration biopsy"),
         r"fine needle aspiration|\bFNA\b|aspiration biopsy",
         "机器人执行细针抽吸并取得细胞学样本。",
         "支气管镜 TBNA 归 S3；纯治疗性抽吸/引流。"),
    Task("S8", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic lumbar puncture / CSF collection", "机器人腰椎穿刺/脑脊液采集",
         ("robotic lumbar puncture", "robot-assisted lumbar puncture",
          "autonomous lumbar puncture", "robotic cerebrospinal fluid collection"),
         r"lumbar puncture|cerebrospinal fluid|\bCSF\b",
         "机器人定位椎间隙、穿刺并取得脑脊液样本。",
         "硬膜外麻醉或药物注射而无采样。"),
    Task("S9", "S", "Sample-based interactive diagnosis", "采样式交互检测",
         "Robotic bone-marrow / body-fluid sampling", "机器人骨髓/体液穿刺采样",
         ("robotic bone marrow biopsy", "robot-assisted bone marrow biopsy",
          "robotic bone marrow aspiration", "robotic joint aspiration",
          "robotic pleural aspiration", "robotic diagnostic paracentesis"),
         r"bone marrow|joint aspiration|pleural aspiration|paracentesis",
         "机器人执行骨髓活检/抽吸或关节、胸腹腔液体的诊断性采样。",
         "以治疗引流为唯一终点的操作。"),
)


TASK_BY_CODE = {task.code: task for task in TASKS}
CLASS_ORDER = {"S": 0, "R": 1, "A": 2}
BROAD_QUERIES: dict[str, tuple[str, ...]] = {
    "A4": ("robot dermoscopy", "robot skin examination", "robot total body photography"),
    "A6": ("robot otoscopy", "robot otoscope", "robot oral examination", "robot intraoral imaging", "robot ear examination"),
    "R2": ("robot elastography", "robot tissue stiffness mapping", "robot compression ultrasound"),
    "R3": ("robot joint laxity", "robot arthrometer", "robot joint examination"),
    "R4": ("robot diagnostic percussion", "robot percussion examination", "robot acoustic percussion"),
    "R5": ("robot tendon reflex", "robot patellar reflex", "robot reflex examination"),
    "R7": ("robot nerve conduction", "robot electrical stimulation response", "robot neuromuscular assessment"),
    "R8": ("robot tonometry", "robot corneal indentation"),
}
STRICT_TITLE_CODES = {"A4", "A6", "R2", "R3", "R5", "R7", "R8", "S4", "S5", "S6", "S7", "S9"}
REVIEW_RE = re.compile(
    r"\b(systematic|scoping|narrative|integrative|literature|comprehensive|state[- ]of[- ]the[- ]art|current) review\b|"
    r"\bmeta[- ]analysis\b|\bbibliometric\b|\ba review of\b|\breview and future\b|"
    r"\bconsensus\b|\brecommendations?\b|\bposition statement\b|\bannual progress\b|"
    r"\bperspective\b|\bcommentary\b|\beditorial\b|\bletter to the editor\b|\breferee report\b|"
    r"\bresearch progress\b|\brecent advances\b|\bprospects of\b|\bfuture of\b|"
    r"\bcurrent evidence\b|\bwhat is the evidence\b|\bclinical applications and future\b|"
    r"\btechnology[- ]driven roadmapping\b|\ba call for\b|\ba review\b|\breview of\b|"
    r"\breview on\b|\bdata review\b|\bupdated review\b|\bannual review\b|\boverview\b|"
    r"\bstate[- ]of[- ]the[- ]art\b|\bfuture directions\b|\bfuture prospects\b|\bfuture perspectives\b|\bcurrent trends\b|"
    r"^\s*review\s*:|\bclinical practice review\b|"
    r"\breflection on\b|\bglimpse to the future\b|\bapplication and development of\b|^\s*Re:\s",
    re.I,
)
EMBODIED_RE = re.compile(
    r"\brobot\w*\b|\btelerobot\w*\b|\bautonomous\s+(?:system|device|platform|robot|scanner|probe|endoscop\w*)\b|"
    r"\bmagnetic(?:ally)?[- ](?:controlled|actuated|guided)\b",
    re.I,
)
TITLE_EMBODIED_RE = re.compile(
    r"\brobot\w*\b|\btelerobot\w*\b|\bautonom\w*\b|\bmagnetic(?:ally)?[- ](?:controlled|actuated|guided)?\s*capsule\b|"
    r"\bmagnetic capsule\b",
    re.I,
)
CLINICAL_RE = re.compile(
    r"patient|human|clinical|medical|surg\w*|diagnos\w*|screen\w*|examin\w*|tissue|organ|"
    r"cancer|tumou?r|lesion|biops\w*|blood|lung|liver|breast|prostate|brain|skin|eye|cornea|"
    r"endoscop\w*|ultrasound|palpat\w*|stethoscop\w*|venipuncture|swab\w*",
    re.I,
)
SAMPLE_ACTION_RE = re.compile(
    r"biops\w*|tissue acquisition|tissue sampl\w*|needle aspiration|fine needle aspiration|\bFNA\b|"
    r"\bTBNA\b|transbronchial|venipuncture|phlebotom\w*|blood draw|swab\w*|lumbar puncture|"
    r"cerebrospinal fluid|bone marrow aspiration|joint aspiration|pleural aspiration|paracentesis",
    re.I,
)
DIAGNOSTIC_ENDOSCOPY_RE = re.compile(
    r"capsule|colonoscop\w*|bronchoscop\w*|diagnos\w*|screen\w*|detect\w*|inspect\w*|examin\w*|"
    r"imag\w*|navigation|locali[sz]\w*|lesion|polyp|mapping|visuali[sz]\w*|reconnaissance",
    re.I,
)
TMS_MAPPING_RE = re.compile(
    r"motor evoked|\bMEP\b|map\w*|locali[sz]\w*|assessment|diagnos\w*|measure\w*|response|"
    r"functional|cortical|motor threshold|navigat\w*",
    re.I,
)
PERCUSSION_DIAG_RE = re.compile(r"diagnos\w*|examin\w*|assess\w*|acoustic|sound|detect\w*|measure\w*", re.I)
INDUSTRIAL_RE = re.compile(
    r"weld|(?:oil|gas) pipeline|pipeline inspection|crop|fruit|agricultur|manufactur|composite|concrete|bridge|road|building|"
    r"battery|photovoltaic|aerospace|industrial inspection|food quality|mineral|salmon|fish fillet|"
    r"art restoration|cultural heritage|archaeolog|anthropolog|storage device|hard-to-reach industrial|"
    r"inner wall defects?|non[- ]destructive testing.*production|corrosion defect",
    re.I,
)
A2_DIAG_RE = re.compile(
    r"diagnos\w*|screen\w*|detect\w*|inspect\w*|examin\w*|visuali[sz]\w*|lesion|polyp|nodule|"
    r"diagnostic yield|accuracy|reconnaissance|search|mapping",
    re.I,
)
A2_STRONG_DIAG_RE = re.compile(
    r"diagnos\w*|screen\w*|detect\w*|inspect\w*|examin\w*|visuali[sz]\w*|diagnostic yield|"
    r"diagnostic accuracy|reconnaissance|lesion search|polyp detection",
    re.I,
)
A2_NONDIGNOSTIC_TITLE_RE = re.compile(
    r"relative pose estimation.*remote center of motion|"
    r"autonomous endoscope robot positioning using instrument segmentation|"
    r"pose tracking.*suture needle.*robotic endoscope|"
    r"enhanced distance perception.*robotic endoscopy",
    re.I,
)
THERAPY_RE = re.compile(
    r"resection|surg\w*|ablat\w*|suturing|closure|dissection|repair|enucleation|nephrectom\w*|"
    r"gastrectom\w*|colectom\w*|prostatectom\w*|hepatectom\w*|laser|treatment|therapy|marking|"
    r"fiducial|dye locali[sz]\w*|cerclage|drilling",
    re.I,
)


def normalize_title(title: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", title or "")
    if len(cleaned) > 80:
        cleaned = re.sub(r"\s*\([^)]{1,60}\)\s*$", "", cleaned)
    text = unicodedata.normalize("NFKD", cleaned).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def reconstruct_abstract(inv: dict[str, list[int]] | None) -> str:
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, locs in inv.items():
        positions.extend((int(pos), word) for pos in locs)
    positions.sort()
    return " ".join(word for _, word in positions)


def fetch_json(url: str, attempts: int = 8) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if attempt == attempts - 1:
                raise
            retry_after = int(exc.headers.get("Retry-After", "0") or 0) if exc.code == 429 else 0
            time.sleep(max(retry_after, min(2 ** attempt, 30)))
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError("unreachable")


def fetch_xml(url: str, attempts: int = 8) -> ET.Element:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return ET.fromstring(response.read())
        except urllib.error.HTTPError as exc:
            if attempt == attempts - 1:
                raise
            retry_after = int(exc.headers.get("Retry-After", "0") or 0) if exc.code in {429, 503} else 0
            time.sleep(max(retry_after, min(3 * (2 ** attempt), 45)))
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(min(3 * (2 ** attempt), 30))
    raise RuntimeError("unreachable")


def phrase_query(phrases: Iterable[str]) -> str:
    return " OR ".join(f'"{p}"' for p in phrases)


def openalex_url(task: Task, cursor: str, search_text: str | None = None) -> str:
    filters = ",".join((
        f"title_and_abstract.search:{search_text or phrase_query(task.phrases)}",
        f"from_publication_date:{START_DATE}",
        f"to_publication_date:{CUTOFF}",
        "type:article|preprint|report|dissertation",
    ))
    params = urllib.parse.urlencode({
        "filter": filters,
        "per-page": 200,
        "cursor": cursor,
    })
    return f"https://api.openalex.org/works?{params}"


def europepmc_url(task: Task, cursor: str) -> str:
    q = " OR ".join(f'TITLE_ABS:"{p}"' for p in task.phrases)
    q = f"({q}) AND FIRST_PDATE:[{START_DATE[:4]} TO {CUTOFF[:4]}]"
    params = urllib.parse.urlencode({
        "query": q,
        "format": "json",
        "resultType": "core",
        "pageSize": 1000,
        "cursorMark": cursor,
    })
    return f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}"


def arxiv_query(task: Task) -> str:
    phrases = list(dict.fromkeys((*task.phrases, *BROAD_QUERIES.get(task.code, ()))))
    phrase_blocks = [f'(ti:"{phrase}" OR abs:"{phrase}")' for phrase in phrases]
    cutoff_stamp = CUTOFF.replace("-", "") + "2359"
    start_stamp = START_DATE.replace("-", "") + "0000"
    return f"({' OR '.join(phrase_blocks)}) AND submittedDate:[{start_stamp} TO {cutoff_stamp}]"


def arxiv_url(query: str, start: int, max_results: int = 2000) -> str:
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    return f"https://export.arxiv.org/api/query?{params}"


def collect_openalex(task: Task, cache_dir: Path, refresh: bool) -> tuple[list[dict[str, Any]], int, str]:
    cache_name = f"openalex_v2_{task.code}.json" if task.code in BROAD_QUERIES else f"openalex_{task.code}.json"
    cache_file = cache_dir / cache_name
    search_blocks = (phrase_query(task.phrases),) + BROAD_QUERIES.get(task.code, ())
    query_text = " || ".join(search_blocks)
    if cache_file.exists() and not refresh:
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
        return payload["records"], payload["hit_count"], query_text

    by_id: dict[str, dict[str, Any]] = {}
    hit_count = 0
    block_counts: list[dict[str, Any]] = []
    for search_text in search_blocks:
        cursor = "*"
        block_count = 0
        block_retrieved = 0
        while cursor:
            data = fetch_json(openalex_url(task, cursor, search_text))
            block_count = int(data.get("meta", {}).get("count", 0))
            page = data.get("results", [])
            block_retrieved += len(page)
            for record in page:
                record_key = record.get("id") or hashlib.sha1(json.dumps(record, sort_keys=True).encode()).hexdigest()
                by_id[record_key] = record
            next_cursor = data.get("meta", {}).get("next_cursor")
            if not next_cursor or not page:
                break
            cursor = next_cursor
            time.sleep(0.12)
        hit_count += block_count
        block_counts.append({"search": search_text, "hit_count": block_count, "retrieved": block_retrieved})
    records = list(by_id.values())
    payload = {"task": task.code, "query": query_text, "hit_count": hit_count, "query_blocks": block_counts, "records": records}
    cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return records, hit_count, query_text


def collect_europepmc(task: Task, cache_dir: Path, refresh: bool) -> tuple[list[dict[str, Any]], int, str]:
    cache_file = cache_dir / f"europepmc_{task.code}.json"
    query_text = " OR ".join(f'TITLE_ABS:"{p}"' for p in task.phrases)
    if cache_file.exists() and not refresh:
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
        return payload["records"], payload["hit_count"], query_text

    records: list[dict[str, Any]] = []
    cursor = "*"
    hit_count = 0
    while cursor:
        data = fetch_json(europepmc_url(task, cursor))
        hit_count = int(data.get("hitCount", 0))
        page = data.get("resultList", {}).get("result", [])
        records.extend(page)
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or not page or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.12)
    payload = {"task": task.code, "query": query_text, "hit_count": hit_count, "records": records}
    cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return records, hit_count, query_text


def collect_arxiv(task: Task, cache_dir: Path, refresh: bool) -> tuple[list[dict[str, Any]], int, str]:
    """Retrieve title/abstract phrase matches from arXiv serially."""
    cache_file = cache_dir / f"arxiv_{task.code}.json"
    query_text = arxiv_query(task)
    if cache_file.exists() and not refresh:
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
        return payload["records"], payload["hit_count"], query_text

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "open": "http://a9.com/-/spec/opensearch/1.1/",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    records: list[dict[str, Any]] = []
    start = 0
    hit_count = 0
    while True:
        if start > 0:
            time.sleep(3.1)
        root = fetch_xml(arxiv_url(query_text, start=start, max_results=2000))
        hit_count = int(root.findtext("open:totalResults", default="0", namespaces=ns) or 0)
        entries = root.findall("atom:entry", ns)
        for entry in entries:
            entry_id = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
            arxiv_id = entry_id.rsplit("/", 1)[-1]
            records.append({
                "id": arxiv_id,
                "entry_id": entry_id,
                "title": re.sub(r"\s+", " ", entry.findtext("atom:title", default="", namespaces=ns) or "").strip(),
                "summary": re.sub(r"\s+", " ", entry.findtext("atom:summary", default="", namespaces=ns) or "").strip(),
                "published": (entry.findtext("atom:published", default="", namespaces=ns) or "").strip(),
                "updated": (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip(),
                "doi": (entry.findtext("arxiv:doi", default="", namespaces=ns) or "").strip().lower(),
                "journal_ref": (entry.findtext("arxiv:journal_ref", default="", namespaces=ns) or "").strip(),
                "categories": [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ns)],
                "authors": [
                    (author.findtext("atom:name", default="", namespaces=ns) or "").strip()
                    for author in entry.findall("atom:author", ns)
                ],
            })
        start += len(entries)
        if not entries or start >= hit_count:
            break

    payload = {"task": task.code, "query": query_text, "hit_count": hit_count, "records": records}
    cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return records, hit_count, query_text


def openalex_to_record(raw: dict[str, Any], query_task: str) -> dict[str, Any]:
    source = (((raw.get("primary_location") or {}).get("source") or {}).get("display_name")) or ""
    return {
        "source_db": "OpenAlex",
        "source_id": (raw.get("id") or "").rsplit("/", 1)[-1],
        "doi": (raw.get("doi") or "").replace("https://doi.org/", "").lower(),
        "pmid": "",
        "title": raw.get("display_name") or raw.get("title") or "",
        "abstract": reconstruct_abstract(raw.get("abstract_inverted_index")),
        "year": raw.get("publication_year") or "",
        "publication_date": raw.get("publication_date") or "",
        "work_type": raw.get("type") or "",
        "venue": source,
        "cited_by_count": raw.get("cited_by_count") or 0,
        "url": raw.get("doi") or raw.get("id") or "",
        "query_tasks": {query_task},
    }


def europepmc_to_record(raw: dict[str, Any], query_task: str) -> dict[str, Any]:
    first_date = raw.get("firstPublicationDate") or ""
    year = raw.get("pubYear") or (first_date[:4] if first_date else "")
    source = raw.get("journalTitle") or raw.get("journalInfo", {}).get("journal", {}).get("title") or ""
    doi = (raw.get("doi") or "").lower()
    pmid = str(raw.get("pmid") or "")
    url = f"https://doi.org/{doi}" if doi else (f"https://europepmc.org/article/MED/{pmid}" if pmid else "")
    return {
        "source_db": "Europe PMC",
        "source_id": f"{raw.get('source', '')}:{raw.get('id', '')}",
        "doi": doi,
        "pmid": pmid,
        "title": raw.get("title") or "",
        "abstract": raw.get("abstractText") or "",
        "year": int(year) if str(year).isdigit() else "",
        "publication_date": first_date,
        "work_type": raw.get("pubType") or "",
        "venue": source,
        "cited_by_count": raw.get("citedByCount") or 0,
        "url": url,
        "query_tasks": {query_task},
    }


def arxiv_to_record(raw: dict[str, Any], query_task: str) -> dict[str, Any]:
    published = raw.get("published") or ""
    year = int(published[:4]) if len(published) >= 4 and published[:4].isdigit() else ""
    doi = (raw.get("doi") or "").lower()
    categories = raw.get("categories") or []
    return {
        "source_db": "arXiv",
        "source_id": raw.get("id") or "",
        "doi": doi,
        "pmid": "",
        "title": raw.get("title") or "",
        "abstract": raw.get("summary") or "",
        "year": year,
        "publication_date": published[:10],
        "work_type": "preprint",
        "venue": "arXiv" + ((" [" + ", ".join(categories) + "]") if categories else ""),
        "cited_by_count": 0,
        "url": raw.get("entry_id") or (f"https://arxiv.org/abs/{raw.get('id')}" if raw.get("id") else ""),
        "query_tasks": {query_task},
    }


def merge_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}

    def absorb(cur: dict[str, Any], rec: dict[str, Any]) -> None:
        cur["query_tasks"].update(rec["query_tasks"])
        cur["source_dbs"].add(rec["source_db"])
        cur["source_ids"].add(rec["source_id"])
        if len(rec.get("abstract", "")) > len(cur.get("abstract", "")):
            cur["abstract"] = rec["abstract"]
        # A journal article and its preprint are one work; use the earliest
        # known public date for annual trajectory analyses.
        cur_date = str(cur.get("publication_date") or "")
        rec_date = str(rec.get("publication_date") or "")
        rec_is_arxiv = rec.get("source_db") == "arXiv"
        cur_year = int(cur_date[:4]) if len(cur_date) >= 4 and cur_date[:4].isdigit() else None
        rec_year = int(rec_date[:4]) if len(rec_date) >= 4 and rec_date[:4].isdigit() else None
        plausible_preprint_lead = bool(
            rec_is_arxiv and cur_year is not None and rec_year is not None and 0 <= cur_year - rec_year <= 10
        )
        if rec_date and (not cur_date or (rec_date < cur_date and plausible_preprint_lead)):
            cur["publication_date"] = rec_date
            if len(rec_date) >= 4 and rec_date[:4].isdigit():
                cur["year"] = int(rec_date[:4])
        elif not cur.get("year") and rec.get("year"):
            cur["year"] = rec["year"]
        for field in ("doi", "pmid", "venue", "url"):
            if not cur.get(field) and rec.get(field):
                cur[field] = rec[field]
        cur["cited_by_count"] = max(int(cur.get("cited_by_count") or 0), int(rec.get("cited_by_count") or 0))

    for rec in records:
        norm_title = normalize_title(rec["title"])
        if len(norm_title) >= 16:
            key = f"title:{norm_title}"
        elif rec["doi"]:
            key = f"doi:{rec['doi']}"
        else:
            key = f"source:{rec['source_db']}:{rec['source_id']}"
        if key not in by_key:
            by_key[key] = rec.copy()
            by_key[key]["source_dbs"] = {rec["source_db"]}
            by_key[key]["source_ids"] = {rec["source_id"]}
        else:
            absorb(by_key[key], rec)

    # Second pass: merge DOI-identical records whose titles differ by subtitle or punctuation.
    by_doi: dict[str, dict[str, Any]] = {}
    output: list[dict[str, Any]] = []
    for rec in by_key.values():
        doi = rec.get("doi", "")
        if doi and doi in by_doi:
            absorb(by_doi[doi], rec)
        else:
            output.append(rec)
            if doi:
                by_doi[doi] = rec
    return output


def score_task(task: Task, text: str, query_tasks: set[str]) -> int:
    score = 0
    if task.code in query_tasks:
        score += 4
    if re.search(task.task_pattern, text, re.I):
        score += 5
    phrase_matches = sum(1 for phrase in task.phrases if phrase.lower() in text.lower())
    score += min(phrase_matches, 3) * 2
    return score


def eligible(task: Task, text: str, title: str, query_tasks: set[str]) -> bool:
    if not EMBODIED_RE.search(text) or not re.search(task.task_pattern, text, re.I):
        return False
    if task.code in STRICT_TITLE_CODES and (
        not TITLE_EMBODIED_RE.search(title) or not re.search(task.task_pattern, title, re.I)
    ):
        return False
    # Cross-task reassignment is allowed only when the target action is explicit in the title.
    if task.code not in query_tasks and not re.search(task.task_pattern, title, re.I):
        return False
    if task.code == "A2":
        if INDUSTRIAL_RE.search(text):
            return False
        if A2_NONDIGNOSTIC_TITLE_RE.search(title):
            return False
        title_has_diag = bool(A2_DIAG_RE.search(title))
        title_is_capsule = bool(re.search(r"capsule endoscop\w*|capsule robot", title, re.I))
        title_is_colonoscopy = bool(re.search(r"colonoscop\w*", title, re.I))
        if THERAPY_RE.search(title) and not A2_STRONG_DIAG_RE.search(title):
            return False
        return bool(DIAGNOSTIC_ENDOSCOPY_RE.search(text)) and (title_has_diag or title_is_capsule or title_is_colonoscopy or not THERAPY_RE.search(title))
    if task.code == "A3":
        return not bool(INDUSTRIAL_RE.search(text) or re.search(r"fingermark|forensic", text, re.I))
    if task.code == "A4":
        return bool(CLINICAL_RE.search(text)) and not bool(re.search(r"electronic skin|e-skin|robot skin|tactile skin|artificial skin|skin-like", text, re.I))
    if task.code == "A6":
        return bool(CLINICAL_RE.search(text)) and not bool(INDUSTRIAL_RE.search(text))
    if task.code == "A7":
        return bool(CLINICAL_RE.search(text)) and not bool(INDUSTRIAL_RE.search(text))
    if task.code == "R3":
        return not bool(re.search(r"rehabilitat\w*|training|prosthe\w*|arthroplast\w*|surgical navigation", text, re.I))
    if task.code == "R2":
        return not bool(re.search(r"robot-assisted partial nephrectom|robotic partial nephrectom", title, re.I))
    if task.code == "R4":
        return bool(re.search(r"percussion", title, re.I)) and bool(re.search(r"robot\w*|telemedical", title, re.I)) and bool(PERCUSSION_DIAG_RE.search(text)) and not bool(re.search(r"therap\w*|physiotherap\w*|airway clearance|secretion|bolt|pipeline|music|opera", text, re.I))
    if task.code == "R6":
        return bool(TMS_MAPPING_RE.search(text))
    if task.code == "R7":
        return not bool(re.search(r"prosthe\w*|rehabilitat\w*|functional electrical stimulation|therapy", text, re.I))
    if task.code == "R8":
        return bool(CLINICAL_RE.search(text)) and not bool(INDUSTRIAL_RE.search(text))
    if task.code == "S1":
        return task.code in query_tasks and bool(re.search(r"blood|sample|draw|collect|phlebotom|venipuncture", text, re.I))
    if task.code == "S2":
        return task.code in query_tasks and bool(re.search(r"nasopharyn|oropharyn|sample|collect|specimen|COVID|SARS", text, re.I)) and not bool(re.search(r"clean\w*|disinfect\w*|floor|food contact|hygiene monitor", text, re.I))
    if task.code == "S3":
        if re.search(r"ablat\w*|resection|dye marking|fiducial placement", title, re.I) and not re.search(r"biops\w*|sampl\w*|diagnostic yield|tissue acquisition", title, re.I):
            return False
        return bool(re.search(r"biops\w*|tissue acquisition|sampl\w*|needle aspiration|\bTBNA\b|transbronchial|diagnostic yield", text, re.I))
    if task.code == "S4":
        return bool(re.search(r"robot\w*", title, re.I)) and bool(re.search(r"prostat\w*", title, re.I)) and bool(re.search(r"biops\w*|tissue sampl\w*", title, re.I))
    if task.code == "S5":
        return (task.code in query_tasks or bool(re.search(r"robot\w*.*(?:needle|percutaneous|breast|liver|lung|kidney).*biops|biops\w*.*robot\w*", title, re.I))) and bool(re.search(r"biops\w*|tissue sampl\w*|core needle", text, re.I))
    if task.code == "S6":
        return (task.code in query_tasks or bool(re.search(r"robot\w*.*endoscop\w*.*biops|endoscop\w*.*robot\w*.*biops", title, re.I))) and bool(re.search(r"biops\w*|tissue sampl\w*|specimen", text, re.I))
    if task.code == "S7":
        return task.code in query_tasks and bool(re.search(r"aspirat\w*|cytolog\w*|sample", text, re.I))
    if task.code == "S8":
        return task.code in query_tasks and bool(re.search(r"collect\w*|sampl\w*|cerebrospinal|\bCSF\b", text, re.I)) and not bool(re.search(r"epidural|anesth\w*|inject\w*", text, re.I))
    if task.code == "S9":
        return task.code in query_tasks and bool(re.search(r"biops\w*|aspirat\w*|sampl\w*|diagnos\w*", text, re.I))
    return True


def is_core_title(task: Task, title: str) -> bool:
    """High-precision tier: embodiment and concrete task are both explicit in title."""
    if task.code == "A1":
        if re.search(r"ultrasound[- ]guided.*robot\w*.*(?:surg|resection|ablation|biopsy|cerclage|drilling|nephrectom)", title, re.I):
            return False
        return bool(re.search(
            r"(?:robot(?:ic|ized|ised|ically)?(?:[-–— ]+(?:arm|system|platform|probe|scanner|assisted|enabled|controlled|guided))*[-–— ]+(?:ultrasound|ultrasonograph\w*|sonograph\w*))|"
            r"(?:telerobot\w*|autonom\w*).{0,35}(?:ultrasound|ultrasonograph\w*|sonograph\w*)|"
            r"(?:ultrasound|ultrasonograph\w*|sonograph\w*).{0,35}robot(?:ic)?[-–— ]+(?:arm|system|platform|probe|scanner)",
            title, re.I,
        ))
    if task.code == "A2":
        if not (TITLE_EMBODIED_RE.search(title) and re.search(task.task_pattern, title, re.I)):
            return False
        if INDUSTRIAL_RE.search(title) or (THERAPY_RE.search(title) and not A2_STRONG_DIAG_RE.search(title)):
            return False
        return bool(A2_DIAG_RE.search(title) or re.search(r"capsule endoscop\w*|capsule robot|colonoscop\w*", title, re.I))
    if task.code == "A3":
        if INDUSTRIAL_RE.search(title) or re.search(r"fingermark|forensic|needle insertion|microsutur\w*|dissection", title, re.I):
            return False
        return bool(re.search(
            r"robot(?:ic|ically)?(?:[-–— ]+(?:arm|assisted|scanner|system))*[-–— ]+(?:OCT|optical coherence tomography)|"
            r"(?:OCT|optical coherence tomography).{0,30}robot(?:ic)?[-–— ]+(?:scanner|system|arm|imaging)",
            title, re.I,
        ))
    if task.code == "R2":
        if re.search(r"partial nephrectom|comparison.*with a robotic measurement", title, re.I):
            return False
        return bool(re.search(
            r"robot(?:ic|ically)?(?:[-–— ]+(?:arm|assisted|controlled|system))*[-–— ]+(?:ultrasound )?(?:elastograph\w*|compressional elastograph\w*)|"
            r"elastograph\w*.{0,40}(?:positioning robot|robotic arm|robotic control|robotic system)",
            title, re.I,
        ))
    if task.code == "R4":
        return bool(re.search(r"percussion", title, re.I) and re.search(r"robot\w*|telemedical", title, re.I))
    return bool(TITLE_EMBODIED_RE.search(title) and re.search(task.task_pattern, title, re.I))


def classify_record(rec: dict[str, Any]) -> dict[str, Any]:
    title = rec.get("title", "")
    abstract = rec.get("abstract", "")
    text = f"{title}. {abstract}"
    query_tasks: set[str] = set(rec["query_tasks"])

    rec["normalized_title"] = normalize_title(title)
    review_exception = bool(re.search(r"retrospective (?:chart )?review|overview and development|roadmap and case study", title, re.I))
    if (REVIEW_RE.search(title) and not review_exception) or "review" in str(rec.get("work_type", "")).lower():
        rec["included"] = False
        rec["exclusion_reason"] = "Review / meta-analysis"
        rec["matched_tasks"] = []
        rec["primary_task"] = ""
        return rec
    if not EMBODIED_RE.search(text):
        rec["included"] = False
        rec["exclusion_reason"] = "No embodied robotic action in title/abstract"
        rec["matched_tasks"] = []
        rec["primary_task"] = ""
        return rec

    candidates: list[tuple[int, Task]] = []
    for task in TASKS:
        if eligible(task, text, title, query_tasks):
            candidates.append((score_task(task, text, query_tasks), task))

    if not candidates:
        rec["included"] = False
        rec["exclusion_reason"] = "Task/action inclusion rule not met"
        rec["matched_tasks"] = []
        rec["primary_task"] = ""
        return rec

    # Sampling papers override observational navigation/imaging when tissue acquisition is explicit.
    bronch_sampling_title = bool(
        re.search(r"bronchoscop\w*", title, re.I)
        and re.search(r"diagnostic yield|diagnos\w*|cytopatholog\w*|histopatholog\w*|pathology|molecular adequacy", title, re.I)
    )
    if SAMPLE_ACTION_RE.search(text) or bronch_sampling_title:
        sampling = [item for item in candidates if item[1].class_code == "S"]
        if sampling:
            candidates = sampling

    candidates.sort(key=lambda item: (-item[0], CLASS_ORDER[item[1].class_code], item[1].code))
    primary = candidates[0][1]
    rec["included"] = True
    rec["exclusion_reason"] = ""
    rec["matched_tasks"] = [task.code for _, task in candidates]
    rec["primary_task"] = primary.code
    rec["class_code"] = primary.class_code
    rec["class_en"] = primary.class_en
    rec["class_zh"] = primary.class_zh
    rec["task_en"] = primary.task_en
    rec["task_zh"] = primary.task_zh
    rec["evidence_tier"] = "Core (title-explicit)" if is_core_title(primary, title) else "Expanded (abstract-supported)"
    return rec


def serializable(rec: dict[str, Any]) -> dict[str, Any]:
    out = rec.copy()
    for field in ("query_tasks", "source_dbs", "source_ids"):
        if isinstance(out.get(field), set):
            out[field] = sorted(out[field])
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            cooked = row.copy()
            for key, value in list(cooked.items()):
                if isinstance(value, (list, set, tuple)):
                    cooked[key] = "; ".join(str(x) for x in value)
            writer.writerow(cooked)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/bibliometrics")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    out_dir = Path(args.out)
    cache_dir = out_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict[str, Any]] = []
    query_log: list[dict[str, Any]] = []

    def collect_task(task: Task) -> tuple[Task, list[dict[str, Any]], int, str, list[dict[str, Any]], int, str]:
        oa_records, oa_hits, oa_query = collect_openalex(task, cache_dir, args.refresh)
        ep_records, ep_hits, ep_query = collect_europepmc(task, cache_dir, args.refresh)
        return task, oa_records, oa_hits, oa_query, ep_records, ep_hits, ep_query

    completed: dict[str, tuple[Task, list[dict[str, Any]], int, str, list[dict[str, Any]], int, str]] = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(collect_task, task): task.code for task in TASKS}
        for future in as_completed(futures):
            result = future.result()
            completed[result[0].code] = result
            task, oa_records, oa_hits, _, ep_records, ep_hits, _ = result
            print(f"{task.code}: OpenAlex {oa_hits}/{len(oa_records)}, Europe PMC {ep_hits}/{len(ep_records)}", flush=True)

    # arXiv is queried serially to comply with its official legacy-API rate limit.
    arxiv_completed: dict[str, tuple[list[dict[str, Any]], int, str]] = {}
    made_arxiv_request = False
    for task in TASKS:
        needs_fetch = args.refresh or not (cache_dir / f"arxiv_{task.code}.json").exists()
        if needs_fetch and made_arxiv_request:
            time.sleep(3.1)
        ax_records, ax_hits, ax_query = collect_arxiv(task, cache_dir, args.refresh)
        if needs_fetch:
            made_arxiv_request = True
        arxiv_completed[task.code] = (ax_records, ax_hits, ax_query)
        print(f"{task.code}: arXiv {ax_hits}/{len(ax_records)}", flush=True)

    for task in TASKS:
        task, oa_records, oa_hits, oa_query, ep_records, ep_hits, ep_query = completed[task.code]
        ax_records, ax_hits, ax_query = arxiv_completed[task.code]
        for raw in oa_records:
            all_records.append(openalex_to_record(raw, task.code))
        query_log.append({
            "database": "OpenAlex", "task_code": task.code, "class_code": task.class_code,
            "query": oa_query, "raw_hit_count": oa_hits, "retrieved_records": len(oa_records),
            "retrieved_on": date.today().isoformat(), "cutoff": CUTOFF,
            "api_url_template": "https://api.openalex.org/works?filter=title_and_abstract.search:<QUERY>",
        })

        for raw in ep_records:
            all_records.append(europepmc_to_record(raw, task.code))
        query_log.append({
            "database": "Europe PMC", "task_code": task.code, "class_code": task.class_code,
            "query": ep_query, "raw_hit_count": ep_hits, "retrieved_records": len(ep_records),
            "retrieved_on": date.today().isoformat(), "cutoff": CUTOFF,
            "api_url_template": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<QUERY>",
        })

        for raw in ax_records:
            all_records.append(arxiv_to_record(raw, task.code))
        query_log.append({
            "database": "arXiv", "task_code": task.code, "class_code": task.class_code,
            "query": ax_query, "raw_hit_count": ax_hits, "retrieved_records": len(ax_records),
            "retrieved_on": date.today().isoformat(), "cutoff": CUTOFF,
            "api_url_template": "https://export.arxiv.org/api/query?search_query=<QUERY>",
        })

    merged = merge_records(all_records)
    classified = [classify_record(rec) for rec in merged]
    included = [rec for rec in classified if rec["included"]]
    included.sort(key=lambda rec: (str(rec.get("class_code", "")), str(rec.get("primary_task", "")), int(rec.get("year") or 0), rec["title"]))

    # Query-level included counts are not additive because one work can hit more than one query.
    for row in query_log:
        task_code = row["task_code"]
        db = row["database"]
        row["union_included_with_query_tag"] = sum(
            1 for rec in included if task_code in rec["query_tasks"] and db in rec["source_dbs"]
        )

    counts = Counter(rec["primary_task"] for rec in included)
    core_counts = Counter(rec["primary_task"] for rec in included if rec.get("evidence_tier") == "Core (title-explicit)")
    class_counts = Counter(rec["class_code"] for rec in included)
    core_class_counts = Counter(rec["class_code"] for rec in included if rec.get("evidence_tier") == "Core (title-explicit)")
    print("Included by task:", dict(sorted(counts.items())))
    print("Core by task:", dict(sorted(core_counts.items())))
    print("Included by class:", dict(sorted(class_counts.items())))
    print("Core by class:", dict(sorted(core_class_counts.items())))
    print(f"Raw records={len(all_records)}, merged={len(merged)}, included={len(included)}")

    metadata = {
        "cutoff": CUTOFF,
        "start_date": START_DATE,
        "retrieved_on": date.today().isoformat(),
        "task_count": len(TASKS),
        "raw_records": len(all_records),
        "deduplicated_candidates": len(merged),
        "included_records": len(included),
        "task_counts": dict(sorted(counts.items())),
        "core_task_counts": dict(sorted(core_counts.items())),
        "class_counts": dict(sorted(class_counts.items())),
        "core_class_counts": dict(sorted(core_class_counts.items())),
        "databases": ["OpenAlex", "Europe PMC", "arXiv"],
        "method_note": "Union of OpenAlex, Europe PMC, and direct arXiv title/abstract searches (exact task phrases plus targeted broad combinations for low-count tasks); DOI then canonicalized-title deduplication; original research/preprints only; deterministic title/abstract inclusion rules; one primary task per work; high-precision core and expanded sensitivity tiers reported separately.",
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "tasks.json").write_text(json.dumps([task.__dict__ for task in TASKS], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "query_log.json").write_text(json.dumps(query_log, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "candidates.jsonl").write_text("\n".join(json.dumps(serializable(rec), ensure_ascii=False) for rec in classified), encoding="utf-8")
    (out_dir / "included.jsonl").write_text("\n".join(json.dumps(serializable(rec), ensure_ascii=False) for rec in included), encoding="utf-8")

    fields = [
        "source_dbs", "source_ids", "doi", "pmid", "title", "year", "publication_date",
        "work_type", "venue", "cited_by_count", "url", "query_tasks", "matched_tasks",
        "included", "exclusion_reason", "class_code", "class_en", "class_zh", "primary_task",
        "task_en", "task_zh", "evidence_tier", "abstract",
    ]
    write_csv(out_dir / "included.csv", included, fields)
    write_csv(out_dir / "candidates.csv", classified, fields)
    write_csv(out_dir / "query_log.csv", query_log, list(query_log[0].keys()))


if __name__ == "__main__":
    main()
