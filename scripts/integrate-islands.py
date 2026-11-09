from pathlib import Path
import json,hashlib
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import LineString,mapping
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];src=P/'data/raw/north-island/north_island.zip'
g=gpd.read_file('zip://'+str(src));assert len(g)==4 and g.is_valid.all()
tr=Transformer.from_crs(g.crs,'EPSG:4326',always_xy=True)
tr.transform(121.78,25.19)
operation=tr.get_last_used_operation()
names={'10017010S04':'基隆嶼','10017010S01':'彭佳嶼','10017010S02':'棉花嶼','10017010S03':'花瓶嶼'}
a=g.to_crs(4326);features=[]
for _,r in a.iterrows():
 features.append({'type':'Feature','properties':{'name':names[r.VILLCODE],'code':r.VILLCODE,'source':'內政部國土測繪中心 村里界圖(TWD97經緯度)，使用者提供子集','source_url':'https://data.gov.tw/dataset/7438','license':'政府資料開放授權條款-第1版','name_method':'依地理位置對照島嶼名稱；原屬性無島名','area_m2':round(gpd.GeoSeries([r.geometry],crs=4326).to_crs(3826).area.iloc[0],1)},'geometry':mapping(r.geometry)})
fc={'type':'FeatureCollection','features':features};(P/'data/islands.geojson').write_text(json.dumps(fc,ensure_ascii=False));(P/'data/islands.js').write_text('window.ISLANDS='+json.dumps(fc,ensure_ascii=False,separators=(',',':'))+';')
u=unary_union(a.geometry);f=P/'data/map-data.js';d=json.loads(f.read_text().split('=',1)[1].rstrip(';'));before=len(d['contours']);clipped=[];intersects=0
for c in d['contours']:
 line=LineString(c['points']);intersects+=int(line.intersects(u));cut=line.difference(u)
 for l in (list(cut.geoms) if hasattr(cut,'geoms') else [cut]):
  if l.geom_type=='LineString' and not l.is_empty and len(l.coords)>1:clipped.append({'level':c['level'],'points':list(l.coords)})
d['contours']=clipped;f.write_text('window.MAP_DATA='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';')
qa={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_crs_wkt':g.crs.to_wkt(),'display_crs':'EPSG:4326','transform':operation.description,'transform_accuracy_m':operation.accuracy,'coordinate_epoch':'PRJ名稱含2020，未提供觀測epoch；未做板塊運動或公分級校正','features':[{**x['properties'],'geometry_type':x['geometry']['type']} for x in features],'all_valid':bool(a.is_valid.all()),'contour_segments_before':before,'source_contours_intersecting_islands':intersects,'contour_segments_after':len(clipped),'provenance':'使用者提供四島子集，來源dataset7438，內政部國土測繪中心，政府資料開放授權條款第1版。測製日期與精度未附。面屬性為未編定村里，呈現為提供的島嶼陸地面，不宣稱即時潮位岸線。'}
(P/'evidence/islands-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False,indent=2))
