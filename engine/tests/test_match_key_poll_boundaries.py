"""Two unregistered external guest boundaries, modeled only for caller ABI tests."""
import unittest
from original_match.port import Entry
import test_match_key_poll as base
# Source guest calls have no arguments: near1A04 and far16D6:0945. Their bodies
# are absent from the pinned port registry; do not claim Match hooks or execution proof.
# Do not register these entries in any production Registry or claim their bodies ported.
for address,ret in [('0791:1A04','ret'),('16D6:0945','retf')]:
 assert address not in base.ENTRIES
 base.ENTRIES[address]=Entry(address,ret,lambda mem,variant:None,'authored external-guest ABI')

class KeyPollBoundaryTests(unittest.TestCase):
 def test_positive_cases_finish_and_all_boundaries_return(self):
  visited=set();called=set()
  for case in range(26):
   pair=[]
   for cls in [base.Oracle,base.PortMachine]:
    result,_=base.exercise(cls,case)
    self.assertIsNone(result['error'],(case,result['error']))
    pair.append(result)
   self.assertEqual(*pair)
   visited.update(s for s,_ in pair[0]['visits']);called.update(pair[0]['calls'])
  self.assertTrue(set(base.RETURNS)<=visited,set(base.RETURNS)-visited)
  self.assertTrue(set(base.TARGETS)<=called,set(base.TARGETS)-called)

 def test_unregistered_guest_refusal_is_preserved(self):
  saved={ad:base.ENTRIES.pop(ad) for ad in ['0791:1A04','16D6:0945']}
  try:
   for case in [1,8]:
    p,_=base.exercise(base.Oracle,case);r,_=base.exercise(base.PortMachine,case)
    self.assertIsNotNone(p['error']);self.assertEqual(p,r)
  finally:base.ENTRIES.update(saved)
