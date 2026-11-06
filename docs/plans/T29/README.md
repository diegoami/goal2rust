# T29 proof preparation outside the active development epoch

These are prepared producers, not completed evidence. They live here because
T29's live development controller hashes every source in out/T29; adding files
there now would violate its fixed epoch. Do not modify engine/out/T29 bound
sources while capture/development producers live. Metadata and these separately
bound templates are outside those controllers' input sets.

After development passes AND PID53605 exits, post_development.py can install
these templates exclusively into out/T29. It must verify the completed source
map first and refuse to duplicate either controller. It then waits for known-idle
IT13 before starting each new producer. It archives exact sources and the active
CPython binary before the first attempt and never overwrites logs or receipts.
Any failure stops the pipeline and preserves that source/artifact/log epoch.

The proposed live matrix has five positively witnessed callback scenarios:

- First cached physical record versus later seg/off argument rereads.
- Cached pointer/point across guest, with a newly read original-record Y byte.
- Captured SENT direction versus AX changed by the real register-read callback.
- Local-byte read in changed live SS after the write listener.
- AX high byte captured before a callback on the local-byte SS read.

Each is planned for160 Python/native comparisons, with equality, concrete final
state/call-packet assertions, positive callback hits and a mutation-disabled
reference that must differ in memory/registers/calls. This is800 planned pairs,
not an observed pass. Own memory reads remain deliberately untapped.

The source branch observer reads trace locals/actual helper returns only. Eight
outcomes cover state13, holder equality, X-near and Y-near, both sides of each.
There are no extra guest-memory/register reads. The preseal plan must positively
reach every selected error selector and every source outcome before publishing
exclusive proof-plan-v1.json. Selector counts are determined by reached rows,
not copied from T28. Body436,outputs437..443 and actual return444 remain distinct.

near_zone_differential.py is a later canonical template: genuine8/four observer
modes/500 authored/integrated/ABI states,source/outside/nondefault all6-owned
witnesses,body/output/return controls,error selectors and branch coverage. It
requires a fresh final evidence.py and frozen combined artifact, retaining all
prior87 bodies/12 live matrices. The post-development controller does not run
this canonical template or final build/freeze/timing/merge. No claim of native
fidelity, performance or final acceptance follows from these prepared files.
