"""Re-run preserved tree producers with the new pinned state-v2 evidence module."""
import argparse,runpy,sys
import evidence as e
ap=argparse.ArgumentParser();ap.add_argument('--suite',choices=['availability','ball','skill'],required=True)
ap.add_argument('--mutant',type=int,default=0);ap.add_argument('--out',required=True);a=ap.parse_args()
e.verify()
source={'availability':'T04','ball':'T05','skill':'T06'}[a.suite]
sys.argv=['differential.py','--out',a.out,'--mutant',str(a.mutant)]
print('Preserved suite',a.suite,'control',a.mutant,flush=True)
runpy.run_path(str(e.BASE/'out'/source/'differential.py'),run_name='__main__')
