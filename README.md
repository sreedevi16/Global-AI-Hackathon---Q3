# Global-AI-Hackathon---Q3
# Protein Stability Lab: an Omnigent agentic lab

An AI lab built on **Omnigent** (Databricks × Hack-Nation, 7th Global AI Hackathon, Challenge 03: *Agentic Scientific Discovery*). Five specialist agents, coordinated by an Omnigent director, investigate one question and let each experiment decide the next.


---

## Research question

**How effectively can a compact, zero-shot protein language model (no fine-tuning) predict the stability effect (ΔΔG) of single point mutations in enzymes?**

- **Model:** a small ESM-2 checkpoint (e.g. 8M or 35M parameters), used zero-shot.
- **Score:** pseudo-log-likelihood ratio, `log p(mutant aa) - log p(wild-type aa)` at the mutated position.
- **Primary metric:** Spearman rank correlation (ρ) with experimental ΔΔG, reported with a 95% bootstrap confidence interval.
- **Stretch goal:** ρ > 0.60. This is a goal, not a pass/fail test. We report the real number whatever it is.
- **Baselines:** BLOSUM62 substitution score and a random score, so the result has a reference point.

## The bottleneck we attack

Comparing scoring methods, model sizes and protein subsets by hand is slow and easy to get wrong (for example, a flipped ΔΔG sign gives a misleading negative correlation). The lab automates the **literature → hypothesis → experiment → analysis → next experiment** loop under a fixed compute budget.

**Measured improvement:** `TODO` (e.g. "N experiment configurations in X minutes by the lab vs. an estimated Y minutes by hand = Z× faster"). Report the number you actually observed, and say how the manual time was estimated.

---

## How the lab works

```
              ┌─────────────────────────┐
              │  Omnigent director      │  coordinates, logs, asks the human
              └───────────┬─────────────┘
   ┌────────────┬─────────┼──────────┬─────────────┐
   ▼            ▼         ▼          ▼             ▼
literature → hypothesis → planner → runner → analysis
  agent        agent       agent     agent     agent
                              ▲                   │
                              └── result changes ─┘
                                  the next plan
```

| Agent | Decision it owns | Tools | Output |
|---|---|---|---|
| `literature_agent` | What is already known; realistic Spearman values; candidate datasets | web search | 3-5 cited sources, datasets flagged "to verify" |
| `hypothesis_agent` | Which claims are worth testing | none | 3 testable hypotheses with refutation criteria |
| `planner_agent` | Which experiment to run under the budget | none | ≥2 scored candidate tests, one chosen and justified |
| `runner_agent` | Executing the experiment | `run_python`, `pip_install` | Raw numbers, code, file names |
| `analysis_agent` | What the result means and what to test next | none | Verdict, comparison to baselines, failure regions, next experiment |

**The loop that changes the decision:** experiment 2 must be chosen *because of* what experiment 1 showed (for example a weak subset such as buried residues or a mutation type). See `research_log.md` after a run for the full trail.

### Design notes
- **Budget:** at most 2 experiments, ~20 minutes of compute each, smallest models first.
- **Shared record:** the director logs every step (inputs, outputs, numbers, file names) to `research_log.md`. Every script the runner executes is kept in `lab_runs/`.
- **Labelling:** agent-generated ideas are marked `HYPOTHESIS`. Agents are told never to invent numbers, datasets or citations.


---

## Data and models

| Resource | Purpose | Notes |
|---|---|---|
| ESM-2 (small checkpoint) | Zero-shot mutation scoring | Check size and license before download |
| Stability benchmark (e.g. ProteinGym stability assays, Tsuboyama mega-scale set, S669, FireProtDB) | Experimental ΔΔG | `TODO:` record which dataset you actually used, its license, and any filtering (e.g. enzymes only, single mutants only) |

> Check the ΔΔG **sign convention** of your dataset. The runner is instructed to state the convention it found and convert so that higher = more stable.

---

## Run it

Requires Python 3.12+ and a Gemini API key (from Google AI Studio).

```bash
# 1. Install Omnigent with Gemini (Antigravity SDK) support
pip install "omnigent[antigravity]"

# 2. Store your key (Antigravity -> Set Gemini API key), then quit setup
omnigent setup

# 3. Put these files in one folder:
#      protein_stability_lab_v2.yaml
#      lab_tools.py
cd path/to/that/folder

# 4. Let Omnigent import lab_tools.py, and make sure the server sees your key
export PYTHONPATH="$PWD"
export GEMINI_API_KEY='your-key-here'     # if the server cannot find your stored key
omnigent stop                             # restart the server so it picks these up

# 5. Start the lab and send the first message
omnigent run protein_stability_lab_v2.yaml
#   > Start the research. Use one dataset and the smallest ESM-2 model.
```

 `http://127.0.0.1:6767` shows sessions in the browser. 

**Known limits**
- The free Gemini tier allows very few requests per day per model (we hit a 20-request/day limit). A full lab run makes many model calls, so use a billed key or another provider.
- `503 "high demand"` errors come from Google's servers and are usually temporary; resend the message.
- Windows: Omnigent's native terminal wrappers are limited; the SDK-based `antigravity` harness is the supported route here.

---

## Files

| File | What it is |
|---|---|
| `protein_stability_lab_v2.yaml` | Agent specifications and rules: the director plus five sub-agents |
| `lab_tools.py` | The runner's `run_python` and `pip_install` tools |

---



