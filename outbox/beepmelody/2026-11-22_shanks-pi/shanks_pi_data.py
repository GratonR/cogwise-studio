import mpmath, csv
from PIL import Image, ImageDraw, ImageFont
mpmath.mp.dps=760
tr=mpmath.nstr(mpmath.pi,750,strip_zeros=False)[2:709]
sh501='9833673362440656643086021395016092448077230943628553096620275569397986950222474996206074970304123668'+'8619951100892023837702131416941190298858254468163979990465970008170029631237738134208413079145118398'+'0570985'
assert len(sh501)==207
sh=tr[:500]+sh501   # 1-500 identical to true pi (Shanks correct to 527)
assert sh[:527]==tr[:527] and sh[527]!=tr[527]
SRC="Shanks 1873 (Proc. R. Soc. 21:319) via engert.us/erwin/miscellaneous/William Shanks 707 digits.pdf + mathlair.allfunandgames.ca/shanks.php; true pi: computed (mpmath), cross-checked MacTutor 707 places"
with open('/home/claude/cogwise-studio/studio/beepmelody/episodes/shanks_pi.csv','w',newline='') as f:
  w=csv.writer(f); w.writerow(['decimal','shanks','true','same','source'])
  for i in range(707): w.writerow([i+1,sh[i],tr[i],int(sh[i]==tr[i]),SRC if i in (0,527) else ''])
wrong=[i+1 for i in range(527,707) if sh[i]!=tr[i]]; lucky=[i+1 for i in range(527,707) if sh[i]==tr[i]]
print(len(wrong),len(lucky),lucky)
# tally digits used
F=ImageFont.truetype('/home/claude/cogwise-studio/studio/this-melody-is/engine/vt323.ttf',30)
FS=ImageFont.truetype('/home/claude/cogwise-studio/studio/this-melody-is/engine/vt323.ttf',24)
BG=(18,22,30); G=(120,230,140); R=(255,80,80); Y=(255,205,80); C=(235,230,210); D=(120,130,150)
per=30; rows=list(range(500,707,per))
H=90+len(rows)*72+40
im=Image.new('RGB',(720,H),BG); d=ImageDraw.Draw(im)
d.text((20,14),"DECIMALS 501-707",font=F,fill=C)
d.text((20,48),"top: SHANKS 1873   bottom: TRUE PI",font=FS,fill=D)
y=90
for r in rows:
  d.text((4,y+10),f"{r+1}",font=FS,fill=D)
  for k in range(per):
    i=r+k
    if i>=707: break
    x=62+k*21.5
    col = G if i<527 else (Y if sh[i]==tr[i] else R)
    d.text((x,y),sh[i],font=F,fill=col)
    d.text((x,y+30),tr[i],font=F,fill=(G if i<527 else C))
  y+=72
d.text((20,y+4),"green = right  red = wrong  gold = right by luck",font=FS,fill=D)
im.save('card/diff.png')
