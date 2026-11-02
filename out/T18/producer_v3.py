"""Bind preserved producers through the explicit v3 evidence-source manifest."""
import runpy,sys
import evidence_v3
sys.modules['evidence']=evidence_v3
script=sys.argv[1];sys.argv=sys.argv[1:]
runpy.run_path(str(evidence_v3.BASE/'out/T18'/script),run_name='__main__')
