"""Common bridge fast-path parity, fallbacks and callback mutation."""
import functools,unittest
from original_match.port.engine import PortMachine as Oracle
from goal2rust.machine import PortMachine


def trial(cls,fast=True):
    m=cls(bytes(range(256))*(0x110000//256),0x823,fast=fast) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
    mem=m.port_memory();events=[];values=[]
    m.io_tap=lambda *x:events.append(('io',x))
    m.write_tap=lambda *x:events.append(('direct-write',x))
    class Tap:
        def listen_enter(self,*x):events.append(('enter',x));return len(events)
        def listen_leave(self,x):events.append(('leave',x))
    m.listen_tap=Tap()
    added=[False]
    def first(a,n,v):
        events.append(('write',a,n,v,m.pc()))
        if not added[0]:
            m.on_write(16,32,lambda *x:events.append(('new',x)));added[0]=True
        # Hooks may change tap installation; no cached tap values may survive.
        m.io_tap=None if m.io_tap is not None else lambda *x:events.append(('new-io',x))
    m.on_write(16,32,first)
    for pos in [0,16,31,0x10fffe,0x10ffff,-1,0x110000,True]:
        for size in [1,2]:
            try:values.append(('read',pos,size,(mem.u8 if size==1 else mem.u16)(pos)))
            except Exception as e:values.append(('error',type(e).__name__,str(e)))
    for n in [0,1,2,3,4,5,8,9,16]:
        for v in [0,1,-1,0x12345678,2**64-1,-2**127,2**200+7]:
            try:m.write_as(16,n,v,0x1234)
            except Exception as e:values.append(('write-error',type(e).__name__,str(e)))
    for name in ['eax','AX','ah','al','sp','IP','FLAGS','eflags','ss','no-such']:
        for v in [0,-1,2**80+0x1234]:
            try:m.set_reg(name,v);values.append(('reg',name,m.reg(name)))
            except Exception as e:values.append(('reg-error',type(e).__name__,str(e)))
    for n in [1,2,8,9]:
        def fail(a,n,v):raise ValueError('bridge callback refused')
        m._writes.clear();m._writes_now=();m._writes_span=(1,0);m.on_write(16,32,fail)
        try:m.write_as(16,n,-1,0x1234)
        except Exception as e:values.append(('callback-error',type(e).__name__,str(e)))
    m.io_tap=m.write_tap=None
    return m.snapshot(),values,events,getattr(m._core,'bridge_fast_calls',None) if cls is PortMachine else None


class BridgeFastTests(unittest.TestCase):
    def test_exact_state_events_and_fast_path_coverage(self):
        p=trial(Oracle);slow=trial(PortMachine,False);fast=trial(PortMachine,True)
        self.assertEqual(p[:3],slow[:3]);self.assertEqual(p[:3],fast[:3])
        self.assertGreater(fast[3]['u8'],0);self.assertGreater(fast[3]['u16'],0);self.assertGreater(fast[3]['write'],0)
        self.assertTrue(all(v==0 for v in slow[3].values()))

    def test_read_fallbacks_and_resized_buffer(self):
        machines=[Oracle(bytes(range(256))*(0x110000//256),0x823),PortMachine(bytes(range(256))*(0x110000//256),0x823,fast=False),PortMachine(bytes(range(256))*(0x110000//256),0x823,fast=True)]
        outputs=[]
        for m in machines:
            mem=m.port_memory();out=[]
            class Index:
                def __index__(self):out.append('index');return 4
                def __add__(self,n):out.append(('add',n));return 4+n
                def __str__(self):return 'index-object'
            # Preserve baseline Rust fallback behavior even for non-reference extension types.
            for x in [True,-1,0x110000,2**100,1.5,'4',Index()]:
                try:out.append(mem.u16(x))
                except Exception as e:out.append((type(e).__name__,str(e)))
            m._memory[:]=bytes(range(32))
            for x in [0,30,31,32]:
                try:out.append(mem.u16(x))
                except Exception as e:out.append((type(e).__name__,str(e)))
            outputs.append(out)
        self.assertEqual(outputs[1],outputs[2])
        self.assertEqual(outputs[0][-4:],outputs[2][-4:])

if __name__=='__main__':unittest.main()
