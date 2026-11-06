"""Wire the prepared native path only after genuine capture and baseline audit."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[2];O=B/'out/T29'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((O/'capture-input-audit-v1.json').read_text());assert audit['pass_all']
saved=json.loads((O/'baseline-snapshot-v1.json').read_text())
for src,dst in saved['source_map'].items():assert sha(B/src)==sha(B/dst),src
for src,dst in [('prepared_near_zone.rs','engine/src/near_zone.rs'),('test_near_zone.py','engine/tests/test_near_zone.py')]:
 with (B/dst).open('xb') as f:f.write((O/src).read_bytes())
p=B/'engine/src/lib.rs';s=p.read_text();needle='pub mod receiver;';assert s.count(needle)==1;s=s.replace(needle,'pub mod near_zone;\n'+needle);p.write_text(s)
p=B/'engine/src/machine.rs';s=p.read_text()
needle='    Receiver(bool),';assert s.count(needle)==1;s=s.replace(needle,'    NearZone(Option<crate::near_zone::Saved>),\n'+needle)
needle='                "0791:533B"=>Some(NativeContinuation::Receiver(false)),';assert s.count(needle)==1;s=s.replace(needle,'                "0791:44C1"=>Some(NativeContinuation::NearZone(None)),\n'+needle)
needle='                NativeContinuation::Receiver(resumed)=>{';assert s.count(needle)==1
block='''                NativeContinuation::NearZone(saved)=>{
                    let first=saved.is_none();let value=if first{0}else{sent.extract::<u16>()?};
                    let action=crate::near_zone::step(&mut h,saved,value)?;
                    if first{*self.native_calls.borrow_mut().entry("0791:44C1".into()).or_insert(0)+=1;}
                    match action{
                        crate::near_zone::Action::Direction(s)=>{
                            let call=self.call_type.bind(py).call1(("0791:2BE5",(s.seg,s.off),"0791:4500",true,false))?;
                            f.native=Some(NativeContinuation::NearZone(Some(s)));Ok(Some(call.unbind()))
                        }
                        crate::near_zone::Action::Done(mut value)=>{
                            if self.mutant==436{crate::marking::corrupt(&mut h)?;}
                            if (437..444).contains(&self.mutant){
                                let reg=[Reg::Ax,Reg::Cx,Reg::Dx,Reg::Si,Reg::Di,Reg::Es,Reg::Eflags][(self.mutant-437) as usize];
                                if reg==Reg::Ax{value^=0x8000;}else{let old=h.reg(reg)?;h.set_reg(reg,old^if reg==Reg::Eflags{0x400}else{0x8000})?;}
                            }
                            completed_value=value.into_pyobject(py)?.into_any().unbind();Ok(None)
                        }
                    }
                }
'''
s=s.replace(needle,block+needle)
needle='            let corrupt = t28_mutant ||';assert s.count(needle)==1;s=s.replace(needle,'            let t29_mutant=self.mutant==444 && ret_to=="0791:4500";\n            let corrupt = t29_mutant || t28_mutant ||')
p.write_text(s)
print('Near-zone continuation/436body/437..443outputs/444actualfarreturn wired after capture audit')
