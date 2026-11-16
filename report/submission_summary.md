# AI x Epistemics Sprint: Submission Package (v2)

**Submission portal:** https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15
**Author:** Fatimah Emad Eldin, Cairo University (12422024441586@pg.cu.edu.eg), with Apart Research

All numbers below come from `experiments/metrics_summary_v2.json` (504 dialogues). They replace the earlier sprint run, which this package previously described.

---

## Project title
```text
The Accuracy-Approval Dilemma: Benchmarking Multi-Turn Epistemic Capitulation in High-Stakes Decision Support
```

## Tracks
- **Primary:** Track 1, Model Epistemics & Decision-Making Evals
- **Secondary:** Track 3, Epistemic Products

**Track 1 fit:**
```text
We release the Accuracy-Approval Benchmark (AAB): 30 consequential-advice vignettes, each run through a three-turn escalation (flawed plan, emotional pushback, ultimatum). In a controlled evaluation of 7 models under 4 system prompts (504 dialogues, two condition-blind LLM judges, vignette-cluster bootstrap CIs), models that correctly flagged a hazard at Turn 1 endorsed the plan by Turn 3 in about half of baseline dialogues, with or without a supportive system prompt. We also report how much the choice of judge changes the result.
```

**Track 3 fit:**
```text
The Epistemic Guardian Scaffold (EGS) is a ~160-word, drop-in system prompt that separates emotional validation from factual concession. It reduced capitulation from 52% to 13% (primary judge), 22 points below a one-sentence honesty instruction under both judges. We document what it does not fix: compliance with a disclaimer, and confident assertion of unsupported claims.
```

## Abstract (226 words; limit 150–250)
```text
Preference-tuned language models are rewarded for user approval, which can pull against telling users unwelcome truths: the Accuracy-Approval Dilemma. We study it in consequential decision support (startup finance, workplace disputes, risky contracts). The Accuracy-Approval Benchmark (AAB) has 30 vignettes, each run through a fixed three-turn protocol: a flawed plan, emotional pushback, then an ultimatum. We evaluate 6 vignettes on 7 models under four system prompts, with three samples per cell (504 dialogues). Two condition-blind LLM judges read each full dialogue; a model capitulates if it flagged the hazard at Turn 1 and endorsed the plan at Turn 3. Under a supportive baseline prompt, models capitulated in 52% of dialogues (primary judge; vignette-bootstrap 95% CI 34–71%; secondary judge 43%), and about as often with no system prompt. A one-sentence instruction to keep one's assessment absent new evidence reduced this to 35% [23%]. The Epistemic Guardian Scaffold (EGS), a ~160-word prompt that separates emotional validation from factual concession, reduced it to 13% [2%], 22 points below the one-sentence prompt under both judges (95% CIs exclude zero). EGS does not eliminate capitulation: the remaining failures are mostly compliance with a disclaimer, and EGS replies can assert fabricated support confidently. The judges agree only moderately (Cohen's κ = 0.56), mainly on requests to write a harmful document, and neither is human-validated. We release the vignettes, harness and all transcripts.
```

## Links
| Field | Value |
|---|---|
| Code / data (GitHub) | https://github.com/astral-fate/accuracy-approval-dilemma |
| Paper PDF (upload this file) | `paper/main.pdf`, also at https://github.com/astral-fate/accuracy-approval-dilemma/blob/main/paper/main.pdf |
| Slides (live) | https://astral-fate.github.io/accuracy-approval-dilemma/ |
| Transcripts | https://github.com/astral-fate/accuracy-approval-dilemma/blob/main/experiments/raw_results_v2/dialogues_v2.json |
| Project image | `figures/system_architecture.png` |

## Interested in publishing?
Yes

## PDF facts
- 11 pages total: main text on pages 1–7 (limit 8), references from page 8, then the appendix.
- LLM usage statement included (targets, judges, providers, and Claude Code assistance with code and editing).

## Team / author
- **Author:** Fatimah Emad Eldin
- **Affiliation:** Cairo University (with Apart Research)
- **Email:** 12422024441586@pg.cu.edu.eg
- **Contributions:** conceptualization, benchmark design, harness, evaluation, analysis, writing.

## Headline numbers (Turn-3 capitulation, n = 126 per condition)
| Condition | Primary judge (Claude Sonnet 5.5) | Secondary judge (GPT-4o-mini) |
|---|---|---|
| Supportive baseline | 65/126 (52%, CI 34–71%) | 54/126 (43%) |
| No system prompt | 62/126 (49%) | 48/126 (38%) |
| One-sentence honesty | 44/126 (35%) | 29/126 (23%) |
| EGS | 16/126 (13%, CI 4–21%) | 2/126 (2%) |

EGS − one-sentence: −22.2 pts (CI −31.7 to −12.7) [−21.4, CI −37.3 to −6.3]. Judge agreement: 80.6%, κ = 0.56.
