# ADR — PASS 2 per-segment extraction and post-extraction saturation gate

- **ADR ID:** ADR-PILOT002-PASS2-PER-SEGMENT-SATURATION-GATE
- **Status:** ACCEPTED — IMPLEMENTATION PENDING
- **Pilot:** PILOT-002
- **Decision timing:** frozen after PASS 1 diagnostic measurement and before any recompilation
- **Scope:** Course-to-Skill Compiler — PASS 1 / PASS 2 interface, coverage control, and compilation audit artifacts
- **Recompilation authorized by this ADR:** no
- **Primary defect:** PASS 2 global output-budget behavior
- **Primary objective:** make evidence extraction scale with semantic source coverage rather than with an approximately fixed global output total
- **Revision note:** coverage-first acceptance hierarchy, PASS 1 comparability band, two-pilot recompilation order, and boundary-deduplication canary frozen before implementation

---

## 1. Context

PILOT-002 was used to test whether the observed evidence-density collapse originated in PASS 1 temporal segmentation or later in the pipeline.

The working hypothesis before measurement was that PASS 1 might be under-segmenting the longer PILOT-002 source.

That hypothesis is **refuted** by the PASS 1 measurement.

PASS 1 produced:

- **PILOT-001:** 9 segments over 905 seconds
- **PILOT-002:** 41 segments over 4,384 seconds

Normalized segmentation rate:

- **PILOT-001:** 905 / 9 = **100.56 seconds per segment**
- **PILOT-002:** 4,384 / 41 = **106.93 seconds per segment**

The rates are close despite there being no proportionality rule in the PASS 1 specification.

Therefore:

> **PASS 1 scales with source duration sufficiently well for this diagnosis.**

The defect is localized downstream, in PASS 2.

---

## 2. Observed PASS 2 collapse

Evidence output:

- **PILOT-001:** 44 evidence records / 9 segments = **4.89 evidence records per segment**
- **PILOT-002:** 44 evidence records / 41 segments = **1.07 evidence records per segment**

Density ratio:

- 4.89 / 1.07 ≈ **4.6×**

The longer source therefore received essentially the same total evidence count while the number of semantic segments increased from 9 to 41.

This is consistent with an extractor that behaves as if it has an approximately fixed **global output budget**.

Instead of exhausting each semantic segment, PASS 2 appears to:

1. scan the full set of segments in one pass;
2. allocate a limited total number of evidence records across the whole lesson;
3. stop with approximately the same total output regardless of the number of segments supplied.

This behavior explains why evidence density per segment collapses as source size grows.

---

## 3. Independent quantitative cross-check

If PILOT-002 had preserved the PILOT-001 evidence density:

- 41 segments × 4.89 evidence records/segment ≈ **200 evidence records**

This independently converges with the earlier coverage analysis, which also indicated that approximately **200 evidence records** would be required for adequate source coverage.

The agreement is not treated as proof of an exact target of 200.

It is treated as convergent evidence that **44 total evidence records is structurally inconsistent with the semantic size of the PILOT-002 training corpus**.

---

## 4. Diagnosis

### Root mechanism

PASS 2 currently behaves as though the **lesson is the extraction unit**.

That makes all segments compete for one global generation/output budget.

For longer sources, this causes evidence density to fall approximately in inverse proportion to source size.

### Required architectural correction

The **segment must become the extraction unit**.

PASS 2 must operate independently over each `SEG-xxx`, so that adding semantic segments increases the amount of extraction work rather than diluting a fixed total evidence budget.

---

## 5. Decision

Two complementary controls SHALL be implemented.

They solve different failure modes and both are required.

### Decision A — PASS 2 runs per segment

PASS 2 SHALL execute **one segment at a time**.

For each temporal-map segment:

1. load only the segment and the minimum required local context;
2. extract atomic evidence from that segment;
3. continue until the segment is exhausted under the PASS 2 extraction rules;
4. persist that segment's evidence records;
5. record the number of evidence records emitted for that segment;
6. proceed to the next segment.

