from pathlib import Path
import json,time,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];t=time.perf_counter()
f=P/'data/map-data.js';d=json.loads(f.read_text().split('=',1)[1].rstrip(';'));z=np.array(d['grid']);h,w=z.shape
x=np.linspace(121.35+.5/240,122.55-.5/240,w);y=np.linspace(24.9+.5/240,25.9-.5/240,h);zz=z[::-1]
xx=np.linspace(x[0],x[-1],(w-1)*4+1);yy=np.linspace(y[0],y[-1],(h-1)*4+1)
a=np.array([np.interp(xx,x,row) for row in zz]);fine=np.array([np.interp(yy,y,col) for col in a.T]).T
levels=np.arange(np.ceil(float(z.min())/20)*20,1,20)
fig,ax=plt.subplots();cs=ax.contour(xx,yy,fine,levels=levels)
cont=[{'level':int(v),'points':np.round(seg,6).tolist()} for v,segs in zip(cs.levels,cs.allsegs) for seg in segs if len(seg)>2]
plt.close(fig);d['contours']=cont;f.write_text('window.MAP_DATA='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';')
qa={'interval_m':20,'native_grid':[h,w],'native_arcseconds':15,'interpolation':'separable bilinear, 4 subdivisions per native centre interval; contour interpolation on resampled field','interpolated_shape':list(fine.shape),'min_depth_m':float(z.min()),'level_count':len(levels),'segments':len(cont),'vertices':sum(len(c['points']) for c in cont),'native_node_max_error':float(np.max(abs(fine[::4,::4]-zz))),'resampled_extrema':[float(fine.min()),float(fine.max())],'source_sha256':hashlib.sha256((P/'data/bathymetry.xyz').read_bytes()).hexdigest(),'seconds':round(time.perf_counter()-t,3),'note':'20 m is vertical contour interval, not horizontal resolution or accuracy. No added measurements; no extrapolation beyond native grid centres.'}
assert qa['native_node_max_error']<1e-5
assert fine.min()>=z.min()-1e-5 and fine.max()<=z.max()+1e-5
(P/'evidence/contours-20m-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,indent=2))
