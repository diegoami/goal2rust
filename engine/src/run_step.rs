//! pilot.player_run_step 0791:8889 and its inline helpers, accepted 2cbeb36f.
//! There are no guest calls, frame prologue, or register assignments in this body.
use crate::host::Host;
use crate::mem::lin;
fn s8(b:u8)->i32{b as i8 as i32}
fn ds8<H:Host>(h:&mut H,o:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),o))}
fn ds16<H:Host>(h:&mut H,o:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),o))}
fn write<H:Host>(h:&mut H,a:u32,b:&[u8],seg:u16,off:u16)->Result<(),H::Err>{h.write(a,b,lin(h.seg(seg),off))}
fn byte<H:Host>(h:&mut H,a:u32,b:u8,site:u16)->Result<(),H::Err>{write(h,a,&[b],0x0791,site)}
fn side<H:Host>(h:&mut H,rec:u32)->Result<u16,H::Err>{Ok(u16::from(h.u8(rec+6)?<12))}
fn attack<H:Host>(h:&mut H,rec:u32)->Result<i32,H::Err>{
 let half=s8(ds8(h,0x8319)?);let left=ds16(h,0x831b)? as i32;let flag=u16::from(half<0||left>half);let idx=flag^side(h,rec)?;
 Ok(s8(ds8(h,0x7920+idx)?))
}
fn member<H:Host>(h:&mut H,base:u32,e:u8)->Result<bool,H::Err>{Ok(h.u8(base+(e>>3) as u32)?&(1<<(e&7))!=0)}
fn random<H:Host>(h:&mut H,n:u32)->Result<u8,H::Err>{
 let off=ds16(h,0xa978)?;let seg=ds16(h,0xa97a)?;let at=lin(seg,off);let old=h.u16(at)?;
 let new=old.wrapping_mul(0x7abd).wrapping_add(0x1b0f);write(h,at,&new.to_le_bytes(),0x214b,0x069f)?;
 Ok((((new as u32*n)>>16)+1) as u8)
}
fn can_move<H:Host>(h:&mut H,rec:u32)->Result<bool,H::Err>{
 let old=h.u16(rec+2)?;write(h,rec,&old.to_le_bytes(),0x0791,0x86f0)?;
 let f=h.u8(rec+0xf)?;
 match f{
  1=>{let b=h.u8(rec)?;byte(h,rec,b.wrapping_sub(1),0x8711)?;}
  2=>{let b=h.u8(rec)?;byte(h,rec,b.wrapping_add(1),0x8725)?;}
  3=>{let b=h.u8(rec+1)?;byte(h,rec+1,b.wrapping_sub(1),0x8739)?;}
  4=>{let b=h.u8(rec+1)?;byte(h,rec+1,b.wrapping_add(1),0x874e)?;}
  _=>{}
 }
 if h.u8(rec+0xf)?==5{return Ok(true);}
 let pos=h.u16(rec)?;if s8(pos as u8).abs()>8||s8((pos>>8) as u8).abs()>0x25{return Ok(false);}
 if ds8(h,0x8325)?==0{return Ok(true);}
 let slot=h.u8(rec+6)?;if slot==ds8(h,0x830c)?||slot==ds8(h,0x830b)?{return Ok(true);}
 let poff=ds16(h,0xa91b)?;let pseg=ds16(h,0xa91d)?;let player=h.u16(rec+0xd)?;
 if h.u8(lin(pseg,poff.wrapping_add(player.wrapping_mul(20)))+6)?==0{return Ok(true);}
 let boff=ds16(h,0x7c16)?;let bseg=ds16(h,0x7c18)?;
 let row=s8(h.u8(rec)?);let col=s8(h.u8(rec+1)?);
 let cell=boff.wrapping_add((row*160) as u16).wrapping_add((col*2) as u16);
 if h.u8(lin(bseg,cell.wrapping_add(0x90f)))?==0x0d{return Ok(true);}
 let ch=h.u8(lin(bseg,cell.wrapping_add(0x90e)))?;
 Ok(!member(h,lin(h.ds(),0x648),ch)?)
}
pub fn run<H:Host>(h:&mut H,mutant:u32)->Result<(),H::Err>{
 // mem.arg(0), then one Frame.lin for the parent's contiguous far pointer.
 let a=h.ss_lin(h.entry().0+2)?;let parent=h.u16(a)?;
 let a=h.ss_lin(parent as u32+6)?;let off=h.u16(a)?;let seg=h.u16(a+2)?;let rec=lin(seg,off);
 let mut skip=false;
 if ds8(h,0x8302)?!=0{
  let row=s8(h.u8(rec+1)?);let own=row*attack(h,rec)?;
  let row=s8(ds8(h,0x82f7)?);let ball=row*attack(h,rec)?;
  if ball>own{skip=true;}
 }
 if !skip{let slot=h.u8(rec+6)?;if slot==ds8(h,0x830b)?||slot==ds8(h,0x830c)?{skip=true;}}
 if !skip{let a=attack(h,rec)?>0;let c=s8(h.u8(rec+8)?)>0;if a!=c{skip=true;}}
 if !skip{
  let idx=if side(h,rec)?==0{1}else{0};let line=s8(ds8(h,0x82e3+6*idx)?).abs();
  if s8(h.u8(rec+8)?).abs()>=line{
   let state=h.u8(rec+0x12)?;
   if member(h,lin(h.seg(0x0791),0x8869),state)?{
    let slot=h.u8(rec+6)?;
    if slot!=1&&slot!=12{
     let d=attack(h,rec)?;let idx=if side(h,rec)?==0{1}else{0};let line=s8(ds8(h,0x82e3+6*idx)?);
     byte(h,rec+8,(line-d) as u8,0x89e1)?;
    }
   }
  }
 }
 let dx=s8(h.u8(rec+7)?.wrapping_sub(h.u8(rec)?));let dy=s8(h.u8(rec+8)?.wrapping_sub(h.u8(rec+1)?));
 let pos=h.u16(rec)?;let target=h.u16(rec+7)?;
 if pos==target{byte(h,rec+0xf,5,0x8a26)?;}
 else{
  let coin=random(h,2)?==1;
  let (direction,site)=if coin{
   if dx.abs()>0{(u8::from(dx>0)+1,0x8a5b)}else{(u8::from(dy>0)+3,0x8a79)}
  }else if dy.abs()>0{(u8::from(dy>0)+3,0x8aa5)}else{(u8::from(dx>0)+1,0x8ac1)};
  byte(h,rec+0xf,direction,site)?;
 }
 while !can_move(h,rec)?{let d=random(h,5)?;byte(h,rec+0xf,d,0x8add)?;}
 if mutant==24{let a=h.ss_lin(h.entry().0.wrapping_sub(2))?;let old=h.u16(a)?;write(h,a,&(old^1).to_le_bytes(),0x214b,0)?;}
 if mutant==25{let pos=h.u16(rec)?;write(h,rec,&(pos^0x8000).to_le_bytes(),0x214b,0)?;}
 Ok(())
}