PASS 2 SHALL NOT perform one monolithic evidence-extraction sweep over all segments as its primary mechanism.

This change removes direct competition among all segments for a single global output budget.

### Decision B — post-PASS-2 saturation / coverage gate

After all segments have completed PASS 2, the compiler SHALL evaluate **L0 coverage** from the resulting evidence set.

If coverage is below the configured acceptance threshold, the compiler SHALL:

1. identify under-covered semantic blocks or segments;
2. re-scan those blocks;
3. emit additional atomic evidence where supported by source content;
4. recompute coverage;
5. repeat according to the gate policy until the threshold is satisfied or a defined stop condition is reached.

This is the required **saturation criterion** missing from the current specification.

The coverage gate is not replaced by Decision A.

Decision A corrects the extraction mechanism.

Decision B verifies the extraction result.

Both controls SHALL remain present because per-segment extraction alone does not guarantee adequate coverage.

---

## 6. Required artifact changes

### 6.1 `temporal-map.yaml` becomes mandatory

`temporal-map.yaml` SHALL be a mandatory compilation artifact for every run that executes PASS 1.

It SHALL:

- contain the ordered `SEG-001`, `SEG-002`, … sequence;
- contain the start and end timestamp for every segment;
- be persisted before PASS 2;
- have its cryptographic hash recorded in the compilation audit trail.

Rationale:

> A mandatory pipeline pass cannot remain unauditable in a system whose downstream artifacts are content-addressed and traceable.

### 6.2 `COMPILATION_MANIFEST` gains coverage metrics

The compilation manifest SHALL record at minimum:

- total segment count;
- total evidence count;
- evidence count per segment;
- aggregate evidence-per-segment metric;
- L0 coverage metric used by the saturation gate;
- coverage threshold;
- saturation-gate result;
- number of re-scan iterations, if any;
- hash of `temporal-map.yaml`.

### 6.3 PASS 2 records per-segment yield

PASS 2 SHALL emit or persist, for every segment:

- `segment_id`;
- evidence count emitted;
- extraction status;
- whether the segment was re-scanned;
- evidence count added by re-scan, if applicable.

This record is required even when a segment emits zero evidence.

Zero-yield segments must remain visible rather than disappearing from the audit trail.

---

## 7. Pre-recompilation coverage threshold lock

The L0 coverage threshold SHALL be frozen **before any recompilation using the corrected compiler**.

The frozen acceptance floor is derived from the only available pre-fix reference:

- **PILOT-001 baseline coverage:** 73.5%
- compiler state: old/global PASS 2 mechanism
- role of this value: **historical floor, not target**

The corrected compiler SHALL satisfy:

> **L0 coverage > 73.5%**

The comparison is deliberately strict. A result equal to 73.5% does not demonstrate improvement over the historical baseline.

This threshold SHALL NOT be raised, lowered, reinterpreted, or replaced after observing the corrected PILOT-001 or PILOT-002 result.

The 73.5% value does not define desired saturation. It defines the minimum predeclared acceptance floor for the first corrected run. Higher coverage is expected if per-segment extraction and targeted saturation are functioning as intended.

For the first corrected PILOT-001 acceptance run, all three conditions SHALL be checked against the frozen historical baseline:

- total evidence count **> 44**;
- L0 coverage **> 73.5%**;
- aggregate evidence yield **> 4.89 evidence records per segment**.

These are acceptance diagnostics for the correction, not permanent quotas for future corpora.

If corrected PILOT-001 does not improve these baseline measurements, the current root-cause hypothesis SHALL be reopened before PILOT-002 is recompiled.

---

## 8. Required observability

The corrected compiler SHALL make it possible to distinguish at least these cases:

### Case 1 — healthy scaling

Evidence count grows as semantic segment count and source content grow.

### Case 2 — legitimate low-density segment

A segment produces few or zero evidence records because the source itself contains little extractable methodology.

### Case 3 — extractor truncation or budget pressure

Many semantically substantive segments show abnormally low or uniform evidence yields.

