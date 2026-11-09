"""Local supplied TBIA snapshot; no external upload or inferred habitat model."""
import csv,io,zipfile,json,hashlib,collections,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]; raw=P/'data/raw/tbia'
z=zipfile.ZipFile(raw/'tbia_6af137d6a272970017cd2db0.zip')
rows=list(csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]),encoding='utf-8-sig')))
surveys={'The Survey Data of Mianhua and Huaping Islets Wildlife Refuge','AI Ocean 數據海洋 海洋公民科學生物資料庫','北方三島（棉花嶼、花瓶嶼、彭佳嶼）調查資料集','示範海域海洋生物資訊蒐集及資源調查-北部海域','Reef Check in Taiwan 台灣珊瑚礁體檢'}
citizens={'iOcean垂釣回報','iOcean海洋生物目擊回報','iNaturalist Research-grade Observations'}
seen=set(); output=[]; reasons=collections.Counter(); datasets=[]; keys={}; audit=[]
for r in rows:
 key=r['id']
 # Do not collapse same species/event coordinates: distinct specimens and rows may be legitimate.
 if key in seen: reasons['duplicate_tbia_id']+=1;continue
 seen.add(key)
 try: x=float(r['standardLongitude']);y=float(r['standardLatitude'])
 except ValueError: reasons['invalid_coordinates']+=1;continue
 try:u=float(r['coordinateUncertaintyInMeters'])
 except ValueError:u=None
 status='context';flags=[]
 if not (121.35<=x<=122.55 and 24.9<=y<=25.9):flags.append('outside_extent')
 if r['dataGeneralizations'].lower()=='true' or r['sensitiveCategory'] not in ('','無'):flags.append('generalized_or_sensitive')
 if r['taxonRank'] not in ('species','subspecies') or r['match_higher_taxon'].lower()=='true':flags.append('not_species_identification')
 if r['datasetName'] in surveys and not flags:
  if abs(x-122.10872)<1e-7 and abs(y-25.37875)<1e-7:flags.append('previously_flagged_station_outlier')
  elif u is not None and 0<=u<=2000 and r['verbatimSRS'].lower() in ('wgs84','epsg:4326'):status='survey'
  else:status='uncertain'
 elif r['datasetName'] in citizens and not flags:status='uncertain'
 else:flags.append('source_not_validated_for_local_habitat')
 if u is not None and u>2000:flags.append('uncertainty_exceeds_max_lens')
 if u is None:flags.append('uncertainty_unknown')
 if not r['verbatimSRS']:flags.append('datum_not_supplied')
 # Do not spatially expose sensitive/generalized observations even for local inspection.
 if 'generalized_or_sensitive' in flags:status='context'
 dk=(r['tbiaDatasetID'],r['license'])
 if dk not in keys:
  keys[dk]=len(datasets);datasets.append({'id':dk[0],'name':r['datasetName'],'license':r['license'],'holder':r['rightsHolder'],'sourceId':r['sourceDatasetID']})
 o={'id':r['id'],'oid':r['occurrenceID'],'lon':x,'lat':y,'u':u,'tier':status,'source':keys[dk],'taxon':r['taxonID'],'latin':r['scientificName'],'name':r['common_name_c'] or r['scientificName'],'date':r['eventDate'],'standardDate':r['standardDate'],'basis':r['basisOfRecord'],'url':r['references'],'flags':flags}
 output.append(o)
 audit.append({'id':r['id'],'tier':status,'reasons':';'.join(flags)})
old=json.loads((P/'data/filtered-occurrences.json').read_text())
oldkeys={str(r['taibifOccurrenceID']) for r in old}
replacement=[r for r in rows if r['sourceDatasetID']=='6b81e881-9d69-48b3-90c1-4154764c9c7c']
qa={'input_rows':len(rows),'columns':len(rows[0]),'unique_tbia_ids':len({r['id'] for r in rows}),'source_datasets':len({r['tbiaDatasetID'] for r in rows}),'county_values':dict(collections.Counter(r['county'] for r in rows)),'scope_note':'Supplied snapshot has only 基隆市 county values; not a census of northern Taiwan. county is TBIA coordinate-derived, not evidence of capture location.','output_rows':len(output),'removed':dict(reasons),'tiers':dict(collections.Counter(r['tier'] for r in output)),'unknown_uncertainty':sum(r['u'] is None for r in output),'uncertainty_8000m':sum(r['u']==8000 for r in output),'generalized_input':sum(r['dataGeneralizations']=='true' for r in rows),'licenses':dict(collections.Counter(r['license'] for r in rows)),'reconciliation':{'old_taibif_selected_rows':len(old),'tbia_same_source_rows':len(replacement),'old_taibif_ids_matched_in_tbia':len(oldkeys & {r['occurrenceID'] for r in replacement}),'policy':'Replace old TaiBIF occurrence display entirely with TBIA snapshot, never union counts. Same-source matching does not assert every field identical.'},'method':'Survey tier requires named marine survey dataset, species/subspecies identification, supplied WGS84 and 0–2000 m uncertainty; uncertain tier includes iOcean, iNaturalist, surveys with missing uncertainty/datum. Uncertain is only a reported coordinate, not a validated habitat. All other sources retained as context-only; no inference of fish absence.'}
for name,x,y in [('huanggang',121.7838,25.3544),('coral',122.1833,25.55)]:
 d=[math.hypot((r['lon']-x)*100.5,(r['lat']-y)*111.2) for r in output]
 qa[name]={'all_source_points_within_2km':sum(v<=2 for v in d),'nearest_supplied_coordinate_km':min(d)}
qa['sources']=[{'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in raw.iterdir() if f.is_file()]
(P/'data/tbia-records.json').write_text(json.dumps({'datasets':datasets,'records':output},ensure_ascii=False))
visible=[r for r in output if r['tier']!='context']
(P/'data/tbia-data.js').write_text('window.TBIA='+json.dumps({'datasets':datasets,'records':visible,'qa':qa},ensure_ascii=False,separators=(',',':'))+';')
(P/'evidence/tbia-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
with (P/'data/tbia-audit.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['id','tier','reasons']);w.writeheader();w.writerows(audit)
print(json.dumps(qa,ensure_ascii=False,indent=2))
