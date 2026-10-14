from pathlib import Path
import math, html, json
import cairosvg
out=Path(__file__).resolve().parent
out.mkdir(parents=True, exist_ok=True)
parts=[]
from source_chem import SRC
BACKBONES_UNUSED={False: {'proximal':5,'distal':2}, True: {'proximal':2,'distal':4}}
navy='#0B675E'; blue='#CC5034'; ink='#333B43'; muted='#667078'; purple='#8654A7'
def add(s):parts.append(s)
def text(x,y,s,size=20,color=ink,weight=400,anchor='start',italic=False):
 add(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'+(' font-style="italic"' if italic else '')+'>'+html.escape(s)+'</text>')
def line(x1,y1,x2,y2,color=ink,w=2.4,arrow=False,dash=False):
 add(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{w}"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="4 4"' if dash else '')+'/>')
def path(points,color=ink,w=2.4):
 add('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{w}"/>')
def rect(x,y,w,h,fill='#fff',stroke='none',r=12):add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
def circle(x,y,r,fill,stroke='none'):add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
def charge(x,y):
 circle(x,y,10,'#E6F0F7',ink);text(x,y+4,'+/−',10,ink,anchor='middle')
def wave(x,y,c):
 add(f'<path d="M{x-15},{y} l3,-3 l3,3 l3,-3 l3,3 l3,-3 l3,3" fill="none" stroke="{c}" stroke-width="2.5"/>')
def chain(x,y,n,c):
 wave(x,y,c);pts=[(x,y)]+[(x+i*14,y+(-8 if i%2 else 0)) for i in range(1,n+1)];path(pts,c);return pts[-1]
def double(a,b,c=ink):
 line(*a,*b,c);dx=b[0]-a[0];dy=b[1]-a[1];q=math.hypot(dx,dy);ox=-dy/q*4;oy=dx/q*4;line(a[0]+ox,a[1]+oy,b[0]+ox,b[1]+oy,c,1.8)
def group(x,y,scale=1):add(f'<g transform="translate({x},{y}) scale({scale})">')
def end():add('</g>')
def src_group(x,y,anchor,scale=1.8):
 group(x,y,scale);group(-anchor[0],-anchor[1])
def src_wave(a,b,c):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 if length<6:
  a=(b[0]-10,b[1]);dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 points=[]
 for j in range(13):
  t=j/12;off=1.15*math.sin(t*6*math.pi)
  points.append((a[0]+dx*t-dy/length*off,a[1]+dy*t+dx/length*off))
 path(points,c,1.45)
def src_charge(last,q):
 dx,dy=last[0]-q[0],last[1]-q[1];length=math.hypot(dx,dy)
 radius=10.7
 if length>radius:line(*last,q[0]+dx/length*radius,q[1]+dy/length*radius,ink,1.6)
 circle(*q,radius,'#F1F3F5',ink)
 add(f'<text x="{q[0]}" y="{q[1]}" dominant-baseline="central" text-anchor="middle" fill="{ink}" font-size="12.5">+/−</text>')
def src_carbonyl(carbon,oxygen):
 dx,dy=oxygen[0]-carbon[0],oxygen[1]-carbon[1];length=math.hypot(dx,dy)
 tip=(oxygen[0]-dx/length*6,oxygen[1]-dy/length*6)
 double(carbon,tip)
 add(f'<text x="{oxygen[0]}" y="{oxygen[1]}" dominant-baseline="central" text-anchor="middle" fill="{ink}" font-size="13.5">O</text>')
def src_methyl(points):
 line(*points[0],*points[1],ink,1.8);line(*points[0],*points[2],ink,1.8)
def src_molecule(key,c):
 d=SRC[key]
 path(d['chain'],c,1.8)
 if 'wave' in d:src_wave(*d['wave'],c)
 if 'double' in d:
  a,b=d['double'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
  line(a[0]+dx*.15-dy/length*3,a[1]+dy*.15+dx/length*3,b[0]-dx*.15-dy/length*3,b[1]-dy*.15+dx/length*3,ink,1.6)
  if key.startswith('neutral') or key in ['m2','n2']:line(*a,*b,ink,1.8)
 if 'carbonyl' in d:src_carbonyl(*d['carbonyl'])
 if 'methyl' in d:src_methyl(d['methyl'])
 if 'ring' in d:
  v=d['ring'];oxygen_index=d['oxygen'];o=v[oxygen_index]
  assert len(v)==4 and len(set(v))==4
  assert v[0]==d['chain'][-1] and v[3]==d['tail'][0]
  for i in range(4):
   a,b=v[i],v[(i+1)%4]
   if oxygen_index in [i,(i+1)%4]:
    carbon=b if i==oxygen_index else a
    dx,dy=carbon[0]-o[0],carbon[1]-o[1];length=math.hypot(dx,dy)
    line(o[0]+dx/length*6,o[1]+dy/length*6,*carbon,ink,1.8)
   else:line(*a,*b,ink,1.8)
  add(f'<text x="{o[0]}" y="{o[1]}" dominant-baseline="central" text-anchor="middle" fill="{ink}" font-size="13.5">O</text>')
  path(d['tail'],c,1.8)
  # Cleavage plane crosses the acetone C–O and original alkene C–C bonds.
  upper=((v[1][0]+v[2][0])/2,(v[1][1]+v[2][1])/2)
  lower=((v[0][0]+v[3][0])/2,(v[0][1]+v[3][1])/2)
  dx,dy=lower[0]-upper[0],lower[1]-upper[1];L=math.hypot(dx,dy)
  aa=(upper[0]-dx/L*7,upper[1]-dy/L*7);bb=(lower[0]+dx/L*6,lower[1]+dy/L*6)
  line(*aa,*bb,ink,1.5,False,True);line(*bb,bb[0]+4,bb[1]+5,ink,1.5,True)
 if 'charge' in d:src_charge(d.get('tail',d['chain'])[-1],d['charge'])
def parent(x,y,c,is_b=False):
 k='parent_B' if is_b else 'parent_A';anchor=(482,51) if is_b else (174,49)
 src_group(x+20,y+27,anchor,1.8);src_molecule(k,c)
 text(477 if is_b else 204,32,'Δn' if is_b else 'Δm',13.5,ink,italic=True)
 end();end()
def acetone(x,y):
 group(x,y,1.1);path([(-15,12),(0,3),(15,12)],ink,2.3);double((0,3),(0,-12));text(0,-17,'O',21,anchor='middle');end()
def product(x,y,c,is_b=False,second=False):
 k='PB_'+('B' if is_b else 'A')+('2' if second else '1')
 anchor={'PB_A1':(111,148),'PB_A2':(274,148),'PB_B1':(382,150),'PB_B2':(544,151)}[k]
 src_group(x,y,anchor,1.8);src_molecule(k,c);end();end()
def diagnostic(x,y,c,is_b=False,second=False):
 k=('n' if is_b else 'm')+('2' if second else '1')
 anchor={'m1':(101,254),'m2':(279,257),'n1':(454,253),'n2':(613,249)}[k]
 src_group(x+37,y,anchor,1.8);src_molecule(k,c);end();end()
def neutral(x,y,c,is_b=False,second=False):
 k='neutral_'+('B' if is_b else 'A')+('2' if second else '1')
 anchor={'neutral_A1':(60,207),'neutral_A2':(238,207),'neutral_B1':(390,210),'neutral_B2':(558,208)}[k]
 src_group(x,y,anchor,1.65);src_molecule(k,c);end();end()
add('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="#333B43"/></marker><marker id="uv-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#8654A7"/></marker></defs><g font-family="Arial,Helvetica,sans-serif" stroke-linecap="round" stroke-linejoin="round">')
rect(0,0,1600,1200,'white',r=0)
text(40,43,'A',32,navy,700)
chem_scenes=[]
for idx,c in enumerate([navy,blue]):
 scene_start=len(parts)
 add(f'<g id="chem-{chr(65+idx)}" data-layout-bounds="{42+idx*788} 58 728 534">')
 x=42+idx*788
 rect(x,58,728,534,'#F7FAFD','#D9E5EF',18)
 text(x+26,94,'C=C location isomer '+('A' if idx==0 else 'B'),25,c,700)
 parent(x+272,130,c,bool(idx));acetone(x+251,212)
 text(x+361,216,'hν',23,ink,italic=True)
 text(x+30,195,'PB reaction',18,ink,italic=True);text(x+30,221,'+58 Da',20,ink,700)
 line(x+355,174,x+355,229,ink);path([(x+190,244),(x+190,229),(x+540,229),(x+540,244)],ink);line(x+190,229,x+190,253,ink,2.4,True);line(x+540,229,x+540,253,ink,2.4,True)
 for k in range(2):
  cx=x+190+k*350
  product(cx-(12 if idx==1 and k==1 else 0),315,c,bool(idx),bool(k))
  line(cx+5,362,cx+5,414,ink,2.4,True);text(cx+28,403,'CID',19,ink,700)
  neutral(cx-68,403,c,bool(idx),bool(k))
  add(f'<path d="M{cx-5},362 Q{cx-8},386 {cx-32},394" fill="none" stroke="{ink}" stroke-width="2" marker-end="url(#arrow)"/>')
  rect(cx-81,416,190,138,'#E4F2EE' if idx==0 else '#FBEAE3',r=12)
  diagnostic(cx-21,484,c,bool(idx),bool(k));text(cx+121,490,('m' if idx==0 else 'n')+str(k+1),25,c,700,italic=True)
 text(x+364,573,'diagnostic ions of '+('A' if idx==0 else 'B'),22,c,700,anchor='middle')
 end()
 chem_scenes.append(parts[scene_start:])
top_end=len(parts)
text(40,650,'B',32,navy,700)
# Detection row
add('<g transform="translate(0,32)">')
det_frames={}
for x,w,title in [(42,445,'On-line PB reaction'),(527,437,'nanoESI-MS'),(1004,554,'MS/MS')]:
 start=len(parts)
 rect(x,643,w,249,'#FAFCFE','#DBE6EF',14);text(x+20,676,title,23,ink,700)
 det_frames[title]=parts[start:];del parts[start:]
# On-line reaction apparatus
add('<g id="apparatus" data-layout-bounds="42 643 445 249">');parts.extend(det_frames['On-line PB reaction'])
text(65,716,'UV lamp',20,ink);text(65,741,'~254 nm',20,purple,700)
path([(83,797),(83,767),(225,767)],ink)
circle(83,815,19,'white',ink);text(83,820,'HV',22,ink,700,anchor='middle')
rect(227,710,29,10,'#D4D8DD',ink,3)
rect(230,720,23,22,'#F2EAF8',purple,5)
line(235,725,235,736,purple,1.8);line(248,725,248,736,purple,1.8)
for target in [(185,763),(203,763),(221,763)]:
 add(f'<path d="M240,745 L{target[0]},{target[1]}" fill="none" stroke="{purple}" stroke-width="1.8" marker-end="url(#uv-arrow)"/>')
line(143,763,225,763,muted,3);line(143,770,225,770,muted,3)
for a in [-2,-1,0,1,2]:add(f'<path d="M220,767 Q252,{767+a*3} 271,{767+a*9}" fill="none" stroke="{ink}" stroke-width="1.6"/>')
path([(309,730),(295,743),(295,758)],muted,4);path([(309,803),(295,790),(295,775)],muted,4)
line(316,750,331,730,muted,4);line(316,784,331,806,muted,4)
text(302,716,'MS inlet',20,ink,anchor='middle');text(205,838,'lipids in',20,ink,anchor='middle');text(205,862,'acetone/water',20,ink,anchor='middle')
end()
line(455,780,512,780,ink,3,True);line(932,780,990,780,ink,3,True)
def axes(x,y,w,h):line(x,y,x+w,y,ink,1.7,True);line(x,y,x,y-h,ink,1.7,True);text(x+w+6,y+3,'m/z',22,ink,italic=True);add(f'<text transform="translate({x-22},{y-h/2}) rotate(-90)" text-anchor="middle" font-size="22" fill="{ink}">Relative Intensity</text>')
add('<g id="ms1" data-layout-bounds="527 643 437 249">');parts.extend(det_frames['nanoESI-MS'])
axes(574,843,311,122)
line(623,843,623,747,ink,3);text(610,731,'A',18,navy,700);text(625,731,',',18,ink);text(633,731,'B',18,blue,700)
line(754,843,754,782,ink,3);text(769,727,'PB products',18,ink,700,anchor='middle');text(769,753,'+58 Da',18,ink,700,anchor='middle');line(626,791,747,791,ink,2,True)
end()
add('<g id="msms" data-layout-bounds="1004 643 554 249">');parts.extend(det_frames['MS/MS'])
axes(1057,843,432,123)
for x,h,c in [(1101,46,navy),(1112,61,navy),(1162,63,blue),(1173,86,blue),(1392,38,ink),(1423,55,ink)]:line(x,843,x,843-h,c,3)
path([(1093,747),(1093,740),(1181,740),(1181,747)],muted,1.5);text(1137,716,'diagnostic ions',22,ink,anchor='middle');text(1400,720,'PB products of',22,ink,anchor='middle');text(1387,746,'A',18,navy,700);text(1402,746,',',18,ink);text(1410,746,'B',18,blue,700)
end()
end()
add('<g transform="translate(0,36)">')
# Quantitation row preserves original direction: diagnostic inset -> calibration -> concentrations
add('<g id="quantitation-heading" data-layout-bounds="42 928 600 35">')
text(42,953,'Lipid C=C isomer ID & quantitation',25,ink,700)
end()
add('<g id="diagnostic-inset" data-layout-bounds="1040 935 518 174">')
rect(1040,935,518,174,'#F4F9FD','#C5DFEF',12)
line(1093,1083,1093,980,ink,1.6,True);line(1093,1083,1515,1083,ink,1.6,True)
for x,h,c,label in [(1150,45,navy,'m1'),(1232,69,navy,'m2'),(1351,75,blue,'n1'),(1433,102,blue,'n2')]:line(x,1083,x,1083-h,c,3);text(x,1083-h-9,label,22,c,700,anchor='middle',italic=True)
for a,b,y in [(1150,1232,1051),(1351,1433,1034)]:line(a+4,y,b-4,y,ink,1.5,True);line(b-4,y,a+4,y,ink,1.5,True);text((a+b)/2,y+24,'26 Da',22,ink,anchor='middle')
end()
line(1093,839,1049,934,muted,1.1,False,True);line(1181,839,1553,934,muted,1.1,False,True)
line(1019,1028,978,1028,ink,2.8,True)
# Calibration curve
add('<g id="calibration" data-layout-bounds="555 944 405 192">')
line(718,1091,928,1091,ink,1.7,True);line(718,1091,718,964,ink,1.7,True)
line(733,1076,909,969,ink,1.6)
for x,y in [(748,1067),(791,1041),(836,1013),(887,982)]:circle(x,y,4,ink)
text(803,1120,'C',24,ink,italic=True);text(817,1127,'A',17,ink,italic=True);text(840,1120,'/',24,ink);text(859,1120,'C',24,ink,italic=True);text(873,1127,'B',17,ink,italic=True)
for yy,prefix in [(1009,'m'),(1043,'n')]:
 text(574,yy,'I',24,ink,italic=True);text(583,yy+7,prefix+'1',17,ink,italic=True);text(610,yy,'+',24,ink);text(636,yy,'I',24,ink,italic=True);text(645,yy+7,prefix+'2',17,ink,italic=True)
line(568,1020,687,1020,ink,1.5)
end()
line(530,1028,486,1028,ink,2.8,True)
add('<g id="concentration-bars" data-layout-bounds="99 947 368 190">')
line(155,1091,436,1091,ink,1.7,True);line(155,1091,155,968,ink,1.7,True)
text(128,1033,'μM',22,ink,anchor='middle',italic=True)
rect(219,1041,38,50,navy,r=0);rect(335,998,38,93,blue,r=0)
text(238,1028,'Δm',22,ink,anchor='middle',italic=True);text(354,985,'Δn',22,ink,anchor='middle',italic=True);text(238,1117,'A',19,navy,700,anchor='middle');text(354,1117,'B',19,blue,700,anchor='middle')
end()
end()
add('</g></svg>')
svg=out/'figure1-AB.svg';svg.write_text('\n'.join(parts))
cairosvg.svg2png(url=str(svg),write_to=str(out/'figure1-AB.png'),output_width=4800,output_height=3600)
cairosvg.svg2png(url=str(svg),write_to=str(out/'preview.png'),output_width=1600,output_height=1200)
print(svg)

import xml.etree.ElementTree as ET
root=ET.fromstring('\n'.join(parts[:top_end])+ '</g></svg>')
root.set('width','1600');root.set('height','610');root.set('viewBox','0 0 1600 610')
for el in root.iter():
 if el.tag.endswith('rect') and el.get('x')=='0' and el.get('y')=='0':el.set('height','610')
# Label as B for the user's requested review-triptych subpanel; scientific content is Figure 1A.
ns={'s':'http://www.w3.org/2000/svg'}
for el in root.findall('.//s:text',ns):
 if el.text=='A' and el.get('x')=='40' and el.get('y')=='43':el.text='B'
a_svg=out/'figure1A-PB.svg'
a_svg.write_text(ET.tostring(root,encoding='unicode'))
cairosvg.svg2png(url=str(a_svg),write_to=str(out/'figure1A-PB.png'),output_width=4800,output_height=1830)
