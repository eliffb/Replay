
# ADR-001: Event Sequence Generation

## Status
Accepted

## Context
Aynı run'a eşzamanlı event yazan 50 worker ile iki yöntem karşılaştırıldı.

## Decision
runs.last_seq sayacı ve SELECT ... FOR UPDATE yöntemi seçildi.

## Experiment Results

| Method | Duration |
|---|---:|
| MAX(seq) + retry | 7.361 s |
| Counter + FOR UPDATE | 0.432 s |

## Correctness
- Both methods produced 50 events.
- Both produced contiguous sequence numbers 1..50.
- Counter consistency was verified for FOR UPDATE.

## Consequences
- Sequence generation is serialized per run.
- Row locking introduces contention.
- Different runs can proceed independently.