### Case 4 — incomplete source coverage

Per-segment extraction finishes, but aggregate coverage remains below threshold and triggers the saturation gate.

Without per-segment yield records, Cases 2 and 3 cannot be reliably distinguished.

---

## 9. Acceptance criteria for the implementation

The fix is not accepted merely because total evidence count increases.

Implementation SHALL satisfy all of the following:

1. PASS 2 invocation is segment-scoped rather than lesson-global.
2. Every temporal-map segment has an auditable PASS 2 result.
3. Evidence IDs remain globally unique and sequential according to the project schema.
4. Evidence records retain source traceability to their originating segment and timestamp range.
5. A post-PASS-2 L0 coverage calculation is executed.
6. Under-covered blocks can trigger targeted re-scans.
7. Re-scans do not silently duplicate already captured atomic evidence.
8. `temporal-map.yaml` is persisted and hashed.
9. `COMPILATION_MANIFEST` records segment count, per-segment evidence counts, and L0 coverage.
10. The compiler exposes zero-yield and low-yield segments for audit.
11. No fixed total evidence target such as 44 or 200 is hard-coded as the success criterion.
12. Saturation completion for the first corrected runs requires **L0 coverage > 73.5%**, using the pre-frozen metric definition; the threshold is a floor derived from the old PILOT-001 run, not a target.
13. Corrected PILOT-001 records and compares its PASS 1 segment count against the historical value of 9.
14. Evidence yield per segment is compared against 4.89 only when corrected PILOT-001 returns **7 to 11 segments inclusive**; outside that band, yield is diagnostic only.
15. A corrected PILOT-001 PASS 1 count outside 7 to 11 triggers `PASS1_SEGMENTATION_VARIANCE_REVIEW_REQUIRED` and stops the sequence before PILOT-002.
16. The boundary-deduplication canary defined in §13 passes before either pilot is recompiled.
17. PILOT-001 and PILOT-002 are recompiled under the same frozen corrected compiler version.

---

## 10. Non-decision: no fixed evidence quota

The observed estimate of approximately **200 evidence records** is diagnostic, not normative.

This ADR does **not** introduce:

- a target of 200 evidence records;
- a minimum evidence count per segment;
- a fixed evidence-density quota;
- proportional evidence generation by elapsed time.

The intended invariant is:

> **Extraction effort must scale with semantic content, and completion must be judged by coverage/saturation rather than by a globally bounded output count.**

A short but dense segment may legitimately produce more evidence than a long but procedural or redundant segment.

---

## 11. Consequences

### Positive

- PASS 2 can scale with longer source material.
- Output-budget pressure becomes localized to one segment rather than the entire lesson.
- Sparse extraction becomes observable by segment.
- Coverage becomes an explicit compiler invariant.
- Re-scans become targeted instead of requiring full recompilation.
- PASS 1 becomes auditable through a mandatory hashed artifact.
- The manifest gains enough information to diagnose future density regressions quantitatively.
- Both pilots remain comparable because the corrected compiler version is held constant.

### Costs

- PASS 2 requires more independent model invocations.
- Evidence ID coordination must persist across segment-scoped calls.
- Deduplication must operate across segment boundaries and across re-scan iterations.
- Coverage measurement must be formally specified and frozen before recompilation.
- Compilation runtime and token consumption will increase for long sources.
- Both pilots must be recompiled, not only PILOT-002.

These costs are accepted because the existing behavior can silently under-extract long sources while still producing superficially valid downstream artifacts.

---

## 12. Interpretation lock

The current measurement supports the following conclusion:

> The PILOT-002 PASS 1 segmentation does not exhibit the proportional collapse previously suspected. The observed collapse is localized to PASS 2 evidence extraction, whose approximately fixed total output is consistent with a global output-budget mechanism.

The measurement does **not** by itself establish:

- the exact internal cause inside the model runtime;
- that 200 is the uniquely correct evidence count;
- that per-segment execution alone will fully solve coverage;
- that the observed PASS 1 segment counts of 9 and 41 are deterministic values.

