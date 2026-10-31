//! Effective skill, oracle e0270981 geometry278A / attributes3A06.
use crate::host::{args,Host,Reg};
use crate::mem::{lin,cbw};
use crate::regs::Regs;

#[derive(Clone, Copy)]
pub struct Saved { pub off:u16, pub seg:u16, pub element:u16, pub base:u16 }
pub struct Start { pub saved:Saved, pub args:(u16,u16) }
fn ds8<H:Host>(h:&mut H,off:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),off))}
fn rec8<H:Host>(h:&mut H,seg:u16,off:u16,k:u16)->Result<u8,H::Err>{h.u8(lin(seg,off.wrapping_add(k)))}
fn rec16<H:Host>(h:&mut H,seg:u16,off:u16,k:u16)->Result<u16,H::Err>{h.u16(lin(seg,off.wrapping_add(k)))}

pub fn start<H:Host>(h:&mut H)->Result<Start,H::Err>{
    let a=args(h,3)?;let (off,seg,element)=(a[0],a[1],a[2]);
    let mut r=Regs::new(false);r.enter(h,10)?;
    let idx=rec16(h,seg,off,13)?;
    r.set(Reg::Ax,idx as u32);r.set(Reg::Dx,20);
    let product=r.get(h,Reg::Ax)? as u32*20;
    r.set(Reg::Ax,product);r.set(Reg::Dx,product>>16);
    let at=lin(h.ds(),0xa91b);let poff=h.u16(at)?;let pseg=h.u16(at+2)?;
    let pdi=poff.wrapping_add(r.get(h,Reg::Ax)?);
    r.set(Reg::Es,pseg as u32);r.set(Reg::Di,pdi as u32);
    r.local16(h,-10,pdi as u32)?;r.local16(h,-8,pseg as u32)?;
    let form=rec8(h,pseg,pdi,12)?;
    let mut base=if (form as i8)>=32 {r.set(Reg::Ax,0);0} else {
        r.set_al(h,form)?;let al=r.al(h)?;r.set(Reg::Ax,cbw(al) as u32);
        let ax=r.get(h,Reg::Ax)?.wrapping_add(1);r.set(Reg::Ax,ax as u32);r.get(h,Reg::Ax)?
    };
    r.local16(h,-4,base as u32)?;
    if element>=12 {base=base.wrapping_add(32);} else {
        let energy=rec8(h,pseg,pdi,14)?;r.set_al(h,energy)?;
        let al=r.al(h)?;r.set(Reg::Ax,cbw(al) as u32);base=base.wrapping_add(r.get(h,Reg::Ax)?);
    }
    r.local16(h,-4,base as u32)?;r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);r.store(h,true)?;
    Ok(Start{saved:Saved{off,seg,element,base},args:(idx,element)})
}

