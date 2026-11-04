# T26 offside/commentary tree

Status: all92 canonical M2 stages pass on fixed artifacts. Full-match validation,
profile,timing and final audits remain pending.
PR#61 stays draft;accepted main remains T25 until completion and merge.

## Source and implementation

At accepted oracle2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c,the complete tree
contains offside_call0791:56D9,set_message_word26A0,commentary_plain2B0F,
emit_commentary1EB5,apply_perf_delta1E53,write_commentary_line1D4A,
commentary_record_is_new1C78,commentary_line_memory1829,fill_bytes214B:0018
and wrap_add_in_range214B:1C86. Inventory resolves25 actual near/far returns
and31 owned function code objects,including both nested word helpers. Existing
native2BE5,T23 Pascal strings and T25 text rendering are the only guest boundaries.

Rust preserves source register/argument order,pending stack writes,live frame
SS/locals,ratings/ring updates,captured pointers/indices and live pointed-to
words. Generator locals survive real guest suspensions. Rendering retains its
captured temporaries,marker expansion,padding,live row/column/colour reads and
actual draw calls. Byte fill and signed-delta wrap retain their distinct store/
pending-push/flag order. All nondefault exports stay Python. See contract.md.

## Preservation and development epochs

Before any build,T25's1083 primary/277 evidence and separately sealed6sources/
121inputs plus merged audit were verified. Actual T25 source/tests/adapter/both
interpreter artifacts are saved in.cache/T26-baseline(77 files);older
.cache/T25-baseline is T24. Capture sealed49 pure-oracle files before execution
and produced80 exclusive private shards,eight per body,from one genuine prefix
through event index692. CapturePID352793 exited0;the initial audit verifies the
pre-implementation runtime epoch. Final_capture_audit verifies that preserved
epoch without rerunning its audit against the changed candidate. Private bytes
remain ignored;public receipts contain hashes/counts.

Pre-native assertions failed for all ten bodies on accepted T25. The first
development native run caught26A0 reading its argument before entering its
frame;the corrected source order passes and the failed log remains. Archived
development-probe-v1 passes5,120 authored/960 real-schedule/1,280 ABI-double
pairs with positive witnesses for all31 code objects/25 returns and no owned
default Python execution inside native lifetimes. Its executed source epoch
is archived separately from the later canonical authored corpus.

The first branch instrument requested the impossible false edge of literal
while True;the failed scan and source archive remain. The sealed plan documents
that edge,two signed16 wrap bounds and variant-only choices explicitly,with65
reachable source outcomes observed. It seals921 distinct reached error selectors
and147,360 error pairs. Ordinals sample bounded early/middle/last writes;this is
not an exhaustive global fault or branch coverage percentage.

The initial live diagnostic is preserved/rejected because its effect count could
include observer-log-only differences. Strengthened live-v2 aligns observer reads
and requires memory/register/call effects;all eight scenarios/1,280 pairs pass.
Both development receipts and executed source archives remain separately bound.

## Final artifact and current gates

Both final full public preflights pass98 tests(CPython108.021s,PyPy152.978s).
These are test-suite wall times,not match performance. Both interpreter artifacts
were archived after those preflights. freeze-v1 fixes1647 concrete primary
bindings and72 explicit producer/audit sources. Nothing bound is rebuilt or
edited during canonical execution.

Canonical new normal comparisons pass30,960 pairs,including10,000 isolated
ABI pairs. All147,360 error pairs/921 reached selectors,2,400 source branch
pairs/65 positive outcomes,224 variants and20,960 all31-code-object scope checks
pass. No owned default Python code executes inside native lifetimes.
Canonical new body controls pass20,960 comparisons,and outputs pass146,720.
All25 real return controls
are reached/detected across4,000 cases. The new live matrix passes1,280 pairs
with semantic effects,including liveSS,cached pointer/index versus live words,
pending pushes,lateDF,captured rendering buffers and later row reads. Every
prior69-body proof/control/error/branch/variant/helper gate and nine prior live
matrices passed freshly on this same artifact.

The controller queues92 M2 and97 total canonical producer groups,plus12 per
complete four-arm timing campaign. Full source/frame/error/output fidelity,
ordered drive,lifecycle,ALL75/F40/immutable prefixes,independent backend/full
profile,strict quiet-host timing and post-writer ledgers remain mandatory.
No T26 speed result or final profile count is available yet. The79-body/
45,569-moved-entry figures remain predictions,not speed,source-line/test
coverage or whole-game completion. See checkpoint#1 for live status.
