"""Create the revised P5 nested-bar SVG/PNG-ready source."""
import csv,html
from pathlib import Path

ROOT=Path(r"D:\Researching\清华\古月\Project\综述\支持图表\codex-参考")
DATA=ROOT/"02_当前主数据"/"P5_public_visible_available_counts_2026-08-13.csv"
OUT=ROOT/"03_PPT图表"/"P5_主动观察_public_visible与public_available_扩展版.svg"
rows=list(csv.DictReader(open(DATA,encoding="utf-8-sig")))
rows=sorted(rows,key=lambda x:int(x['public_visible_precision_title_candidates']),reverse=True)
W,H=1600,1030;left,right,top,bottom=420,110,135,150;pw=W-left-right;rh=(H-top-bottom)/len(rows);mx=max(int(x['public_visible_precision_title_candidates']) for x in rows)
purple="#5B1A6E";green="#2E7D65";grid="#E7E1EA";text="#2B1532";muted="#6D6170"
b=[f'<rect width="{W}" height="{H}" fill="white"/>',f'<text x="60" y="65" font-family="Microsoft YaHei,Arial" font-size="34" font-weight="700" fill="{text}">主动观察式检测｜公开可见与公开全文候选版图</text>']
for i in range(5):
 x=left+pw*i/4;val=round(mx*i/4);b += [f'<line x1="{x}" y1="{top-18}" x2="{x}" y2="{H-bottom+10}" stroke="{grid}"/>',f'<text x="{x}" y="{H-bottom+43}" text-anchor="middle" font-family="Arial" font-size="18" fill="{muted}">{val}</text>']
for i,r in enumerate(rows):
 y=top+i*rh+rh*.13;h=rh*.58;v=int(r['public_visible_precision_title_candidates']);a=int(r['public_available_location_identified']);wv=pw*v/mx;wa=pw*a/mx
 b += [f'<text x="{left-22}" y="{y+h*.72}" text-anchor="end" font-family="Microsoft YaHei,Arial" font-size="22" fill="{text}">{html.escape(r["task"])}</text>',f'<rect x="{left}" y="{y}" width="{wv}" height="{h}" rx="7" fill="{purple}"/>',f'<rect x="{left}" y="{y+h*.30}" width="{wa}" height="{h*.40}" rx="4" fill="{green}"/>',f'<text x="{left+wv+12}" y="{y+h*.72}" font-family="Arial" font-size="21" fill="{text}">{v}</text>']
 if a:b.append(f'<text x="{left+wa-7}" y="{y+h*.60}" text-anchor="end" font-family="Arial" font-size="15" font-weight="700" fill="white">{a}</text>')
b += [f'<rect x="815" y="{H-105}" width="24" height="17" rx="3" fill="{purple}"/><text x="851" y="{H-90}" font-family="Microsoft YaHei,Arial" font-size="18" fill="{muted}">public visible：公开索引题名规则候选</text>',f'<rect x="1220" y="{H-105}" width="24" height="17" rx="3" fill="{green}"/><text x="1256" y="{H-90}" font-family="Microsoft YaHei,Arial" font-size="18" fill="{muted}">public available：识别到公开全文位置</text>',f'<text x="60" y="{H-48}" font-family="Microsoft YaHei,Arial" font-size="15" fill="{muted}">公开索引：OpenAlex、Europe PMC，Crossref/arXiv 补充；2000–2026-08-13。单位：DOI/规范题名去重研究记录。</text>',f'<text x="60" y="{H-22}" font-family="Microsoft YaHei,Arial" font-size="15" fill="{muted}">候选计数并非系统综述全文纳入数；绿色为公开全文位置发现，不是许可证审计。部分补充查询受限流影响；项目/系统另表统计。</text>']
OUT.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'+''.join(b)+'</svg>',encoding="utf-8")
print(OUT)
