//! Speaker/noise data-state tree, accepted 2cbeb36f display94E8/94C9/1E8D and entrypoints0688.
//! Hardware tone/delay stubs remain ordinary visible guest calls.
use crate::host::{Host,Reg,args};
use crate::mem::lin;
use crate::regs::{Regs,sub_flags,CF,PF,AF,ZF,SF,OF};
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase { NoiseStart,NoiseSeedOne,NoiseSeedTwo,NoiseTone,NoiseOff,NoiseDelay,SeedStart,SeedReturn }
pub struct Request {pub next:Phase,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action {Call(Request),Done(Option<u16>)}
fn ds8<H:Host>(h:&mut H,off:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),off))}
fn ds16<H:Host>(h:&mut H,off:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),off))}
fn game<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{
 let off=ds16(h,0xa923)?;let seg=ds16(h,0xa925)?;r.set(Reg::Di,off as u32);r.set(Reg::Es,seg as u32);Ok(())
}
fn speed<H:Host>(h:&mut H,r:&mut Regs)->Result<u8,H::Err>{
 let seg=r.get(h,Reg::Es)?;let off=r.get(h,Reg::Di)?;h.u8(lin(seg,off.wrapping_add(0x3f)))
}
fn request<H:Host>(h:&mut H,r:&mut Regs,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,far:bool)->Result<Action,H::Err>{
 r.store(h,true)?;Ok(Action::Call(Request{next,target,ret_to,args,far}))
}
fn corrupt<H:Host>(h:&mut H)->Result<(),H::Err>{
 let at=h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;let old=h.u16(at)?;h.write(at,&(old^1).to_le_bytes(),lin(h.seg(0x214b),0))
}
fn end<H:Host>(h:&mut H,r:&mut Regs,value:bool,mutant:bool)->Result<Action,H::Err>{
 r.leave(h)?;r.store(h,false)?;
 let out=if value{Some(r.get(h,Reg::Ax)?)}else{None};
 if mutant{corrupt(h)?;}Ok(Action::Done(out))
}
pub fn step<H:Host>(h:&mut H,phase:Phase,mutant:bool)->Result<Action,H::Err>{
 let mut r=Regs::new(!matches!(phase,Phase::NoiseStart|Phase::SeedStart));
 macro_rules! get {($reg:ident)=>{r.get(h,Reg::$reg)?};}
 macro_rules! set {($reg:ident,$v:expr)=>{{let v=$v;r.set(Reg::$reg,v as u32);}};}
 match phase {
  Phase::NoiseStart=>{
   r.enter(h,0)?;
   if ds16(h,0x832a)?>0 {set!(Ax,50);let ax=get!(Ax);return request(h,&mut r,Phase::NoiseSeedOne,"0791:94C9","0791:94F9",vec![ax],false);}
   return request(h,&mut r,Phase::NoiseOff,"214B:1E8D","0791:9532",vec![],true);
  }
  Phase::NoiseSeedOne=>{
   set!(Dx,if get!(Ax)&0x8000!=0{0xffff}else{0});set!(Cx,get!(Ax));set!(Bx,get!(Dx));set!(Ax,ds16(h,0x832a)?);set!(Dx,0);
   let larger=(get!(Dx) as i16)>(get!(Bx) as i16)||(get!(Dx)==get!(Bx)&&get!(Ax)>get!(Cx));
   if larger {
    game(h,&mut r)?;
    if speed(h,&mut r)?>0 {
     set!(Ax,ds16(h,0x832a)?.wrapping_add(300));let ax=get!(Ax);
     return request(h,&mut r,Phase::NoiseSeedTwo,"0791:94C9","0791:9522",vec![ax],false);
    }
   }
   return request(h,&mut r,Phase::NoiseOff,"214B:1E8D","0791:9532",vec![],true);
  }
  Phase::NoiseSeedTwo=>{
   set!(Ax,get!(Ax).wrapping_add(100));let ax=get!(Ax);
   return request(h,&mut r,Phase::NoiseTone,"214B:1EBC","0791:952B",vec![ax],true);
  }
  Phase::NoiseTone|Phase::NoiseOff=>{
   game(h,&mut r)?;let v=speed(h,&mut r)?;r.set_al(h,v)?;r.set_ah(h,0)?;let ax=get!(Ax);
   return request(h,&mut r,Phase::NoiseDelay,"0791:0425","0791:9540",vec![ax],false);
  }
  Phase::NoiseDelay=>return end(h,&mut r,false,mutant),
  Phase::SeedStart=>{
   r.enter(h,2)?;set!(Di,0x8336);
   // Argument BP+4 is evaluated before ss16 flushes its pending stack writes.
   let off=get!(Bp).wrapping_add(4);r.flush(h)?;let at=h.ss_lin(off as u32)?;let n=h.u16(at)?;
   let ds=h.ds();let di=get!(Di);
   return request(h,&mut r,Phase::SeedReturn,"214B:0688","0791:94DC",vec![ds,di,n],true);
  }
  Phase::SeedReturn=>{
   let ax=get!(Ax);r.local16(h,-2,ax as u32)?;return end(h,&mut r,true,mutant);
  }
 }
}
fn add_flags(a:u16,b:u16)->u32 {
 let result=a.wrapping_add(b);let mut f=0;
 if a as u32+b as u32>65535{f|=CF;}
 if (result as u8).count_ones()%2==0{f|=PF;}
 if (a^b^result)&16!=0{f|=AF;}
 if result==0{f|=ZF;}if result&0x8000!=0{f|=SF;}
 if (!(a^b)&(a^result)&0x8000)!=0{f|=OF;}f
}
pub fn rng<H:Host>(h:&mut H,mutant:bool)->Result<(),H::Err>{
 let a=args(h,3)?;let (n,off,seg)=(a[0],a[1],a[2]);let mut r=Regs::new(false);r.enter(h,2)?;let sp=r.get(h,Reg::Sp)?;
 let ds=h.ds();r.push(h,ds as u32)?;r.push(h,seg as u32)?;r.push(h,off as u32)?;
 let at=lin(seg,off);let new=h.u16(at)?.wrapping_mul(0x7abd).wrapping_add(0x1b0f);
 h.write(at,&new.to_le_bytes(),lin(h.seg(0x214b),0x069f))?;
 let high=((new as u32*n as u32)>>16) as u16;let draw=high.wrapping_add(1);
 let step=if h.reg(Reg::Eflags)?&0x400!=0{0xfffe}else{2};
 r.set(Reg::Bx,0x7abd);r.set(Reg::Si,off.wrapping_add(step) as u32);r.set(Reg::Di,off.wrapping_add(step) as u32);r.set(Reg::Es,seg as u32);
 r.set(Reg::Ax,draw as u32);r.set(Reg::Dx,draw as u32);r.arith((add_flags(high,1)&!CF)|if high!=0{CF}else{0});
 r.set(Reg::Sp,sp as u32);r.local16(h,-2,draw as u32)?;r.leave(h)?;r.store(h,false)?;if mutant{corrupt(h)?;}Ok(())
}
pub fn off<H:Host>(h:&mut H,mutant:bool)->Result<(),H::Err>{
 let mut r=Regs::new(false);r.enter(h,0)?;let disabled=ds8(h,0xa9fc)?;r.arith(sub_flags(disabled as u32,0,8));
 if disabled==0{r.set_al(h,0)?;}r.leave(h)?;r.store(h,false)?;if mutant{corrupt(h)?;}Ok(())
}
