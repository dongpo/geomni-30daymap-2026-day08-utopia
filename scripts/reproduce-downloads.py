from pathlib import Path
import requests,subprocess,json
O=Path(__file__).resolve().parents[1];R=O/'data/raw';R.mkdir(exist_ok=True,parents=True)
jobs=[('artificial-reefs.json','https://data.moa.gov.tw/Service/OpenData/FaRss.aspx?IsTransData=1&UnitId=725&key=015'),('taibif-fishes.json','https://portal.taibif.tw/api/v3/occurrence?taxonGroup=Fishes&boundedBy=121.4,25.0,122.4,25.9&rows=1000')]
for name,url in jobs:
 q=requests.get(url,timeout=90);q.raise_for_status();(R/name).write_bytes(q.content)
for name,file,title in [('traditional-names','202501141656070','NAMR111039東北角海岸及海域傳統地名調查勞務委託案成果報告-已壓縮.pdf'),('northern-survey','202601151547370','示範海域海洋生物資訊蒐集及資源調查-北部海域.pdf')]:
 q=requests.get('https://www.namr.gov.tw/filedownload',params={'file':f'research/{file}.pdf','filedisplay':title,'flag':'doc'},timeout=90);q.raise_for_status();assert q.content.startswith(b'%PDF');(R/(name+'.pdf')).write_bytes(q.content)
subprocess.run(['gdal_translate','-projwin','121.35','25.9','122.55','24.9','/vsicurl/https://data.naturalcapitalalliance.stanford.edu/download/global/gebco/gebco_bathymetry_2024_global.tif',str(O/'data/bathymetry.tif')],check=True)
subprocess.run(['gdal_translate','-of','XYZ',str(O/'data/bathymetry.tif'),str(O/'data/bathymetry.xyz')],check=True)
# Then run acquire.py for remaining fish pages and PDFs, and build.py.
