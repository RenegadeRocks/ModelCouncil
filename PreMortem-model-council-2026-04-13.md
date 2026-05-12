# Pre-Mortem Analysis: Model Council

**Date**: 2026-04-13  
**Product**: Model Council v1 (Console MVP)  
**Scenario**: Imagining launch in 14 days — what goes wrong?

> Generated using `pm-execution:pre-mortem` skill (phuryn/pm-skills)

---

## Tigers — Real Risks (Keep You Awake at Night)

### 🐯 Tiger 1: The debate prompt doesn't produce meaningful critiques
**Category**: Launch-Blocking  
**What happens**: Models receive each other's Round 1 answers and are asked to agree or disagree — but they produce polite, non-committal responses that all converge to "both answers have merit." The debate round adds noise, not signal. The agreement table becomes meaningless.  
**Why this is real**: LLMs are trained with RLHF to be helpful and agreeable. Asking them to "critique" another model's answer often produces diplomatic hedging, not genuine disagreement. This is the highest-risk assumption in the entire PRD.  
**Evidence**: Anecdotally, models tend to agree with each other when shown each other's answers unless the prompt is carefully engineered to force position-taking.

---

### 🐯 Tiger 2: Agreement table extraction is unreliable across diverse topics
**Category**: Launch-Blocking  
**What happens**: The meta-prompt that extracts key claims from Round 1 and maps each model's debate position works fine on structured topics (e.g., "best database for X") but fails on open-ended or opinion-based prompts (e.g., "what is the meaning of life"). Claims are vague, positions are ambiguous, and the table output is garbled or empty.  
**Why this is real**: Natural language claim extraction is inherently fragile. The meta-prompt will overfit to structured technical questions during development and break on diverse real-world inputs.

---

### 🐯 Tiger 3: API latency makes the tool feel unusable
**Category**: Fast-Follow  
**What happens**: Round 1 = 3 parallel calls (fast). Round 2 = 3 more parallel calls (fast). Synthesis = 1 call. But each call can take 5–15 seconds depending on response length and provider load. Total wall time can reach 30–45 seconds on a slow day. Users open another tab while waiting and forget to come back.  
**Why this is real**: Parallel calls help but don't eliminate latency. There is no streaming in v1, so the user sees nothing until a full response completes.

---

### 🐯 Tiger 4: One API fails silently and the user doesn't notice
**Category**: Fast-Follow  
**What happens**: Gemini rate-limits mid-session. The app continues with only GPT-4o and Claude. The table and synthesis are generated from 2 models, not 3 — but nothing in the output clearly tells the user this happened. They trust the "council" output without knowing it's incomplete.  
**Why this is real**: API errors and timeouts are common, especially when firing 3 simultaneous calls. Without explicit, visible error handling, the user has no idea their council was missing a voice.

---

## Paper Tigers — Overblown Concerns (Not Worth Losing Sleep Over)

### 📄 Paper Tiger 1: Users won't understand the agreement table
**Why it's overblown**: The primary user is a developer. A 3×5 table with ✅ / ❌ / ⚠️ is not cognitively demanding for this audience. The format mirrors what developers already read in CI dashboards and test reports. Dismiss this concern for v1 — revisit if the secondary (non-technical) segment is targeted.

---

### 📄 Paper Tiger 2: API costs per session will put users off
**Why it's overblown**: At current API rates, a full council session (Round 1 + debate + synthesis across 3 models) costs approximately $0.03–$0.08. Any developer with API key access is already spending at this level regularly. Cost is not a barrier for the primary segment.

---

### 📄 Paper Tiger 3: OpenAI or Anthropic will copy this immediately
**Why it's overblown**: Both companies have an incentive to promote their own models, not facilitate fair comparison with competitors. A debate tool that shows their model losing to a competitor is actively against their interests. This actually protects Model Council's niche — the incumbents won't build this.

---

## Elephants — Unspoken Worries (Nobody Is Talking About These)

