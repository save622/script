import subprocess,re,sys,json
sys.path.insert(0,'.')
import content as C
TH=str.maketrans('0123456789','๐๑๒๓๔๕๖๗๘๙')
pdf=sys.argv[1]
n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
txt=[re.sub(r'\s+',' ',subprocess.run(['pdftotext','-f',str(p),'-l',str(p),pdf,'-'],capture_output=True,text=True).stdout) for p in range(1,n+1)]
start=next(i for i,t in enumerate(txt) if C.BODY[0][1] in t and 'สารบัญ' not in t)
res={'TITLE':'๑'}
for h in [x[1] for x in C.BODY if x[0]=='h1']:
    i=next(i for i in range(start,n) if h in txt[i]); res[h]=str(i-start+1).translate(TH)
i=next(i for i in range(start,n) if txt[i].strip().split(' ')[-1:] and 'บรรณานุกรม' in txt[i][:40]); res['BIB']=str(i-start+1).translate(TH)
i=next(i for i in range(start,n) if txt[i].strip().endswith('ภาคผนวก') or re.match(r'^\s*\d+\s*ภาคผนวก\s*$',txt[i])); res['APP']=str(i-start+1).translate(TH)
json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False); print(res, 'bodystart pdf page', start+1, 'total', n)
