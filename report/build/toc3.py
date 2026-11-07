import subprocess,re,sys,json
sys.path.insert(0,'.')
import content2 as C
TH=str.maketrans('0123456789','๐๑๒๓๔๕๖๗๘๙')
pdf,out=sys.argv[1],sys.argv[2]
info=json.load(open(sys.argv[3]))
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
raw=[subprocess.run(['pdftotext','-f',str(p),'-l',str(p),pdf,'-'],capture_output=True,text=True).stdout for p in range(1,n+1)]
txt=[re.sub(r'\s+','',t) for t in raw]
Z=lambda s: re.sub(r'\s+','',s)
h1=[x[1] for x in C.BODY if x[0]=='h1']
start=next(i for i,t in enumerate(txt) if Z(h1[0]) in t and 'สารบัญ' not in t)
pg=lambda i: str(i-start+1).translate(TH)
res={'TITLE':'๑'}
for h in h1: res[h]=pg(next(i for i in range(start,n) if Z(h) in txt[i]))
res['BIB']=pg(next(i for i in range(start,n) if txt[i][:40].find('บรรณานุกรม')>=0))
res['APP']=pg(next(i for i in range(start,n) if re.fullmatch(r'\s*\S{0,4}\s*ภาคผนวก\s*',raw[i].replace('\x0c',''))))
for x in C.APPENDIX:
    if x[0]=='ah': res[x[2]]=pg(next(i for i in range(start,n) if Z(x[1])[:40] in txt[i]))
for k in info['ORDER']:
    needle=Z('ภาพที่ '+info['NUM'][k]+' '+C.IMGS[k][1])[:24]
    hits=[i for i in range(start,n) if needle in txt[i]]
    res['img:'+k]=pg(hits[0]) if hits else '?'
    if len(hits)!=1: print('WARN',k,len(hits))
json.dump(res,open(out,'w'),ensure_ascii=False); print(res); print('bodystart pdf page',start+1,'total',n)