pub fn resume<H:Host>(h:&mut H,s:Saved,mut skill:u16)->Result<(),H::Err>{
    let mut r=Regs::new(true);let mut base=s.base;
    macro_rules! get {($reg:ident)=>{r.get(h,Reg::$reg)?};}
    macro_rules! set {($reg:ident,$v:expr)=>{{let v=$v;r.set(Reg::$reg,v as u32);}};}
    macro_rules! sal {($v:expr)=>{{let v=$v;r.set_al(h,v)?;}};}
    r.local16(h,-6,skill as u32)?;set!(Es,s.seg);set!(Di,s.off);
    if rec8(h,s.seg,s.off,19)?!=0 {
        set!(Cx,2);set!(Dx,skill%2);skill/=2;set!(Ax,skill);r.local16(h,-6,skill as u32)?;
    }
    set!(Cx,4);set!(Bx,skill/4);set!(Dx,skill%4);set!(Ax,base);
    let product=get!(Ax) as u32*skill as u32;set!(Ax,product);set!(Dx,product>>16);
    set!(Dx,0);set!(Cx,256);let lo=get!(Ax);set!(Ax,lo/256);set!(Dx,lo%256);
    set!(Ax,get!(Ax).wrapping_add(get!(Bx)));base=get!(Ax);r.local16(h,-4,base as u32)?;
    set!(Di,s.element);let mut extra=ds8(h,0x769u16.wrapping_add(s.element))?!=0;
    if !extra && s.element==1 {
        sal!(ds8(h,0x8327)?);let el=r.al(h)?;let sp=get!(Sp);
        let ax=get!(Ax);r.push(h,ax as u32)?;
        let cs=h.seg(0x791);r.push(h,cs as u32)?;r.push(h,0x276a)?;r.push(h,cs as u32)?;r.push(h,0x2841)?;
        set!(Sp,sp);
        let member=(h.u8(lin(h.seg(0x791),0x276au16.wrapping_add((el>>3) as u16)))?>>(el&7))&1;
        set!(Bx,el>>3);set!(Cx,(get!(Cx)&0xff00)|((el&7) as u16));sal!(1u8<<(el&7));
        set!(Es,h.seg(0x791));set!(Di,0x276a);extra=member!=0;
    }
    if extra {
        set!(Es,s.seg);set!(Di,s.off);sal!(rec8(h,s.seg,s.off,17)?);r.set_ah(h,0)?;
        base=base.wrapping_add(get!(Ax));r.local16(h,-4,base as u32)?;
    }
    set!(Es,s.seg);set!(Di,s.off);
    if rec8(h,s.seg,s.off,6)?<12 && ds8(h,0x80fc)?!=0 {
        set!(Ax,base);set!(Dx,0);set!(Cx,16);set!(Ax,base/16);set!(Dx,base%16);
        base=base.wrapping_add(get!(Ax));r.local16(h,-4,base as u32)?;
    }
    set!(Ax,base);r.local16(h,-2,base as u32)?;r.leave(h)?;r.store(h,false)
}

fn arg<H:Host>(h:&mut H,i:u32)->Result<u16,H::Err>{
    let (sp,far)=h.entry();let at=h.ss_lin(sp+if far{4}else{2}+2*i)?;h.u16(at)
}
fn frame_write<H:Host>(h:&mut H,bp:u16,off:i16,value:u16,site:u16)->Result<(),H::Err>{
    let at=h.ss_lin(bp.wrapping_add(off as u16) as u32)?;
    h.write(at,&value.to_le_bytes(),lin(h.seg(0x1771),site))
}

pub fn derived<H:Host>(h:&mut H,mutant:bool)->Result<u16,H::Err>{
    let element=arg(h,0)?;let n=arg(h,1)?;
    // Mem.enter: immediate saved-BP write and real SP/BP/SP updates in source order.
    let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);
    let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)? as u16;
    h.write(at,&bp.to_le_bytes(),lin(h.seg(0x1771),0x3a06))?;
    h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;h.set_reg(Reg::Sp,sp.wrapping_sub(10) as u32)?;
    let ax=(n as u32*20) as u16;
    let at=lin(h.ds(),0xa91b);let poff=h.u16(at)?;let seg=h.u16(at+2)?;let off=poff.wrapping_add(ax);
    frame_write(h,sp,-10,off,0x3a1a)?;frame_write(h,sp,-8,seg,0x3a1d)?;
    let scale=rec8(h,seg,off,4)? as u16+1;frame_write(h,sp,-6,scale,0x3a2c)?;
    let p7=rec8(h,seg,off,7)? as u16;
    let cx=ds8(h,0x6d25u16.wrapping_add((p7*12).wrapping_add(element)))?;
    let p5=rec8(h,seg,off,5)? as u16;
    let t=ds8(h,0x6dcdu16.wrapping_add(p5*12+cx as u16))? as u16;
    frame_write(h,sp,-4,t,0x3a66)?;let product=t.wrapping_mul(scale);let result=product/32;
    // Body control5 changes only this retained local word, not the return value.
    frame_write(h,sp,-2,if mutant{result^1}else{result},0x3a76)?;
    h.set_reg(Reg::Dx,(product%32) as u32)?;Ok(result)
}
