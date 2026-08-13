"""Precision screen the P5 high-recall public-index pool using auditable title rules."""
import argparse,csv,re,json
from pathlib import Path

DEFAULT_BASE=Path(__file__).resolve().parents[1]/"outputs"/"p5_comprehensive_public_landscape_2026-08-13"

RULES={
"A1": (r"(robot(ic|ized)?|autonomous|telerobot(ic)?|robot.assisted).{0,45}(ultrasound|sonograph)|(ultrasound|sonograph).{0,45}(robot(ic|ized)?|autonomous|telerobot(ic)?|robot.assisted)",r"surgery|surgical|resection|myomectomy|enucleation|prostatectomy|ablation|injection|puncture|needle|biopsy|catheter|therapy|therapeutic|rehabilitation|segmentation|lesion detection|review|simulation.based assessment|focused ultrasound|organ.sparing|blood clot"),
"A2": (r"(robot(ic|ized)?|autonomous|semi.autonomous|self.propell|motorized|active).{0,55}(endoscop|colonoscop|gastroscop)|(endoscop|colonoscop|gastroscop).{0,55}(robot(ic|ized)?|autonomous|semi.autonomous|self.propell|motorized)",r"review|robotics in colonoscopy|surgery|surgical|myotomy|fundoplication|thyroidectomy|gastrectomy|bypass|scope holder|transesophageal|cannulation|human.machine interface"),
"A3": (r"((magnet(ic|ically controlled)?|robot(ic)?|active|self.propell|locomotion|steerable|navigation).{0,55}(capsule endoscop|capsule robot)|(capsule endoscop|capsule robot).{0,55}(magnet(ic|ically controlled)?|robot(ic)?|active|self.propell|locomotion|steerable|navigation))",r"crohn|cleanliness|scoring|review|survey|case report|budget impact|mucosal healing|artificial intelligence versus|hybrid living|drug delivery|biopsy|tissue sampling|posterior capsule|prostatic capsule|skin lesion|polishing"),
"A4": (r"(robot(ic|ically assisted)?|autonomous|semi.autonomous|shape.sensing).{0,45}bronchoscop|bronchoscop.{0,45}(robot(ic|ically assisted)?|autonomous|semi.autonomous|shape.sensing)",r"review|perspective|best practices|learning curve|ablation|photodynamic|resection|removal|intubation|sealant|valve|survival|protocol|without robotic"),
"A5": (r"(robot(ic|ically assisted)?|contactless robotic|robot.assisted|robotically aligned|robot.mounted).{0,55}(optical coherence|\bOCT\b)|(optical coherence|\bOCT\b).{0,55}(robot(ic|ically assisted)?|contactless robotic|robot.assisted|robotically aligned|robot.mounted)",r"fingerprint|fingermark|ceramic|injection|cannulation|ablation|craniotomy|suturing|needle|surgery|surgical|segmentation|classification|diagnos|risk factors|intraocular pressure|calibration|path planning"),
"A6": (r"(robot(ic)?|autonomous).{0,45}(auscultat|stethoscop)|(auscultat|stethoscop).{0,45}(robot(ic)?|autonomous)",r"empathy|social robot|industrial|classification|dataset|review|security"),
"A7": (r"(robot(ic)?|remote.controlled|autonomous acquisition|self.align).{0,55}(fundus|slit.lamp|ophthalmoscop)|(fundus|slit.lamp|ophthalmoscop).{0,55}(robot(ic)?|remote.controlled|self.align)",r"surgery|injection|classification|diagnosis|screening|deep learning"),
"A8": (r"(robot(ic)?|telepresence).{0,55}(otoscop|ear examination)|(otoscop|ear examination).{0,55}(robot(ic)?|telepresence)",r"classification|deep learning|diagnosis"),
"A9": (r"(robot(ic|ically controlled)?|autonomous|robot.driven|robot.assisted).{0,100}(wound|skin).{0,45}(scan|imag|reconstruct|assess|evaluation)|(wound|skin).{0,45}(scan|imag|reconstruct|assess|evaluation).{0,100}(robot|autonomous)",r"repair|bioprint|surgery|surgical|therapy|debrid|electronic skin|robot skin|implant|ultrasound"),
"A10":(r"(robot(ic|ically assisted)?|autonomous|robot.arm|robotic arm powered).{0,65}(raman|hyperspectral|multispectral|diffuse reflectance|photoacoustic|confocal|endomicroscop|terahertz)|(raman|hyperspectral|multispectral|diffuse reflectance|photoacoustic|confocal|endomicroscop|terahertz).{0,65}(robot(ic|ically assisted)?|autonomous|robot.arm)",r"fingerprint|fingermark|trace.residue|mars|nuclear|plastic|remote sensing|material character|data fusion for robotic systems|optoelectronic device|surgery|surgical|ablation|prostate|instrument suite"),
"A11":(r"(robot(ic)?|autonomous|remote).{0,55}(laryngoscop|oral examination|oral cavity inspection)|(laryngoscop|oral examination).{0,55}(robot(ic)?|autonomous|remote)",r"surgery|resection|intubat|classification|segmentation|deep learning"),
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=DEFAULT_BASE)
    parser.add_argument('--output-dir',type=Path,default=None)
    args=parser.parse_args(); base=args.input_dir.resolve(); dest=(args.output_dir or base).resolve(); dest.mkdir(parents=True,exist_ok=True)
    src=list(csv.DictReader(open(base/'p5_public_visible_available_records.csv',encoding='utf-8-sig')))
    out=[]
    for x in src:
        inc,exc=RULES[x['task_code']]; title=x['title']
        if re.search(inc,title,re.I) and not re.search(exc,title,re.I):
            y=dict(x);y['screening']='precision automated title candidate; manual verification pending';out.append(y)
    with open(dest/'p5_precision_title_candidates.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    counts=[]
    for code in RULES:
        a=[x for x in out if x['task_code']==code]
        task=next((x['task'] for x in src if x['task_code']==code),code)
        counts.append({'task_code':code,'task':task,'public_visible_precision_title_candidates':len(a),'public_available_location_identified':sum(x['public_available']=='yes' for x in a),'since_2021':sum(x['year'].isdigit() and int(x['year'])>=2021 for x in a),'status':'precision automated title candidate; manual verification pending'})
    with open(dest/'p5_precision_title_candidate_counts.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(counts[0]));w.writeheader();w.writerows(counts)
    print(json.dumps({'records':len(out),'counts':counts,'output_dir':str(dest)},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
