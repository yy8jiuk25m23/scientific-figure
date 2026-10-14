from pathlib import Path
import math, html, json
import cairosvg
out=Path('/workspace/scientific-figure/figure-redesign/pb-lipid-isomers/compact-v2')
out.mkdir(parents=True, exist_ok=True)
parts=[]
navy='#174D78'; blue='#278BC1'; ink='#152B3B'; muted='#61798B'
def add(s):parts.append(s)
def text(x,y,s,size=20,color=ink,weight=400,anchor='start',italic=False):
 add(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'+(' font-style="italic"' if italic else '')+'>'+html.escape(s)+'</text>')
def line(x1,y1,x2,y2,color=ink,w=2.4,arrow=False,dash=False):
 add(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{w}"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="4 4"' if dash else '')+'/>')
def path(points,color=ink,w=2.4):
 add('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{w}"/>')
def rect(x,y,w,h,fill='#fff',stroke='none',r=12):add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
def circle(x,y,r,fill,stroke='none'):add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
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
def parent(x,y,c,is_b=False):
 group(x,y,1.35)
 pts=[(0,8),(14,0),(28,8),(42,0),(56,8),(70,0),(84,6),(94,20),(112,16)]
 if is_b:pts=[(0,20),(14,20),(24,2),(42,-2),(57,8),(71,0),(85,8),(100,0)]
 wave(0,pts[0][1],c);path(pts,c)
 a,b=(pts[2],pts[3]) if is_b else (pts[5],pts[6]);dx=b[0]-a[0];dy=b[1]-a[1];q=math.hypot(dx,dy);line(a[0]+2-dy/q*4,a[1]+4+dx/q*0,b[0]-2-dy/q*4,b[1]+4,c,1.8)
 charge(pts[-1][0]+11,pts[-1][1]);text(55,-12,'Δn' if is_b else 'Δm',13,ink,italic=True);end()
def acetone(x,y):
 group(x,y,1.1);path([(-15,12),(0,3),(15,12)]);double((0,3),(0,-12));text(0,-15,'O',15,anchor='middle');end()
def product(x,y,c,is_b=False,second=False):
 group(x,y,1.25)
 n=2 if is_b else 5
 ex,ey=chain(-14*n-4,10 if n%2==0 else 18,n,c)
 assert (ex,ey)==(-4,10), (ex,ey)
 if not second:
  path([(-4,10),(2,-12),(17,-8),(14,14),(-4,10)])
  rect(10,-16,15,16,'white',r=0);text(17,-3,'O',14,anchor='middle')
  path([(2,-12),(-8,-27)]);path([(2,-12),(8,-31)])
  if is_b:tail=[(14,14),(28,6),(42,14),(56,6),(70,14),(84,6)]
  else:tail=[(14,14),(25,27),(47,27)]
  path(tail,c);charge(tail[-1][0]+11,tail[-1][1])
  line(8,-24,-2,22,navy,2,False,True)
 else:
  path([(-4,10),(0,-10),(17,-15),(20,10),(-4,10)])
  rect(-8,-17,15,15,'white',r=0);text(0,-3,'O',14,anchor='middle')
  path([(17,-15),(15,-34)]);path([(17,-15),(31,-23)])
  tail=[(20,10),(33,22),(55,22)] if not is_b else [(20,10),(34,2),(48,10),(62,2),(76,10),(90,2)]
  path(tail,c);charge(tail[-1][0]+11,tail[-1][1]);line(13,-29,13,19,navy,2,False,True)
 sx,sy=(13,19) if second else (-2,22)
 add(f'<path d="M{sx},{sy} l7,8" fill="none" stroke="{navy}" stroke-width="2" marker-end="url(#arrow)"/>');end()
def diagnostic(x,y,c,is_b=False,second=False):
 group(x,y,1.12)
 if not second:
  double((0,0),(0,-15));text(0,-19,'O',14,anchor='middle')
  pts=[(0,0),(14,8),(28,0),(42,8),(56,0)] if is_b else [(0,0),(8,16),(30,16)]
 else:
  double((0,0),(0,18));path([(-14,-8),(0,0),(14,-7)])
  pts=[(0,18),(14,26),(28,18),(42,26),(56,18)] if is_b else [(0,18),(0,34),(18,43)]
 path(pts,c);charge(pts[-1][0]+11,pts[-1][1]);end()
def neutral(x,y,c,is_b=False,second=False):
 group(x,y,.8)
 n=1 if is_b else 4
 ex,ey=chain(-n*14,12,n,c)
 if second:double((ex,ey),(ex,ey-14));text(ex,ey-18,'O',13,anchor='middle')
 else:
  double((ex,ey),(ex,ey-18));path([(ex,ey-18),(ex-13,ey-26)]);path([(ex,ey-18),(ex+13,ey-26)])
 end()
add('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1034" viewBox="0 0 1600 1034"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="context-stroke"/></marker></defs><g font-family="Arial,Helvetica,sans-serif" stroke-linecap="round" stroke-linejoin="round">')
rect(0,0,1600,1034,'white',r=0)
text(40,43,'A',32,navy,700)
for idx,c in enumerate([navy,blue]):
 x=42+idx*788
 rect(x,58,728,468,'#F7FAFD','#D9E5EF',18)
 text(x+26,94,'C=C location isomer '+('A' if idx==0 else 'B'),25,c,700)
 parent(x+272,130,c,bool(idx));acetone(x+251,190)
 text(x+361,194,'hν',23,navy,italic=True)
 text(x+30,195,'PB reaction',18,navy,italic=True);text(x+30,221,'+58 Da',20,navy,700)
 line(x+355,174,x+355,229,navy);path([(x+190,244),(x+190,229),(x+540,229),(x+540,244)],navy);line(x+190,229,x+190,253,navy,2.4,True);line(x+540,229,x+540,253,navy,2.4,True)
 for k in range(2):
  cx=x+190+k*350
  product(cx,296,c,bool(idx),bool(k))
  line(cx+5,345,cx+5,390,navy,2.4,True);text(cx+28,378,'CID',19,ink,700)
  neutral(cx-55,379,c,bool(idx),bool(k))
  add(f'<path d="M{cx-5},345 Q{cx-8},366 {cx-33},374" fill="none" stroke="{navy}" stroke-width="2" marker-end="url(#arrow)"/>')
  rect(cx-60,404,153,80,'#E7F0F8' if idx==0 else '#DCEEF9',r=12)
  diagnostic(cx-21,432,c,bool(idx),bool(k));text(cx+110,451,('m' if idx==0 else 'n')+str(k+1),25,c,700,italic=True)
 text(x+364,507,'diagnostic ions of '+('A' if idx==0 else 'B'),22,c,700,anchor='middle')
text(40,569,'B',32,navy,700)
# Detection row
add('<g transform="translate(0,-62)">')
for x,w,title in [(42,445,'On-line PB reaction'),(527,437,'nanoESI-MS'),(1004,554,'MS/MS')]:
 rect(x,643,w,249,'#FAFCFE','#DBE6EF',14);text(x+20,676,title,23,navy,700)
# On-line reaction apparatus
text(65,716,'UV lamp',16,navy);text(65,741,'~254 nm',18,navy,700)
path([(83,797),(83,767),(225,767)],ink)
circle(83,815,19,'white',ink);text(83,820,'HV',15,ink,700,anchor='middle')
rect(236,713,10,21,'#B1D7EE',navy,4);circle(241,738,10,'#B1D7EE',navy)
for a in [-1,0,1]:line(241+a*7,754,241+a*18,768,blue,1.7)
line(143,763,225,763,muted,3);line(143,770,225,770,muted,3)
for a in [-2,-1,0,1,2]:add(f'<path d="M220,767 Q252,{767+a*3} 271,{767+a*9}" fill="none" stroke="{navy}" stroke-width="1.6"/>')
path([(309,730),(295,743),(295,758)],muted,4);path([(309,803),(295,790),(295,775)],muted,4)
line(316,750,331,730,muted,4);line(316,784,331,806,muted,4)
text(302,716,'MS inlet',17,ink,anchor='middle');text(205,838,'lipids in',17,navy,anchor='middle');text(205,862,'acetone/water',17,navy,anchor='middle')
line(455,780,512,780,navy,3,True);line(932,780,990,780,navy,3,True)
def axes(x,y,w,h):line(x,y,x+w,y,ink,1.7,True);line(x,y,x,y-h,ink,1.7,True);text(x+w+6,y+3,'m/z',15,ink,italic=True);add(f'<text transform="translate({x-22},{y-h/2}) rotate(-90)" text-anchor="middle" font-size="13" fill="{ink}">Relative Intensity</text>')
axes(574,843,311,122)
line(623,843,623,747,ink,3);text(623,731,'A,B',18,navy,700,anchor='middle')
line(754,843,754,782,navy,3);text(769,727,'PB products',18,navy,700,anchor='middle');text(769,753,'+58 Da',18,navy,700,anchor='middle');line(626,791,747,791,navy,2,True)
axes(1057,843,432,123)
for x,h,c in [(1101,46,navy),(1112,64,navy),(1162,63,blue),(1173,84,blue),(1392,38,ink),(1423,55,navy)]:line(x,843,x,843-h,c,3)
path([(1093,747),(1093,740),(1181,740),(1181,747)],muted,1.5);text(1137,716,'diagnostic ions',16,ink,anchor='middle');text(1400,720,'PB products of',17,navy,anchor='middle');text(1400,746,'A,B',18,navy,700,anchor='middle')
end()
add('<g transform="translate(0,-104)">')
# Quantitation row preserves original direction: diagnostic inset -> calibration -> concentrations
text(42,953,'Lipid C=C isomer ID & quantitation',25,navy,700)
rect(1040,935,518,174,'#F4F9FD','#C5DFEF',12)
line(1093,1083,1093,980,ink,1.6,True);line(1093,1083,1515,1083,ink,1.6,True)
for x,h,c,label in [(1150,45,navy,'m1'),(1232,70,navy,'m2'),(1351,62,blue,'n1'),(1433,98,blue,'n2')]:line(x,1083,x,1083-h,c,3);text(x,1083-h-9,label,19,c,700,anchor='middle',italic=True)
for a,b,y in [(1150,1232,1051),(1351,1433,1034)]:line(a+4,y,b-4,y,ink,1.5,True);line(b-4,y,a+4,y,ink,1.5,True);text((a+b)/2,y+24,'26 Da',16,ink,anchor='middle')
line(1101,885,1049,934,blue,1.1,False,True);line(1173,885,1553,934,blue,1.1,False,True)
line(1019,1028,978,1028,navy,2.8,True)
# Calibration curve
line(718,1091,928,1091,ink,1.7,True);line(718,1091,718,964,ink,1.7,True)
line(733,1076,909,969,navy,1.6)
for x,y in [(748,1067),(791,1041),(836,1013),(887,982)]:circle(x,y,4,navy)
text(803,1120,'C',18,ink,italic=True);text(816,1126,'A',12,ink,italic=True);text(834,1120,'/',18,ink);text(851,1120,'C',18,ink,italic=True);text(864,1126,'B',12,ink,italic=True)
for yy,prefix in [(1009,'m'),(1043,'n')]:
 text(578,yy,'I',18,ink,italic=True);text(585,yy+5,prefix+'1',12,ink,italic=True);text(609,yy,'+',18,ink);text(630,yy,'I',18,ink,italic=True);text(637,yy+5,prefix+'2',12,ink,italic=True)
line(569,1020,678,1020,ink,1.5)
line(530,1028,486,1028,navy,2.8,True)
line(155,1091,436,1091,ink,1.7,True);line(155,1091,155,968,ink,1.7,True)
text(128,1033,'μM',18,ink,anchor='middle',italic=True)
rect(219,1041,38,50,navy,r=0);rect(335,998,38,93,blue,r=0)
text(238,1028,'Δm',17,ink,anchor='middle',italic=True);text(354,985,'Δn',17,ink,anchor='middle',italic=True);text(238,1117,'A',19,navy,700,anchor='middle');text(354,1117,'B',19,blue,700,anchor='middle')
end()
add('</g></svg>')
svg=out/'pb-blue-white-compact-v2.svg';svg.write_text('\n'.join(parts))
cairosvg.svg2png(url=str(svg),write_to=str(out/'pb-blue-white-compact-v2.png'),output_width=4800,output_height=3102)
cairosvg.svg2png(url=str(svg),write_to='/workspace/figure-setup/compact-preview.png',output_width=1600,output_height=1034)
print(svg)
