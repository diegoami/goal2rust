"""Resume canonical keys-v3 receipts and retain the failed jobs-v1 log unchanged."""
from pathlib import Path
p=Path('out/T10/supervise.py')
s=p.read_text().replace("jobs-v1.jsonl","jobs-v3.jsonl").replace("name=f'keys-{label}-v1'","name=f'keys-{label}-v3'").replace("'keys_differential.py'","'keys_differential_v3.py'")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
