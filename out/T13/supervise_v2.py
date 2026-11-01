"""Current canonical play-v2 proof, failed preflight journal retained separately."""
from pathlib import Path
p=Path('out/T13/supervise.py');s=p.read_text().replace('jobs-v1.jsonl','jobs-v2.jsonl').replace("name=f'play-{label}-v1'","name=f'play-{label}-v2'").replace("'play_differential.py'","'play_differential_v2.py'")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
