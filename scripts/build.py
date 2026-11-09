from pathlib import Path
import json,glob,re,collections,hashlib,time,sys,datetime
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,LightSource
O=Path(__file__).resolve().parents[1];t=time.perf_counter()
z=np.loadtxt(O/'data/bathymetry.xyz')[:,2].reshape(240,288)
cmap=LinearSegmentedColormap.from_list('sea',['#c3e8c0','#76c5b8','#348e9b','#256277','#163c59','#10283e'])
d=np.maximum(-z,0);rgb=cmap(np.clip(np.log1p(d)/np.log1p(1800),0,1))[:,:,:3]
gy,gx=np.gradient(z);shade=np.clip(.88+(-gx+gy)*.003,.55,1.13);rgb=np.clip(rgb*shade[:,:,None],0,1);rgb[z>=0]=[.74,.77,.64]
Image.fromarray((rgb*255).astype('uint8')).resize((1152,960),Image.Resampling.BICUBIC).save(O/'data/terrain.png')
# Geographic contours are extracted from the actual raster, never invented bathymetry.
fig,ax=plt.subplots();cs=ax.contour(np.linspace(121.3520833333,122.5479166667,288),np.linspace(25.8979166667,24.9020833333,240),z,levels=[-1000,-500,-200,-100,-50,0]);cont=[]
for level,segs in zip(cs.levels,cs.allsegs):
 for seg in segs:
  if len(seg)>2:cont.append({'level':int(level),'points':np.round(seg,6).tolist()})
plt.close(fig)
rows=[]
for p in sorted((O/'data/raw').glob('*fish*.json')):rows+=json.loads(p.read_text())['data']
ref=[r for r in rows if 'Mianhua' in r.get('datasetName','')]
seen=set();use=[];excluded=[]
for r in ref:
 key=r['taibifOccurrenceID'];lon=r['decimalLongitude'];lat=r['decimalLatitude']
 if key in seen:continue
 seen.add(key)
 if not(122.09<lon<122.12 and 25.47<lat<25.50):excluded.append({'id':key,'lon':lon,'lat':lat,'reason':'outside concentrated Mianhua survey cluster; needs verification'});continue
 if r['taxonRank']!='species':continue
 use.append(r)
sites=collections.defaultdict(list)
for r in use:sites[(r['decimalLongitude'],r['decimalLatitude'])].append(r)
ss=[]
for (lon,lat),rs in sites.items():
 species={}
 for r in rs:
  k=r['originalScientificName'];s=species.setdefault(k,{'latin':k,'name':(r['vernacularName'] or k).split(',')[0],'records':0});s['records']+=1
 ss.append({'lon':lon,'lat':lat,'records':len(rs),'species':sorted(species.values(),key=lambda s:-s['records']),'years':sorted({r['year'] for r in rs if r['year']}),'uncertainty_m':sorted({r['coordinateUncertaintyInMeters'] for r in rs if r['coordinateUncertaintyInMeters'] is not None})})
reefs=[]
for r in json.loads((O/'data/raw/artificial-reefs.json').read_text()):
 if r['座標系統']!='WGS-84':continue
 nums=re.findall(r'[NE](\d+)°(\d+)\D+?(\d+(?:\.\d+)?)',r['中心位置經緯度'])
 if len(nums)<2:continue
 vals=[float(a)+float(b)/60+float(c)/3600 for a,b,c in nums];pts=[[vals[i+1],vals[i]] for i in range(0,len(vals)-1,2)]
 lon,lat=np.mean(pts,axis=0)
 if not(121.35<=lon<=122.55 and 24.9<=lat<=25.9):continue
 reefs.append({'name':r['禁漁區名稱'],'lon':float(lon),'lat':float(lat),'points':pts,'type':'reef','depth':r['平均水深'],'date':r['公告日期'],'range':r['範圍'],'geometry':'source polygon' if len(pts)>1 else 'source centre','note':'公告資料定位；非礁體現存位置／狀態調查'+('；石城與另一官方頁座標不一致，待核對' if '石城' in r['禁漁區名稱'] else '')})
wrecks=[{'name':'外木山沉船','lon':121.71759,'lat':25.1654,'type':'wreck','note':'政府潛點名錄代表點；與 GEBCO 陸地格網衝突（+53 m），位置待核，不能認定為已定位沉船'}, {'name':'萬安艦','lon':121.945156,'lat':24.962338,'type':'wreck','note':'政府潛點名錄代表點；未提供沉船輪廓、測量日期與座標基準'}]
report={'acquired_date':'2026-11-09','raw_fish_records':len(rows),'refuge_records':len(ref),'mapped_species_rank_records':len(use),'mapped_sites':len(ss),'mapped_species':len({r['originalScientificName'] for r in use}),'excluded_off_cluster':excluded,'excluded_non_species_rank':len(ref)-len(use)-len(excluded),'reef_features':len(reefs),'wreck_points':len(wrecks),'raster_shape':list(z.shape),'grid_arcseconds':15,'build_seconds':round(time.perf_counter()-t,3)}
stations=[
 {'name':'彭佳嶼','code':'N1','lon':122+4/60+33.6/3600,'lat':25+37/60+26.4/3600,'depth':'3–12 m','habitat':'大型礁岩與圓石；大型藻類覆蓋較多，其次為石珊瑚。','fish':['霓虹雀鯛','鈍頭錦魚','鋸尾鯛','條紋雀鯛','杜氏刺尾鯛'],'fish_note':'2021 第一季優勢魚種，圖 5-3-53；不代表全部魚種'},
 {'name':'花瓶嶼','code':'N2','lon':121+56/60+49.2/3600,'lat':25+25/60+26.4/3600,'depth':'3–11 m','habitat':'高聳礁岩與陡升斷崖；石珊瑚覆蓋較多，並見大型藻類與海綿。','fish':['霓虹雀鯛','鈍頭錦魚','杜氏刺尾鯛','多帶海緋鯉','鋸尾鯛'],'fish_note':'2021 第一季優勢魚種，圖 5-3-54；不代表全部魚種'},
 {'name':'棉花嶼','code':'N3','lon':122+6/60+28.8/3600,'lat':25+28/60+55.2/3600,'depth':'4–12 m','habitat':'岩石礁盤、礁柱與圓石，間有礫石與粗砂；藻類覆蓋較多，其次為石珊瑚。','fish':[],'fish_note':'附近另有 TaiBIF 2021–2025 逐筆調查紀錄'}]
D={'bounds':[121.35,24.9,122.55,25.9],'grid':z.astype(int).tolist(),'contours':cont,'sites':ss,'reefs':reefs,'wrecks':wrecks,'stats':report,'stations':stations,'grounds':json.loads((O/'data/grounds.json').read_text())}
D['landmarks']=json.loads((O/'data/landmarks.json').read_text())
overrides=json.loads((O/'data/user-feature-overrides.json').read_text())
D['wrecks']=[overrides['corrected_wreck'] if w['name']=='外木山沉船' else w for w in D['wrecks']]
D['reefs'].append(overrides['new_cube_reef'])
(O/'data/map-data.js').write_text('window.MAP_DATA='+json.dumps(D,ensure_ascii=False,separators=(',',':'))+';')
(O/'data/filtered-occurrences.json').write_text(json.dumps(use,ensure_ascii=False))
(O/'evidence/data-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
