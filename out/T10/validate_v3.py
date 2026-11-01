"""Final v3 acceptance: completed external-guest ABI coverage, original v1 evidence retained."""
from pathlib import Path
p=Path('out/T10/validate.py')
s=p.read_text().replace("'keys-'+k+'-v1'","'keys-'+k+'-v3'").replace("'keys-'+label+'-v1'","'keys-'+label+'-v3'").replace('jobs-v1.jsonl','jobs-v3.jsonl')
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