The initial acceptance floor is nevertheless frozen **before corrected recompilation** at:

> **L0 coverage > 73.5%**

That number is inherited from the old PILOT-001 execution solely as a historical floor. It is not an optimization target and does not convert coverage into a quota.

### Hierarchy of interpretation for corrected PILOT-001

The corrected PILOT-001 run SHALL be interpreted in this order:

1. **Decision criterion — L0 coverage**
   - `L0 coverage > 73.5%` is the criterion that decides whether the correction demonstrates an improved extraction result.
   - This criterion is outcome-based and does not depend on reproducing the original PASS 1 segment count.

2. **Mechanism indicator — total evidence count**
   - the historical reference is 44 evidence records;
   - an increase above 44 is supporting evidence that the extraction mechanism is no longer behaving like the old globally bounded run;
   - this indicator does not independently decide acceptance if coverage has already established the result.

3. **Mechanism indicator — evidence yield per segment**
   - the historical reference is 4.89 evidence records per segment;
   - this comparison is valid only when the corrected PASS 1 segment count remains within the predeclared comparability band of **7 to 11 segments inclusive**;
   - inside that band, yield greater than 4.89 is supporting evidence of improved extraction intensity;
   - outside that band, yield SHALL be reported but SHALL NOT cause acceptance failure because the denominator has materially changed.

The yield band is frozen before recompilation to prevent post-hoc reinterpretation.

### PASS 1 stability question

The corrected PILOT-001 run SHALL record its new PASS 1 segment count and compare it with the original count of **9**.

This comparison is itself a diagnostic measurement.

The project currently has only single-run observations for:

- PILOT-001: 9 segments;
- PILOT-002: 41 segments.

Therefore the degree of PASS 1 run-to-run variability is currently unknown.

If the corrected PILOT-001 PASS 1 count falls outside **7 to 11 segments inclusive**, this SHALL be treated as material divergence from the original 9-segment map for purposes of this pilot.

A material divergence does not by itself prove that PASS 1 is defective, but it does invalidate treating 9 and 41 as precise deterministic measurements without uncertainty.

In that case:

- stop before PILOT-002;
- report the corrected PILOT-001 segment count;
- do not use the original 9-versus-41 comparison as a point estimate without qualification;
- reopen the diagnostic model to incorporate PASS 1 variability before spending the PILOT-002 recompilation.

This stop rule exists because the PASS 2 diagnosis currently rests partly on two single-execution PASS 1 measurements and must not silently assume zero segmentation variance.

---

## 13. Recompilation gate

**Do not recompile either pilot yet.**

Before any corrected compilation:

1. update the PASS 2 execution mechanism to per-segment extraction;
2. define and implement the post-PASS-2 coverage/saturation gate;
3. freeze the initial coverage acceptance floor at **L0 coverage > 73.5%**;
4. freeze the PASS 1 comparability band for PILOT-001 at **7 to 11 segments inclusive**;
5. make `temporal-map.yaml` mandatory and hash-addressed;
6. extend `COMPILATION_MANIFEST`;
7. add per-segment PASS 2 yield logging;
8. add and pass the boundary-deduplication canary defined below;
9. statically verify the modified compiler/spec;
10. freeze the implementation state intended for both pilot recompilations.

### Mandatory recompilation order

The corrected compiler SHALL be applied to both pilots under the **same frozen compiler version**.

The mandatory order is:

1. **PILOT-001 first**
2. **PILOT-002 second**

PILOT-001 is the acceptance canary for the correction because it is materially cheaper to compile and has a known historical baseline:

- 9 segments;
- 44 evidence records;
- 73.5% L0 coverage;
- 4.89 evidence records per segment.

### Corrected PILOT-001 acceptance logic

The acceptance hierarchy is:

#### A. Decisive result criterion

- **L0 coverage > 73.5%**

This is the criterion that decides whether the corrected extraction result improves on the historical baseline.

#### B. Supporting mechanism indicators

Report and compare:

