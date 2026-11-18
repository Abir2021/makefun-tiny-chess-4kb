import json,os,sys,urllib.request
U=os.environ.get("MAKEFUN_ENV_URL")
if not U:sys.exit("MAKEFUN_ENV_URL is not set")
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":0}
K=(-17,-15,-10,-6,6,10,15,17);D=(-17,-16,-15,-1,1,15,16,17)
def post(p,x):
 q=urllib.request.Request(U+p,data=json.dumps(x).encode(),headers={"content-type":"application/json"})
 with urllib.request.urlopen(q) as r:return json.load(r)
def hit(b,s,w):
 for d in ((15,17) if w else (-15,-17)):
  z=s+d
  if not z&136 and b[z]==("P" if w else "p"):return 1
 for d in K:
  z=s+d
  if not z&136 and b[z]==("N" if w else "n"):return 1
 for d in D:
  z=s+d;n=1
  while not z&136:
   p=b[z]
   if p!="#":
    if p!=".":
     if p.isupper()==w and (p.lower()=="q" or p.lower()=="k" and n==1 or p.lower()=="b" and abs(d) in (15,17) or p.lower()=="r" and abs(d) in (1,16)):return 1
     break
   z+=d;n+=1
 return 0
def move(b,w,ep,s,z,p):
 a=list(b);m=a[s];a[s]="."
 if m.lower()=="p" and z==ep and z-s not in (-16,16) and a[z]==".":a[z+(16 if w else -16)]="."
 a[z]=p or m
 if m.lower()=="k" and abs(z-s)==2:
  x,y=(119,117) if z>s and w else (112,115) if w else (7,5) if z>s else (0,3)
  a[y]=a[x];a[x]="."
 e=(s+z)//2 if m.lower()=="p" and abs(z-s)==32 else -1
 return "".join(a),not w,e
def gen(b,w,ep):
 out=[]
 for s in range(128):
  if s&136:continue
  p=b[s]
  if p in ".#" or p.isupper()!=w:continue
  t=p.lower()
  if t=="p":
   d=-16 if w else 16;z=s+d
   if b[z]==".":
    out.append((s,z,"Q" if w and z<8 else "q" if not w and z>=112 else ""))
    zz=z+d
    if (s>>4)==(6 if w else 1) and b[zz]==".":out.append((s,zz,""))
   for d in (d-1,d+1):
    z=s+d
    if not z&136 and (b[z] not in ".#" and b[z].isupper()!=w and b[z].lower()!="k" or z==ep):
     out.append((s,z,"Q" if w and z<8 else "q" if not w and z>=112 else ""))
  else:
   ds=K if t=="n" else D if t in "kq" else (-17,-15,15,17) if t=="b" else (-16,-1,1,16)
   for d in ds:
    z=s+d
    while not z&136:
     if b[z]=="#":break
     if b[z]==".":
      out.append((s,z,""))
     else:
      if b[z].isupper()!=w and b[z].lower()!="k":out.append((s,z,""))
      break
     if t in "nk":break
     z+=d
 return out
def legal(b,w,ep):
 out=[]
 for s,z,p in gen(b,w,ep):
  x=move(b,w,ep,s,z,p)
  if not hit(x[0],x[0].index("K" if w else "k"),not w):out.append((s,z,p,*x))
 return out
def ev(b):
 return sum((1 if p.isupper() else -1)*V[p.lower()] for p in b if p not in ".#")
def search(b,w,ep,d,a,beta,ply):
 ls=legal(b,w,ep)
 if not ls:return -30000+ply if hit(b,b.index("K" if w else "k"),not w) else 0
 if d==0:return (ev(b) if w else -ev(b))
 ls.sort(key=lambda m:V.get(b[m[1]].lower(),0)+(800 if m[2] else 0),reverse=True)
 best=-32000
 for s,z,p,x,n,e in ls:
  v=-search(x,n,e,d-1,-beta,-a,ply+1)
  if v>best:best=v
  if v>a:a=v
  if a>=beta:break
 return best
def choose(fen,us):
 f=fen.split();b=["#"]*128
 for r,row in enumerate(f[0].split("/")):
  c=0
  for p in row:
   if p.isdigit():c+=int(p)
   else:b[r*16+c]=p;c+=1
 b="".join(b);w=f[1]=="w"
 ep=(8-int(f[3][1]))*16+ord(f[3][0])-97 if f[3]!="-" else -1
 best=us[0];score=-32000
 for u in sorted(us):
  s=(8-int(u[1]))*16+ord(u[0])-97;z=(8-int(u[3]))*16+ord(u[2])-97
  p=u[4].upper() if len(u)>4 and w else u[4] if len(u)>4 else ""
  x,n,e=move(b,w,ep,s,z,p)
  v=-search(x,n,e,2,-32000,32000,1)
  if v>score:best,score=u,v
 return best
while True:
 g=post("/game",{})
 if g["status"]=="done":break
 while g["status"]=="your_move":g=post("/move",{"game":g["game"],"move":choose(g["fen"],g["legal_moves"])})
