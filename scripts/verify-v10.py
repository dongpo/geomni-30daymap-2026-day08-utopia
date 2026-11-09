from pathlib import Path
import json,math
import numpy as np
from pyproj import Geod
P=Path(__file__).resolve().parents[1];data=json.loads((P/'data/tbia-records.json').read_text());rs=data['records'];g=Geod(ellps='WGS84');out={}
assert len(rs)==13894 and len({r['id'] for r in rs})==13894
assert sum(r['tier']=='survey' for r in rs)==7554
assert not any(r['tier']=='survey' and (r['u'] is None or r['u']>2000) for r in rs)
for name,lon,lat in [('huanggang',121.7838,25.3544),('coral',122.1833,25.55),('mianhua',122.108,25.482)]:
 def spherical(r):
  dy=math.radians(r['lat']-lat);dx=math.radians(r['lon']-lon)
  return 12742000*math.asin(math.sqrt(math.sin(dy/2)**2+math.cos(math.radians(lat))*math.cos(math.radians(r['lat']))*math.sin(dx/2)**2))
 results=[]
 for radius in [500,1000,2000]:
  precise=[r for r in rs if r['tier']=='survey' and spherical(r)+r['u']<=radius]
  independently=[r for r in rs if r['tier']=='survey' and g.inv(lon,lat,r['lon'],r['lat'])[2]+r['u']<=radius]
  uncertain=[r for r in rs if r['tier']=='uncertain' and spherical(r)<=radius]
  results.append({'radius_m':radius,'survey_rows':len(precise),'taxon_ids':len({r['taxon'] for r in precise}),'uncertain_rows':len(uncertain),'independent_wgs84_geodesic_count':len(independently),'count_difference':len(precise)-len(independently)})
 assert results[0]['survey_rows']<=results[1]['survey_rows']<=results[2]['survey_rows']
 if name in ['huanggang','coral']:assert results[-1]['survey_rows']==results[-1]['uncertain_rows']==0
 out[name]=results
assert out['mianhua'][-1]['survey_rows']==7199
assert out['mianhua'][-1]['taxon_ids']==242
assert out['mianhua'][-1]['uncertain_rows']==40
cont=json.loads((P/'data/map-data.js').read_text().split('=',1)[1].rstrip(';'))['contours'];assert all(c['level']%20==0 for c in cont)
q=json.loads((P/'evidence/contours-20m-qa.json').read_text());assert q['native_node_max_error']==0
(P/'evidence/v10-numerical-qa.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,indent=2))
