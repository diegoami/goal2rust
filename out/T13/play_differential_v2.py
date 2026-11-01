"""Keep v1 immutable; error probes need unmutated tables to reach point-query sites."""
from pathlib import Path
p=Path('out/T13/play_differential.py');s=p.read_text();assert s.count('case,failure=failure,mutations=True')==2
s=s.replace('case,failure=failure,mutations=True','case,failure=failure,mutations=False')
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
