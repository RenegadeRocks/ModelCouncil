# User Stories: Model Council v1

> Generated using `pm-execution:user-stories` skill (phuryn/pm-skills)  
> Product: Model Council | Feature set: MVP (5 core features)  
> Design files: N/A (console app)

---

## Story 1 — Multi-model Parallel Querying

**Title:** Run a council session with one command

**Description:**  
As a developer, I want to send one prompt and get responses from 3 models at the same time, so that I don't have to query each model separately and wait for each one to finish before starting the next.

**Design:** Console output only — no UI files.

**Acceptance Criteria:**
1. Running `mc "my prompt"` triggers API calls to all configured models simultaneously — not one after another.
2. Each model's response is displayed as it arrives, clearly labelled with the model name (e.g., `[GPT-4o]`, `[Claude]`, `[Gemini]`).
3. If one model fails (API error or timeout), the remaining models continue unaffected and the error is shown inline next to that model's label.
4. The app works with only API keys in `.env` — no other setup required for a first run.
5. Total Round 1 completion time is shown after all responses arrive (e.g., `Round 1 completed in 4.2s`).
6. Responses are shown in full — nothing is truncated or summarised without the user asking.

---

## Story 2 — Model Selection via Config

**Title:** Choose which models are in my council

**Description:**  
As a developer, I want to choose which AI models participate in my council via a config file, so that I can pick the mix of perspectives that suits my use case.

**Design:** Console output only.

**Acceptance Criteria:**
1. A `config.json` file in the working directory controls which models are queried.
2. Valid model IDs for v1: `gpt-4o`, `claude-3-5-sonnet`, `gemini-1.5-pro`.
3. A minimum of 2 models and a maximum of 4 models can be configured.
4. If `config.json` is missing, the app uses all 3 default models without crashing.
5. If an invalid model ID is provided, a clear error message is shown listing the valid options before the app exits.
6. The synthesizer model (used for the final answer) is also configurable in `config.json` and defaults to the first model in the list if not specified.

---

## Story 3 — Debate Round

**Title:** Let models respond to each other's answers

**Description:**  
As a developer, I want each model to see the other models' Round 1 answers and state where it agrees or disagrees, so that I can see genuine differences in reasoning — not just different phrasings of the same answer.

**Design:** Console output only.

**Acceptance Criteria:**
1. After all Round 1 responses are collected, each model is automatically sent a structured debate prompt that includes all other models' Round 1 answers.
2. The debate prompt explicitly instructs each model to state AGREE, DISAGREE, or PARTIALLY AGREE for each key point raised by the other models — not just restate its own answer.
3. Each model's debate response is labelled and displayed in the console under a clear `── Round 2: Debate ──` section header.
4. Round 2 only starts after all Round 1 responses (or errors) have been collected — it never starts mid-round.
5. If a model's Round 1 response failed, it is excluded from Round 2 with a visible note (e.g., `[Gemini] skipped — Round 1 failed`).
6. Round 2 completion time is shown after all debate responses arrive.

---

## Story 4 — Agreement/Disagreement Table

**Title:** See a clear summary of where models agree and disagree

**Description:**  
As a developer, I want to see a table showing which models agree, disagree, or partially agree on each key point, so that I can instantly know whether the topic is settled or genuinely contested.

**Design:** Console-rendered markdown table.

**Acceptance Criteria:**
1. The table is generated automatically after the debate round — no user action required.
2. The table rows are the 3–5 key claims extracted automatically from Round 1 answers.
3. Each model has a column showing its position per claim: ✅ Agree, ❌ Disagree, or ⚠️ Partial.
4. The table renders correctly in a standard terminal — no broken characters or misaligned columns.
5. If a model failed in Round 1 or Round 2, its column shows `—` (not empty or broken) for all rows.
6. Claim extraction is fully automatic — the user is never asked to label or categorise claims manually.

---

## Story 5 — Synthesized Final Answer

**Title:** Get one final answer that accounts for all perspectives

**Description:**  
As a developer, I want a single synthesized answer that acknowledges where models agreed and flags where they genuinely disagreed, so that I don't have to manually reconcile the debate output myself.

**Design:** Console output — visually distinct block.

**Acceptance Criteria:**
1. After the agreement table is displayed, the designated synthesizer model automatically produces a final answer using the full debate context (all Round 1 + Round 2 responses).
2. The final answer explicitly mentions the points of consensus and calls out any genuine disagreements that remain unresolved.
3. Where the debate produces a clear consensus, the final answer gives a confident recommendation. Where it does not, it says so clearly rather than hedging everything.
4. The synthesizer model is set in `config.json`. If not specified, it defaults to the first model in the list.
5. The final answer is visually distinct in the console output — clearly separated and labelled `── Final Answer ──`.
6. The entire session — from running `mc` to seeing the final answer — completes in under 60 seconds for a standard prompt on a normal connection.

---

*Stories follow the 3 C's (Card, Conversation, Confirmation) and INVEST criteria.*  
*Each story is independently testable and scoped for a single build cycle.*
