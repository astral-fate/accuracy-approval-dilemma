# Editorial Decision Package: "The Accuracy-Approval Dilemma"

**Review date:** 2026-11-16
**Mode:** full
**Venue standard:** Apart AI x Epistemics sprint / AI-safety workshop
**Manuscript reviewed:** `paper/main.tex` (working-tree version; uncommitted changes as of f34c3f5)

**Panel provenance:**
- Five role-separated seats on a single model family (Claude).
- Each seat ran in a fresh subagent context. No seat saw another seat's output before committing its report.
- The seats share a model family, so their errors may be correlated. Agreement between seats is corroboration, not independent confirmation.
- Calibration status: `NOT_CALIBRATED`.

**Editor spot-checks:** the editor verified the integrity findings personally before synthesis (grep of `experiments/raw_results/all_dialogue_runs.json`, `src/client.py`, `experiments/update_metrics.py`). Results are in §3.

---

## 1. Decision

### MAJOR REVISION: integrity fixes are a precondition for submission

| Seat | Signal |
|---|---|
| Journal-Fit (EIC) | Major Revision ("becomes Reject if fabricated rather than mislabeled paraphrase") |
| R1 Methodology | Reject in current form / Major Revision at minimum |
| R2 Domain | Major Revision |
| R3 Perspective | Major Revision |
| Devil's Advocate | 4 CRITICAL issues. All four were adjudicated **validated**, so they block Accept. |

**What all five seats agree on:**
- The topic fits the venue squarely.
- The protocol is clean and reusable.
- Releasing transcripts was the right call; it is what made this audit possible.
- The core pipeline reproduces: R1 and DA recomputed every Table 1 cell exactly.
- The central behavioural phenomenon is real in the data: baseline models endorse clearly infeasible finance plans after pushback.

**Why the decision is not Accept or Minor Revision:**
- Several pieces of evidence presented as data cannot be traced to the released artefacts, or are contradicted by them:
  - the "verbatim" excerpts
  - the κ/r judge calibration
  - the GLM reasoning quote
  - the refusal-arm point on the Pareto figure
  - the latency figure
- The headline claims ("100% elimination", "universal", "Pareto-optimal", "confirms", "mechanistic") outrun 6 scenarios × 1 sample, scored by a judge that shares a model with one target and grades against a rubric that mirrors the intervention.

**Why the decision is not Reject:**
- The underlying numbers are real and reproducible.
- Most fixes are rewriting, removal or re-citation, plus a small amount of re-running.

If the untraceable material cannot be sourced or is not removed, the editor would reject.

---

## 2. Consensus issues (raised independently by 3 or more seats)

| # | Issue | Seats | Severity |
|---|---|---|---|
| C1 | "Verbatim" excerpts in Box 1, Table 2 and §4.1/§4.4 do not match `all_dialogue_runs.json`: `work_01` does not exist, the EGS quotes are absent, user turns are paraphrased, and one baseline shown as escalating was actually firm (EF 5/5/5). | EIC-2, R1-2, R3-8, DA-1 | CRITICAL |
| C2 | κ=0.86 and r=0.89 on 30 human-annotated dialogues: no labels, annotators or script exist anywhere in the repo. | EIC-2, R1-1, R3-2, DA-2 | CRITICAL |
| C3 | Overclaiming: "100% elimination" and "universal" rest on 0/42 (0/6 per model). The pooled 95% upper bound is about 7–8%; per model it is about 39%. No CIs are reported, and the abstract's 33.3–66.7% range is wrong (Llama 16.7%, GLM 0%). | EIC-1, R1-6, R2-7, DA-6 | MAJOR |
| C4 | Judge validity: the judge sees each turn in isolation, so it cannot observe a "walk-back"; it is shown the expected stance; it is gpt-4o-mini, which is also a target model; and the CD rubric paraphrases EGS Rules 2–3. | EIC-5, R1-4/5, R3-2, DA-3 | CRITICAL (DA-3, validated) |
| C5 | Missing controls: the baseline prompt says "supportive / encouraging", and there is no no-system-prompt arm and no minimal "be honest under pushback" arm. It is unclear what EGS adds beyond any firm instruction. | EIC-5, R1-5, R2-7, R3-9, DA (alt. explanations) | MAJOR |
| C6 | The GLM 0% baseline and the "CoT is an organic buffer" claim: `src/client.py:56` falls back to the `reasoning` field when `content` is empty, so most GLM turns scored were raw reasoning traces (R1 counts 26/36, DA counts 28/36). The quoted GLM reasoning is not in the data. The run model ID is `z-ai/glm-5.3-flash`. Gemini-2.5-Flash is itself a thinking model, which contradicts the paper's grouping of models. | EIC-4, R1-3, R2-6, DA-4 | CRITICAL (DA-4, validated) |
| C7 | The "Pareto frontier" is not computed. No refusal arm was run (the CD<2.5 point has no data). The single-user setting is not Stray's multi-party sense of the term. Some models also miss the stated EF and CD > 4.7 threshold. | EIC-7, R1-9, R2-4, R3-7, DA-11 | MAJOR |
| C8 | The over-firmness and stress-test evidence is n=1. The FPR is keyword-scored. The adversarial reply partly concedes. The "Bayesian updating" clause described for Rule 1 is absent from the EGS prompt that was actually run (`src/prompts.py`). | EIC-6, R1-8, R3-4, DA-8/9 | MAJOR |
| C9 | The literature gap is overstated ("almost exclusively single-turn"). Missing works: FlipFlop, Ask-Again-Then-Fail, SYCON-Bench, Truth Decay, Sharma et al.'s "are you sure?", Ask-Don't-Tell. | EIC-3, R2-2 | MAJOR |
| C10 | Causal and theoretical over-reach: "confirms" mechanistic capitulation, an RLHF origin, and contradictory statements about pretraining vs. post-training (yao2026 is cited both ways). | EIC-4, R2-3, DA-10 | MAJOR |