### 🐘 Elephant 1: Multi-model consensus creates false confidence on shared blind spots
**What it is**: When all 3 models agree, users treat the answer as reliable. But all 3 models may share the same training bias, the same knowledge cutoff, or the same systematic error on a topic. Three models agreeing confidently on a wrong answer is worse than one model hedging.  
**Why nobody is discussing it**: The whole pitch of Model Council is "consensus = confidence." Questioning that premise feels like questioning the product itself.  
**What to investigate**: Add a caveat in the final answer output: *"Agreement across models does not guarantee factual accuracy — models may share the same training biases."* This is honest and builds trust rather than eroding it.

---

### 🐘 Elephant 2: The synthesizer model biases the final answer toward its own Round 1 position
**What it is**: The synthesizer receives the full debate context but it wrote one of the Round 1 answers. It has an inherent "home team" bias — it is more likely to treat its own Round 1 answer as the baseline and frame disagreements around it.  
**Why nobody is discussing it**: Synthesizer selection feels like a minor config detail. It isn't — it determines whose worldview the final answer is filtered through.  
**What to investigate**: Test whether rotating the synthesizer across sessions produces meaningfully different final answers on the same prompt. If it does, consider always using a separate "neutral" synthesis prompt that doesn't reveal which model is doing the synthesis.

---

### 🐘 Elephant 3: "Debate" is the wrong mental model — users expect argument, get academic discussion
**What it is**: The word "debate" implies adversarial disagreement. What the models actually produce is closer to a structured academic review — polite, qualified, often convergent. When users see models say "I agree with GPT-4o's point about X, and would add Y," it may feel anticlimactic.  
**Why nobody is discussing it**: The debate framing is baked into the product name and pitch. Questioning it feels like changing the concept entirely.  
**What to investigate**: A/B test the debate prompt framing. Try "critique" vs "debate" vs "challenge" and measure how often genuine disagreement surfaces. May just be a prompt engineering fix.

---

## Action Plans — Launch-Blocking Tigers

### Tiger 1: Debate prompt doesn't produce meaningful critiques

| Field | Detail |
|---|---|
| **Risk** | Debate round produces diplomatic hedging, not genuine position-taking |
| **Mitigation** | Spike test: manually run the debate prompt across 10 diverse topics in the API playground (before writing a single line of debate code). Test 3 prompt variants: (a) "agree/disagree/partial", (b) "steelman the other views, then state your position", (c) "you are playing devil's advocate — find the strongest objection". Pick the one that produces the most substantive disagreement. |
| **Owner** | Satbir (sole developer) |
| **Decision date** | Before starting Sprint 2 (debate round implementation) |

---

### Tiger 2: Agreement table extraction is unreliable

| Field | Detail |
|---|---|
| **Risk** | Meta-prompt for claim extraction + position mapping fails on diverse inputs |
| **Mitigation** | Test the extraction prompt on 20 sessions across 4 topic types: (1) technical/factual, (2) opinion/recommendation, (3) creative/open-ended, (4) contested/controversial. Build a hardcoded fallback: if extraction fails or produces fewer than 2 claims, show a plain "Model Positions" block with each model's self-stated position from the debate round instead of a table. |
| **Owner** | Satbir (sole developer) |
| **Decision date** | Before calling the table feature "done" |

---

## Pre-Mortem Summary

| Risk | Type | Urgency | Action Required |
|---|---|---|---|
| Debate prompt produces hedging not disagreement | Tiger | Launch-Blocking | Spike test 3 prompt variants before building |
| Agreement table extraction unreliable | Tiger | Launch-Blocking | Test on 20 diverse sessions; build fallback |
| Latency makes the tool feel slow | Tiger | Fast-Follow | Show progress indicators; set 15s timeout |
| Silent API failure corrupts council output | Tiger | Fast-Follow | Explicit error display; recount active models |
| Users misunderstand agreement table | Paper Tiger | — | Not a real risk for developer segment |
| API costs put users off | Paper Tiger | — | ~$0.05/session is not a barrier |
| Incumbents copy immediately | Paper Tiger | — | Incumbents won't build a fair competitor comparison |
| Consensus creates false confidence | Elephant | Investigate | Add bias caveat to final answer |
| Synthesizer biases final answer | Elephant | Investigate | Rotate synthesizer in tests; consider neutral synthesis |
| "Debate" framing disappoints users | Elephant | Investigate | A/B test prompt framing variants |

---

*Revisit this pre-mortem 2–3 days before first test session to verify Tiger mitigations are in place.*