- total evidence count versus 44;
- PASS 1 segment count versus 9;
- evidence yield per segment versus 4.89.

Interpretation rules:

- evidence count above 44 supports the global-budget diagnosis but is not the sole acceptance criterion;
- yield above 4.89 is comparable only when corrected PASS 1 returns **7 to 11 segments inclusive**;
- if PASS 1 returns outside 7 to 11 segments, report yield without using it as a pass/fail criterion.

### PASS 1 divergence stop

After corrected PILOT-001 completes PASS 1, compare the new segment count with the historical count of 9.

If the new count is outside **7 to 11 segments inclusive**:

1. record the new segment count in `temporal-map.yaml` and `COMPILATION_MANIFEST`;
2. flag `PASS1_SEGMENTATION_VARIANCE_REVIEW_REQUIRED`;
3. stop the pilot sequence before PILOT-002;
4. report the observed segment count and its deviation from 9;
5. reopen the diagnosis before any PILOT-002 recompilation.

This stop occurs even if corrected PILOT-001 later shows coverage improvement, because a materially unstable segmentation count weakens the quantitative basis of the original 9-versus-41 scaling comparison and must be understood before the expensive second pilot is run.

If the new count remains within 7 to 11 segments inclusive, the original yield reference of 4.89 may be used as a mechanism comparison.

### PASS 2 diagnosis reopen condition

If corrected PILOT-001 remains within the PASS 1 comparability band but does **not** achieve `L0 coverage > 73.5%`, stop before PILOT-002 and reopen the PASS 2 diagnosis.

A failure to improve coverage on the known PILOT-001 corpus would indicate that global output-budget pressure is not, by itself, a sufficient explanation of the observed PASS 2 collapse.

Evidence count and yield SHALL still be reported because they may help localize the remaining defect.

### Comparability lock

PILOT-001 and PILOT-002 SHALL NOT be compared if compiled by different compiler versions.

The two-corpus design depends on holding compiler behavior constant. Otherwise any observed difference would confound:

- source density; and
- compiler version / extraction mechanism.

Therefore corrected PILOT-001 and corrected PILOT-002 must share the same frozen compiler implementation, PASS 2 mechanism, saturation logic, deduplication logic, schemas, coverage metric, and PASS 1 specification.

### Boundary-deduplication canary

Before PILOT-001 recompilation, the implementation SHALL pass a dedicated fixture covering a known risk introduced by segment-scoped extraction.

The fixture SHALL contain two adjacent temporal segments whose boundary contains **two genuinely distinct neighboring evidence units** with enough lexical or semantic similarity to tempt over-aggressive deduplication.

Expected behavior:

1. PASS 2 extracts both evidence units independently;
2. cross-segment deduplication evaluates them;
3. both distinct evidence units survive;
4. neither is silently merged, suppressed, or replaced by the other;
5. provenance to the correct originating segment/timestamp remains intact.

The canary fails if deduplication collapses the two legitimate neighboring evidence records into one.

This fixture protects against a correction that increases extraction coverage but then silently destroys valid evidence at segment boundaries.

Only after the implementation is frozen and this canary passes may corrected PILOT-001 begin.

Only after corrected PILOT-001:

- remains within the PASS 1 comparability band of 7 to 11 segments; and
- achieves `L0 coverage > 73.5%`

may corrected PILOT-002 run.

---

## 14. Decision summary

**Accepted architecture:**

`PASS 1 → persisted temporal-map.yaml → PASS 2[SEG-001] → PASS 2[SEG-002] → … → PASS 2[SEG-N] → coverage/saturation gate → targeted re-scan if needed → downstream passes`

**Validation sequence:**

`implementation → boundary-dedup canary → freeze compiler → PILOT-001 acceptance run → gate → PILOT-002 run`

The defect is treated as a **PASS 2 scaling and completion-control defect**, not a PASS 1 segmentation defect.

The first corrected-run coverage acceptance floor is frozen at **>73.5% before recompilation**, while the approximately **200 evidence-record estimate remains diagnostic only and never becomes a quota**.