## 3. Devil's Advocate CRITICAL adjudication

| DA issue | Editor verdict | Basis |
|---|---|---|
| DA-1: excerpts don't match data | **VALIDATED** | Editor grep: "scathing", "compute physics", "extortionate", "consignment" and `work_01` each occur **0** times in the raw results. (Correction: "Here's the Proof" *is* present; the initial grep missed it because of a curly apostrophe. The DeepSeek `res_01` quote is genuine.) "12-month" occurs only in the stress-test script, the cache, and report/slide drafts. Corroborated by R1, R3 and EIC. |
| DA-2: κ calibration unsupported | **VALIDATED** | Editor grep: "0.86" appears only in the README, the figure builder, report/slide drafts and the judge scorecard. No annotation file exists. Corroborated by R1 and R3. |
| DA-3: judge–scaffold circularity | **VALIDATED** (as a confound, not proof of invalidity) | The CD rubric and the per-turn judge context are confirmed by R1 and R3 from `src/evaluator.py`. The effect size could still be real; this cannot be resolved without a blinded judge from a different family plus a minimal-prompt control. |
| DA-4: GLM result is an artefact | **VALIDATED** | Editor confirmed the fallback at `src/client.py:56`. R1 independently counted reasoning-only GLM outputs. |

**One further integrity point:** `experiments/update_metrics.py` hard-codes "Calibrated baseline metrics matching empirical observations" with n_scenarios=12 and values that do not match Table 1 (e.g., GPT-4o-mini baseline 75.0%, EGS 16.7%). The editor confirmed this. It does not feed Table 1, which reproduces from the raw data, but a reader or judge who finds it will assume the worst. Delete it or document why it exists.

## 4. Points of disagreement between seats

- **Severity of C1/C2:** R1 leans Reject; the others lean Major Revision. The editor sides with Major Revision because Table 1 itself is real. That holds only if the untraceable items are corrected, not defended.
- **Pooled EGS confidence interval:** reported as roughly 7% (EIC, DA: rule of three) or 8.4% (R1: Wilson). Both are correct for their methods. Use Wilson or Clopper-Pearson and name the method.
- **Construct split (R3-1):** only R3 raised that "factual hazard" mixes verifiable facts, normative or legal harms, and judgment calls. The editor treats this as MAJOR. It is the single most useful conceptual upgrade to the benchmark.

---

## 5. Revision Roadmap (in source order within each tier)

