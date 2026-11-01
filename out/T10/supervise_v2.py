"""Resume canonical keys-v2 receipts and retain the failed jobs-v1 log unchanged."""
from pathlib import Path
p=Path('out/T10/supervise.py')
s=p.read_text().replace("jobs-v1.jsonl","jobs-v2.jsonl").replace("name=f'keys-{label}-v1'","name=f'keys-{label}-v2'").replace("'keys_differential.py'","'keys_differential_v2.py'")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
