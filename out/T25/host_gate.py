"""Read-only shared IT13 runner admission; never stop or reconfigure runners."""
import json,subprocess,time
def runner_state():
 try:
  rows=json.loads(subprocess.check_output(['gh','api','repos/diegoami/goal2/actions/runners'],text=True,stderr=subprocess.DEVNULL,timeout=4))['runners']
  local=[{k:r[k] for k in ['name','status','busy']} for r in rows if 'it13' in r['name'].lower()]
  return dict(time=time.time(),known=bool(local),busy=not local or any(r['busy'] for r in local),runners=local)
 except (subprocess.SubprocessError,OSError,ValueError,KeyError) as exc:
  return dict(time=time.time(),known=False,busy=True,error=type(exc).__name__,runners=[])
def idle():
 r=runner_state();return r['known'] and not r['busy']
def wait_idle():
 while not idle():print('WAIT FOR IDLE IT13 RUNNERS',flush=True);time.sleep(10)
