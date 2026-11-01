//! motion.update_player8AE9, accepted2cbeb36f. Immediate frame/captured linear addresses.
use crate::host::{Host,Reg};
use crate::mem::lin;
#[derive(Clone,Copy)]
pub struct Saved{pub bp:u16,pub off:u16,pub seg:u16,pub rec:u32,pub code:u32,pub ax:u16,pub kept:u8}
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase{Start,Handler,Run,AtBall,Comment,Take,Sprite}
pub struct Request{pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action{Call(Request),Done(Option<u16>)}
fn ds8<H:Host>(h:&mut H,off:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),off))}
fn ds16<H:Host>(h:&mut H,off:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),off))}
fn regs<H:Host>(h:&mut H,ax:u16,dx:Option<u16>)->Result<(),H::Err>{h.set_reg(Reg::Ax,ax as u32)?;if let Some(dx)=dx{h.set_reg(Reg::Dx,dx as u32)?;}Ok(())}
fn lo(ax:u16,al:u8)->u16{(ax&0xff00)|al as u16}
fn call(s:Saved,next:Phase,target:&'static str,ret:&'static str,args:Vec<u16>,far:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to:ret,args,far})}
fn end<H:Host>(h:&mut H,value:Option<u16>,mutant:bool)->Result<Action,H::Err>{
 if mutant{let at=h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;let old=h.u16(at)?;h.write(at,&(old^1).to_le_bytes(),lin(h.seg(0x214b),0))?;}
 Ok(Action::Done(value))
}
fn run(s:Saved)->Action{call(s,Phase::Run,"0791:8889","0791:8BB7",vec![s.bp],false)}
fn sprite<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{regs(h,s.ax,None)?;Ok(call(s,Phase::Sprite,"0791:8537","0791:8C35",vec![s.seg,s.off],true))}
fn take<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{regs(h,s.ax,None)?;Ok(call(s,Phase::Take,"0791:869F","0791:8C26",vec![s.seg,s.off],true))}
fn after_run<H:Host>(h:&mut H,mut s:Saved)->Result<Action,H::Err>{
 s.ax=u16::from(h.u8(s.rec+0xf)?<5);let old=h.u16(s.rec+0x14)?;
 h.write(s.rec+0x14,&old.wrapping_add(s.ax).to_le_bytes(),lin(h.seg(0x0791),0x8bcc))?;
 if ds8(h,0x8302)?!=0{s.ax=h.u8(s.rec+6)? as u16;}
 if ds8(h,0x8302)?!=0{
  let slot=h.u8(s.rec+6)?;let held=ds8(h,0x830d)?;
  if slot==held{regs(h,s.ax,None)?;return Ok(call(s,Phase::AtBall,"0791:2CEC","0791:8BED",vec![s.seg,s.off],true));}
 }sprite(h,s)
}
fn after_at<H:Host>(h:&mut H,mut s:Saved)->Result<Action,H::Err>{
 if s.ax&255!=0&&h.u8(s.rec+0x12)?!=0x0c{
  s.kept=ds8(h,0x8303)?;let slot=ds8(h,0x830d)?;
  h.write(lin(h.ds(),0x830c),&[slot],lin(h.seg(0x0791),0x8c04))?;
  s.ax=lo(s.ax,ds8(h,0x830b)?);
  let current=ds8(h,0x830b)?;let held=ds8(h,0x830d)?;
  if current!=held&&ds8(h,0x8303)?==0{
   s.ax=lo(s.ax,0x19);regs(h,s.ax,None)?;return Ok(call(s,Phase::Comment,"0791:2AD4","0791:8C1D",vec![s.ax],false));
  }return take(h,s);
 }sprite(h,s)
}
pub fn step<H:Host>(h:&mut H,phase:Phase,saved:Option<Saved>,sent:u16,mutant:bool)->Result<Action,H::Err>{
 if phase==Phase::Start{
  let bp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(bp as u32)?;let old=h.reg(Reg::Bp)? as u16;
  h.write(at,&old.to_le_bytes(),lin(h.seg(0x0791),0x8ae9))?;
  h.set_reg(Reg::Sp,bp as u32)?;h.set_reg(Reg::Bp,bp as u32)?;h.set_reg(Reg::Sp,bp.wrapping_sub(6) as u32)?;
  // Frame.lin once, then contiguous farptr reads: second word does not rewrap SS.
  let at=h.ss_lin(bp.wrapping_add(6) as u32)?;let off=h.u16(at)?;let seg=h.u16(at+2)?;let rec=lin(seg,off);
  let idx=h.u16(rec+0xd)?;let product=idx as u32*20;let ax=product as u16;let dx=(product>>16) as u16;
  let poff=ds16(h,0xa91b)?;let pseg=ds16(h,0xa91d)?;let code=lin(pseg,poff.wrapping_add(ax));
  let state=h.u8(rec+0x12)?;regs(h,lo(ax,state),Some(dx))?;
  let s=Saved{bp,off,seg,rec,code,ax,kept:0};
  let target=match state{
   5=>Some(("0791:57AC","0791:8B1B")),13=>Some(("0791:58E1","0791:8B2B")),1=>Some(("0791:69BD","0791:8B3B")),
   2=>Some(("0791:6AAD","0791:8B4A")),3=>Some(("0791:6AF7","0791:8B59")),6=>Some(("0791:6240","0791:8B68")),
   7=>Some(("0791:7069","0791:8B77")),8=>Some(("0791:7287","0791:8B86")),9=>Some(("0791:715A","0791:8B95")),
   10=>Some(("0791:73BA","0791:8BA4")),11=>Some(("0791:7621","0791:8BB3")),_=>None,
  };
  return Ok(if let Some((target,ret))=target{call(s,Phase::Handler,target,ret,vec![seg,off],true)}else{run(s)});
 }
 let mut s=saved.unwrap();
 match phase{
  Phase::Handler=>Ok(run(s)),
  Phase::Run=>after_run(h,s),
  Phase::AtBall=>{s.ax=sent;after_at(h,s)}
  Phase::Comment=>{s.ax=sent;take(h,s)}
  Phase::Take=>{
   s.ax=sent;h.write(lin(h.ds(),0x8303),&[s.kept],lin(h.seg(0x0791),0x8c29))?;
   s.ax=lo(s.ax,s.kept);sprite(h,s)
  }
  Phase::Sprite=>{
   if ds8(h,0x8325)?!=0&&h.u16(s.rec+0x14)?>0xb4{
    if (h.u8(s.code+0xe)? as i8)>1{let b=h.u8(s.code+0xe)?;h.write(s.code+0xe,&[b.wrapping_sub(1)],lin(h.seg(0x0791),0x8c54))?;}
    h.write(s.rec+0x14,&0u16.to_le_bytes(),lin(h.seg(0x0791),0x8c5d))?;return end(h,Some(0),mutant);
   }end(h,None,mutant)
  }
  Phase::Start=>unreachable!(),
 }
}
