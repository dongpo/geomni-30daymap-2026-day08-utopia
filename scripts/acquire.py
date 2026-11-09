from pathlib import Path
import requests,json,time,concurrent.futures,datetime
O=Path(__file__).resolve().parents[1];raw=O/'data/raw';log=[]
def get(job):
 name,url=job;t=time.time()
 try:
  r=requests.get(url,timeout=70);r.raise_for_status();(raw/name).write_bytes(r.content);return {'file':name,'url':url,'bytes':len(r.content),'seconds':round(time.time()-t,2),'status':'OK'}
 except Exception as e:return {'file':name,'url':url,'status':'FAILED','error':str(e)}
base='https://portal.taibif.tw/api/v3/occurrence?taxonGroup=Fishes&boundedBy=121.4,25.0,122.4,25.9&rows=1000&offset='
jobs=[(f'fish-{i:05}.json',base+str(i)) for i in range(1000,27000,1000)]
jobs += [('divesites.pdf','https://www.penghu.gov.tw/uploaddowndoc?file=report%2F202509190851032.pdf&filedisplay=3270308_0023451_114E1003167-01.pdf&flag=doc'),('ecology2024.pdf','https://www.oca.gov.tw/filedownload?file=research%2F202503121409200.pdf&filedisplay=112-113OCA_ClosureReprot_compressed.pdf&flag=doc'),('reefs-survey.pdf','https://kmweb.moa.gov.tw/files/document/8333/f7b32edc2f930641e08c93ea1b112122_v2.pdf')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for result in ex.map(get,jobs):log.append(result);print(result['file'],result['status'],flush=True)
(O/'evidence/acquisition.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requests':log},ensure_ascii=False,indent=2))
