# Freight Audit

[![CI](https://github.com/cmiedema25-rgb/freight-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/cmiedema25-rgb/freight-audit/actions/workflows/ci.yml)

Detention and layover charge adjudicator for a carrier desk. Reads a settlement packet of JSONL files and writes one decision per charge:

`APPROVE` · `PARTIAL` · `DENY` · `DUPLICATE` · `INSUFFICIENT_EVIDENCE`

Same output contract as the Harbor `insight/freight-audit` task the pass-2 zip was scoring. Packet and policy here are original Inland Empire / Northline numbers, not the benchmark oracle files.

Pairs with [driver-settlement-automation](https://github.com/cmiedema25-rgb/driver-settlement-automation) (paper in) and [freight-dispatch-shift](https://github.com/cmiedema25-rgb/freight-dispatch-shift) (plan the day). This repo decides whether the accessorial invoice survives.

**Not a legal billing product.** Rate math is a planning aid.

## Run

```bash
git clone https://github.com/cmiedema25-rgb/freight-audit.git
cd freight-audit
python -m pip install -e ".[dev]"
make verify
```

```bash
freight-audit \
  --input examples/input \
  --output build/adjudications.jsonl

freight-audit \
  --input examples/input \
  --output build/cutoff.jsonl \
  --as-of 2026-04-04T19:00:00Z
```

## Sample packet

| Charge | What the desk sees | Decision |
| --- | --- | --- |
| CHG-0001 Perris detention | IN 07:50, corrected OUT 12:35, 60 free + 15 grace, $15/15 min, $60 already paid | `PARTIAL` $150 / 210 billable min |
| CHG-0002 Colton layover | Trailer in 15:40 Apr 4, out 08:10 Apr 5, local date change, $250 flat | `APPROVE` $250 |
| CHG-0003 | Duplicate of CHG-0001 | `DUPLICATE` |
| CHG-0004 short live load | 55 minutes on site after window start | `DENY` — still inside free+grace |

`--as-of` before `2026-04-04T20:00:00Z` hides the OUT correction, so CHG-0001 bills off 12:20 instead of 12:35.

## Rules

1. Duplicate charges never pay.
2. Need one unambiguous IN and one OUT on the billed asset after applying ACTIVE corrections.
3. Need one CONFIRMED appointment covering arrival and one winning rate term (facility addendum beats region; equipment-specific beats generic).
4. Detention clock starts at `max(arrival, appointment window start)`. Subtract free + grace, round per term, apply cap / escalation.
5. Layover pays the flat only when the term trigger is met (`LOCAL_DATE_CHANGE` here).
6. Settlement PAYMENT / RECOVERY on the service episode reduces what is still approvable. `PARTIAL` when billed > remaining support.
7. Missing or conflicting evidence is `INSUFFICIENT_EVIDENCE`, not a guessed amount.

## Packet files

```text
examples/input/
  facilities.jsonl stops.jsonl charges.jsonl appointments.jsonl
  rate_terms.jsonl rate_overrides.jsonl events.jsonl event_updates.jsonl
  visit_activity.jsonl service_links.jsonl settlement_ledger.jsonl
  record_visibility.jsonl
```

## License

MIT © Charles Miedema