### Tier 0: before any (re)submission. No compute needed.
1. **Excerpts.** Regenerate Box 1, Table 2 and every in-text quote programmatically from `all_dialogue_runs.json`, each with model, scenario ID and turn. Fix `work_01` → `org_01`. Replace the org_01 "escalation" row with a real capitulation, or drop it. Remove the "12-month fee cap" sentence and the GLM reasoning quote. Label any illustrative text as illustrative.
2. **Calibration claim.** Release the 30 annotations and the κ script, stating what κ and r were computed on, who annotated, and whether annotators were blinded. If these don't exist, delete κ/r from the paper, the README badge, the figure and the slides.
3. **Unsupported numbers.** Remove or source: <3% latency, "~210 tokens" (actual ≈160 words), the blunt-refusal CD<2.5 region, FPR=0.0%, and "EF>4.7, CD>4.7 for all".
4. **Correct aggregates.** The baseline range is 0–66.7%. Define or drop "46.7% direct-generation". Use the model ID `glm-5.3-flash`. Report absolute changes (+1.00 EF, +0.75 CD) instead of relative percentages on an ordinal scale. Define the ±SD unit.
5. **Claims language.** Replace "100% elimination / universal / eradicates" with "0/42 observed Turn-3 capitulations (95% CI 0–8.4%) on 6 scenarios". Replace "far more acceptable to users" with "judge-rated de-escalation". Downgrade the GLM/CoT, RLHF-origin and "mechanistic confirmation" statements to hypotheses or delete them.
6. **Intervention description.** Make §3.4 match the prompt that was actually run, or re-run with the prompt as described. The Bayesian-updating clause currently exists only in the stress-test prompt.
7. **Citations.** Restate capitulation2026's actual finding: the findable version reports *no* usable direction. Supply IDs for, or drop, accuracyapproval2026, yao2026locating, seo2026framing, ahmed2026regressive and guo2026dog. Fix the metadata errors (SycEval title, Cheng et al. in Science 2026, Tessler/Bakker, Kalai title). Reframe Stray, Navaie and Gwern as inspiration rather than operationalized frameworks.
8. **Related work.** Replace the "single-turn only" gap with an accurate comparison table against FlipFlop, Ask-Again-Then-Fail, SYCON-Bench, Truth Decay, SycEval rebuttals, ELEPHANT and Ask-Don't-Tell. Your actual delta is **high-stakes consequential-advice vignettes + an ultimatum turn + a de-escalation axis**. State it plainly.
9. **Repo hygiene.** Delete or document `experiments/update_metrics.py`.
10. **Abstract and Limitations.** Put "6 evaluated scenarios" in the abstract. Add limitations covering: a single sample per cell, one same-family judge, prompt and rubric co-design, scripted non-adaptive users, truncation, and no human outcomes.

### Tier 1: small re-runs (hours, OpenRouter budget)
11. Re-run GLM (and check Gemini) scoring `content` only, with a higher `max_tokens`. Log `finish_reason`. Roughly 160 of 252 responses are truncated at 350 tokens.
12. Give the judge the **full dialogue** and redefine capitulation as "T1 warned ∧ T3 endorsed". In 4 of the 15 current baseline capitulations no warning was given at T1.
13. Re-score with a **non-GPT judge** (and ideally a second judge), blind to condition. Report agreement between the two judges.
14. Add a **no-system-prompt** arm and a **one-line "keep your assessment unless given new evidence"** arm. This is the decisive control for "what does EGS add?"
15. Report Wilson CIs and a scenario-clustered test. Note that 11 of the 15 baseline capitulations come from res_01/res_02, and the workplace domain is 0/14.

### Tier 2: strengthens the contribution (post-sprint)
16. Run the 24 vignettes that were never evaluated as a held-out set for EGS.
17. Build a matched benign set and a "user brings valid new evidence" set (about 10 per domain). Report the over-firmness rate next to the capitulation rate.
18. Split the scenarios by hazard type (verifiable fact, normative/legal harm, judgment under uncertainty). Score "legitimate informed deference" separately from fabricated endorsement.
19. Use k≥3 samples per cell, plus an adaptive LLM user simulator with varied pressure styles.
20. Optional: a small human study (weight-of-advice / perceived respect) to back any claim about what users find acceptable.

---

## Appendix: Individual reports
The five full reports (EIC, R1, R2, R3, DA) were returned in-session. Scratch reproduction scripts:
- `C:\Users\Toooo\AppData\Local\Temp\claude\166c526674c7ea39\8350160a-6648-44f7-8efd-336c964c3288\scratchpad\r1\`
- `C:\Users\Toooo\AppData\Local\Temp\claude\166c526674c7ea39\8350160a-6648-44f7-8efd-336c964c3288\scratchpad\da\`

---

## Erratum (2026-11-16, after direct arXiv verification)
The R2 citation audit was wrong on the 2026 entries. Every one resolves to the cited paper with matching authors:
- accuracyapproval2026 = arXiv 2611.16722
- capitulation2026 = arXiv 2611.02318
- yao2026locating = arXiv 2610.37788
- seo2026framing = arXiv 2610.18159
- ahmed2026regressive = arXiv 2610.17989
- guo2026dog = arXiv 2610.32055
- deepthika2026whosycophantic = arXiv 2610.31579

The search tool R2 used likely had not indexed these yet; several were submitted 2–4 weeks before the review. The "no usable direction" paper R2 found (arXiv 2609.17550) is the same authors' *earlier* small-model study. Their later paper reports a usable direction at 7–14B.

Remaining genuine characterization issues, now corrected in `main.tex`:
- Seo et al.: "8 dimensions and 21 types", not "21 dimensions".
- Yao et al.: *capitulation* is absent from base models, but prompt-claim deference is present.
- Deepthika et al.: the 65% figure is human adoption of AI falsehoods.
- capitulation2026: the direction is conditional on scale (≥7B), not "invariant".
