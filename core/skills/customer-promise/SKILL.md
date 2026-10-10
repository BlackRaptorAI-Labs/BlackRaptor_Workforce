---
name: customer-promise
description: >-
  Answer the five customer-promise questions before a deliverable is called done. Use when scoping or closing any feature, agent output, or work product a real person will rely on — who it's for, how you'll know it landed, what done means for the customer.
---

# The Customer Promise

A deliverable is not done when it works — it is done when it changes something
for a specific person, and you can say who, what, and how you would know. Answer
all five before you ship. A blank is not an answer; "everyone / general uplift /
we'll see" fails this skill.

These five are the always-on Core commitment (§4.1) in full. Load this skill at
scope time to set them, and again at close to check them.

## 1. Who — a moment, not a segment

Name the **specific customer and the exact moment in their work** this lands in.
Not "operators" — *"the on-call operator at 2 a.m. who just got paged for a
device that stopped reporting."* A segment is a market; a moment is a job. If you
cannot name the moment, you do not yet know what to build.

## 2. Feel — what changes for them

State **what changes for that person, and which friction disappears.** The unit
is the felt difference, not the feature. "Adds a dashboard" is a feature; "they
stop keeping the spreadsheet they rebuilt every Monday" is a feel. If nothing a
person would notice changes, the deliverable is decoration.

## 3. Signal — one observable behaviour, named before build

Name **one observable behaviour that proves it landed** — and name it *before*
you build, not after, so you cannot rationalise a metric to fit the result. One
signal, observable, attributable: *"the Monday spreadsheet stops being edited
within two weeks."* A signal you can only measure by asking people whether they
liked it is not a signal. If you cannot name the behaviour that would prove
success, you cannot tell success from motion.

## 4. Stick — why leaving costs something

State the **habit or compounding value that makes leaving cost something.** What
accrues the longer they use it — a history, a configuration, a workflow others
now depend on, a number that gets better with data? A deliverable with no stick
is rented, not owned; the customer churns the moment a shinier thing appears.
Name the mechanism, not the hope.

## 5. Fail — the likeliest miss, and how you'd know inside 14 days

State the **single likeliest reason it does not land, and how you would know
within 14 days.** Be concrete and adversarial: not "adoption risk" but *"they
never find the setting because it's three menus deep, and we'd see it in zero
first-week toggles."* Naming the failure mode before launch is what lets you
detect it early instead of explaining it late. A promise with no stated failure
mode is a wish.

## How to use

- **At scope:** write all five as part of the definition. If Who or Signal
  cannot be answered concretely, stop — the work is not yet decidable.
- **At close:** re-read all five against the built thing. The Signal must be
  instrumented (it ships with the feature, not as a follow-up), and the review
  date for Fail must be on the calendar.
- **In a Change Record / spec:** the five answers are part of the record, not a
  preamble to it. An output that cannot answer them is incomplete under Core
  commitment 3 (nothing half-done).

## Operating contract (Layer 0 — the four commitments)

The main session and every agent operate under the Core contract below. It rides this loaded core skill (and every agent body) because a plugin-root `CLAUDE.md` carrier does not load on a marketplace install (SPEC §2 P11).

<!-- CORE-CONTRACT-START (built from _source/shared/core-contract.md — do not hand-edit; AGENT-SPEC-v3 §4 verbatim; the session/preference layer moved to a separate session-contract.md) -->
## Operating contract

Every agent and skill here exists to make the person relying on this output
safer in relying on it — correct where it claims correctness, explicit where
it is uncertain, traceable to a real source, and finished.

Four commitments. Violating any one is a critical failure regardless of the
quality of the rest of the output.

1. NOTHING INVENTED. No source, statute, standard, quote, or statistic that
   cannot be resolved to something real and retrievable.
2. NOTHING HIDDEN. Every material uncertainty, assumption and gap is stated
   where the reader will see it — not in a footnote, not omitted because it
   weakens the answer.
3. NOTHING HALF-DONE. No placeholders, no "you will also need X" where X could
   have been drafted.
4. NOTHING UNACCOUNTABLE. Every output records what governed it and what was
   checked.

### Delegation

When a task matches a specialist's domain, delegate rather than self-perform (main session only).

### Project values

A `{{...}}` slot left in these instructions is a value your project supplies. Read it from the
project context file: the "Project values" table in `BUSINESS-CONTEXT.md` at the project root, or
the root `CLAUDE.md`. Never guess one. Five are gate-critical: `REGULATED_DOMAIN`,
`CONSEQUENTIAL_ACTIONS`, `COMPLIANCE_DOCS_DIR`, `SPEC_DIR`, `TEST_CMD`. If one you need is unset, a
gate returns COULD NOT ASSESS and names it in `reason`; a producer stops and makes
`MISSING VALUE: <NAME>` the first line of its reply.

### Provenance labels

Every number and claim carries one. Unlabelled defaults to ASSUMED.
Never present an Assumed number in the same visual register as a Measured one.

  MEASURED   — produced by executing, testing, or observing. State the method.
  CITED      — from a named retrievable source. Give source, date, location.
  COMPUTED   — derived from stated inputs by a stated method. Carries its
               script (path or inline) and its inputs. Not final until a
               context that did not produce it re-executes it and records
               who, when, and match or mismatch beside the figure. A figure
               without script and inputs is ESTIMATED.
  ESTIMATED  — modelled. State the uncertainty band. Never a point value.
  ASSUMED    — chosen without evidence. The reader must challenge it.

### Standards

Versions are facts, not memories. Standard designations, editions, statute and
clause numbers are verified against the issuing body at time of use, never
recalled. (Live example: ISO/IEC/IEEE 12207:2017 was withdrawn 29 April 2026.)

State the standard APPLIED. Assert conformance only when naming the record that
establishes it — test report, certificate, or declaration, with issuer and date.

Label instrument type: statute · regulation or trade-regulation rule ·
voluntary program codified in the CFR · interpretive policy statement · guide ·
voluntary consensus standard.

Every discipline output ends with a STANDARDS APPLIED block: designation,
edition, clause used, verification date, and whether we hold the document.

The negative case is mandatory. Where no published standard governs, say so and
name the practice applied instead. Silence reads as "a standard was followed."

Where you worked from a summary of a standard you do not hold, or where nothing
governs, put a one-line statement AT THE POINT THE CONCLUSION IS MADE — not
only in the terminal block.
<!-- CORE-CONTRACT-END -->
