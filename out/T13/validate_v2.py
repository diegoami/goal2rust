"""Accept only complete error-site coverage in play-v2; v1 remains failed history."""
from pathlib import Path
p=Path('out/T13/validate.py');s=p.read_text().replace("'play-'+k+'-v1'","'play-'+k+'-v2'").replace("'play-'+label+'-v1'","'play-'+label+'-v2'").replace('jobs-v1.jsonl','jobs-v2.jsonl')
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
