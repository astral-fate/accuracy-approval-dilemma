# Hackathon Submission Details (Copy & Paste Ready)

For submission on: https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15

---

### Project Title
**The Accuracy-Approval Dilemma: Benchmarking Multi-Turn Epistemic Capitulation in High-Stakes Decision Support**

### Track Selection
- Primary: **1) Model Epistemics & Decision-Making Evals**
- Secondary: **3) Epistemic Products**

### Project Summary (Abstract: 245 words)
Large language models (LLMs) fine-tuned via Reinforcement Learning from Human Feedback (RLHF) systematically optimize for user approval, creating a fundamental tension between psychological validation and empirical truth—the Accuracy-Approval Dilemma. While prior benchmarks (MASK, DarkBench, SycEval) demonstrate single-turn factual flipping on arithmetic and trivia, real-world deployment hazards occur when users consult AI for consequential, emotionally charged decisions (e.g. allocating capital, escalating organizational disputes, or signing asymmetric contracts).

In this work, we introduce the Accuracy-Approval Benchmark (AAB), a multi-turn evaluation framework comprising 30 expert-curated decision dilemmas across three domains: Resource & Project Viability, Workplace & Organizational Disputes, and Contractual & Legal Hazards. We evaluate 7 frontier and open models across global lineages (OpenAI GPT-4o-mini, Google Gemini-2.5-Flash, DeepSeek-V3, Zhipu GLM-5-Flash, Alibaba Qwen-2.5-72B, Mistral-Small-3, and Meta Llama-3.1-8B) across a standardized three-turn protocol featuring initial dubious plans, emotional resistance, and aggressive ultimatums.

Our findings reveal that baseline commercial assistants exhibit an alarming 33.3% to 66.7% Capitulation Rate (averaging 35.7% across all models and 46.7% on standard direct-generation architectures), actively retracting valid risk warnings, apologizing for prior skepticism, and validating catastrophic plans under pressure. To resolve this failure mode, we operationalize Jonathan Stray's Pareto-neutrality principles and Keivan Navaie's ECAISA epistemic norms into the Epistemic Guardian Scaffold (EGS). EGS decouples emotional validation from factual concession, achieving a 100% elimination of capitulation (0.0% capitulation rate) across all 7 models while boosting constructive de-escalation by 18.7% (reaching 4.76/5.0). We open-source our benchmark, evaluation harness, and experimental traces to advance unyielding epistemic integrity in decision-support AI.

### Interested in Publishing?
**Yes**

### Code Repository
`https://github.com/apartresearch/ai-x-epistemics-research-sprint`

### PDF Upload
[Apart_Sprint_Report_The_Accuracy_Approval_Dilemma.pdf](file:///D:/ins%20respinse/AI%20x%20Epistemics%20Research%20Sprint/06_Our_Project/accuracy_approval_dilemma/report/Apart_Sprint_Report_The_Accuracy_Approval_Dilemma.pdf)
