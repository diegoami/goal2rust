"""Bind preserved producers through the explicit v2 evidence-source manifest."""
import runpy,sys
import evidence_v2
sys.modules['evidence']=evidence_v2
script=sys.argv[1];sys.argv=sys.argv[1:]
runpy.run_path(str(evidence_v2.BASE/'out/T18'/script),run_name='__main__')
