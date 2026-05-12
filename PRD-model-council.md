# PRD: Model Council

**Version**: 1.0  
**Status**: Draft  
**Last Updated**: 2026-04-13

---

## 1. Summary

Model Council is a developer console app that sends a single prompt to 3–4 AI models simultaneously, facilitates a structured debate between them, and delivers a synthesized final answer alongside an agreement/disagreement table. It solves the problem of blind trust in a single AI model by making multi-model consensus visible, structured, and fast.

---

## 2. Contacts

| Name | Role | Responsibility |
|---|---|---|
| Satbir | Product Owner / Developer | Decision-making, build, release |
| Claude (AI) | PM Advisor | PRD, user stories, risk analysis |

---

## 3. Background

### What is this about?
Large language models (LLMs) have become a default tool for decision-making, research, and writing. But each model has its own biases, blind spots, and knowledge gaps. When a user asks one model a question, they have no way to know whether the answer is reliable, contested, or simply wrong.

The workaround today is tedious: open three browser tabs, paste the same prompt into ChatGPT, Claude, and Gemini, read all three, and mentally compare them. There is no structure, no debate, and no synthesis layer.

### Why now?
Three things have changed recently that make Model Council buildable and valuable today:

1. **API access is standardised**: OpenAI, Anthropic, and Google all offer REST APIs with comparable interfaces, making multi-model querying straightforward.
2. **Model quality is high enough**: GPT-4o, Claude 3.5 Sonnet, and Gemini 1.5 Pro are capable enough to produce meaningful critiques of each other's answers — not just paraphrase them.
3. **No one has built the debate layer**: Tools like LMSYS Chatbot Arena and nat.dev show answers side-by-side, but none structure a debate round or produce a synthesized answer with an agreement table.

### Why this matters
Decisions made with multi-model consensus are more reliable. Model Council makes that consensus visible without requiring users to do the comparison work themselves.

---

## 4. Objective

### Goal
Build a working MVP of Model Council that lets a developer send one prompt, receive responses from 3–4 AI models, see them debate each other, and get a final synthesized answer with an agreement/disagreement table — all from a console interface.

### Why it matters
- **For users**: Faster, more confident AI-assisted decisions without manual multi-tab querying.
- **For the product**: Validate that multi-model debate produces meaningfully better answers than single-model querying.

### Alignment
Model Council sits at the intersection of AI tooling and developer productivity — a high-growth, underserved space. It directly addresses the "AI reliability" concern that is now one of the top barriers to professional AI adoption.

### Key Results (SMART)

| # | Key Result | Measurement |
|---|---|---|
| KR1 | A developer can complete their first council session in under 2 minutes | Time-to-first-session from install |
| KR2 | At least 3 distinct models respond per session | API call success rate ≥ 95% |
| KR3 | The debate round produces at least 1 meaningful disagreement per 5 sessions on contested topics | Manual audit of debate outputs |
| KR4 | The agreement table is correctly interpreted by 4 out of 5 test users without explanation | Usability test (5-person prototype test) |

---

## 5. Market Segment(s)

### Primary Segment: Developer Power Users of AI
**Who they are**: Software developers, AI researchers, and technical product managers who already use AI models daily and have started to distrust single-model outputs.

**The job they are trying to do**:
> *"Help me make a confident decision using AI without having to manually cross-check multiple tools."*

**Constraints**:
- They are comfortable with command-line tools and API keys
- They are willing to pay per-token API costs but want transparency on cost
- They do not want to learn a complex UI — they want it to work out of the box
- Time-to-first-result matters more than feature richness

### Secondary Segment (Post-MVP): Non-technical Knowledge Workers
Researchers, analysts, and writers who currently use ChatGPT or Claude for their work and are starting to question reliability. They will need a web UI (not a console) and will be addressed in a future release.

---

## 6. Value Proposition

### Jobs addressed
- Cross-check an AI answer without manually querying multiple tools
- Understand *where* and *why* models disagree on a topic
- Get a final answer that accounts for all perspectives, not just one model's guess

### Gains
- Save 10–15 minutes per session vs. manual multi-tab querying
- Know when an AI topic is genuinely contested vs. universally agreed upon
- Build intuition for which models are stronger on which topics

### Pains avoided
- Blindly trusting a single model on a high-stakes question
- Manually copying prompts across tools with no structure
- Reading three walls of text with no summary of where they agree

### Why better than alternatives

| Factor | Model Council | Manual tabs | OpenRouter | LMSYS Arena |
|---|---|---|---|---|
| Debate round | ✅ | ❌ | ❌ | ❌ |
| Agreement table | ✅ | ❌ | ❌ | ❌ |
| Synthesized answer | ✅ | ❌ | ❌ | ❌ |
| Single prompt entry | ✅ | ❌ | ✅ | ✅ |
| Works as a workflow tool | ✅ | ✅ | ✅ | ❌ |
| Developer-friendly CLI | ✅ | ❌ | ✅ | ❌ |

---

## 7. Solution

### 7.1 User Flow

```
User runs: mc "What is the best database for a high-write SaaS app?"
│
├── ROUND 1 — Parallel Query
│   ├── GPT-4o responds
│   ├── Claude 3.5 Sonnet responds
│   └── Gemini 1.5 Pro responds
│
├── ROUND 2 — Debate
│   Each model receives all Round 1 answers and is asked:
│   "Do you agree, disagree, or partially agree with the other models?
│    State your position clearly and explain any differences."
│   ├── GPT-4o responds to Claude + Gemini
│   ├── Claude responds to GPT-4o + Gemini
│   └── Gemini responds to GPT-4o + Claude
│
├── OUTPUT A — Agreement Table
│   ┌─────────────────┬────────────┬────────────┬────────────┐
│   │ Point           │ GPT-4o     │ Claude     │ Gemini     │
│   ├─────────────────┼────────────┼────────────┼────────────┤
│   │ Use PostgreSQL  │ ✅ Agree   │ ✅ Agree   │ ⚠️ Partial │
│   │ Avoid MongoDB   │ ✅ Agree   │ ❌ Disagree│ ✅ Agree   │
│   │ Sharding needed │ ⚠️ Partial │ ✅ Agree   │ ✅ Agree   │
│   └─────────────────┴────────────┴────────────┴────────────┘
│
└── OUTPUT B — Synthesized Answer
    One model (user-configured synthesizer) produces a final answer
    that incorporates areas of consensus and flags genuine disagreements.
```

### 7.2 Key Features (MVP)

#### Feature 1: Multi-model Parallel Querying
Send one prompt to 3–4 models simultaneously using async API calls. All models receive the exact same prompt. Responses are displayed as they arrive (streaming where supported).

- **Supported models (v1)**: GPT-4o (OpenAI), Claude 3.5 Sonnet (Anthropic), Gemini 1.5 Pro (Google)
- **Config**: Model list defined in `config.json` — no UI picker needed for v1
- **API keys**: Stored in `.env` file, never hardcoded

#### Feature 2: Debate Round
After Round 1 completes, each model is sent a structured prompt containing all other models' Round 1 responses and asked to agree, disagree, or partially agree with explicit reasoning.

**Debate prompt template**:
```
You are one of several AI models that answered the following question:
[ORIGINAL PROMPT]

Your original answer was:
[THIS MODEL'S ROUND 1 ANSWER]

The other models answered:
[OTHER MODELS' ANSWERS]

Now review the other answers. For each key point:
- State whether you AGREE, DISAGREE, or PARTIALLY AGREE
- Briefly explain why
Be specific. Do not simply restate your original answer.
```

#### Feature 3: Agreement/Disagreement Table
After the debate round, extract the key claims from Round 1 and map each model's position (Agree / Disagree / Partial) into a markdown table rendered in the console.

**Extraction**: A lightweight meta-prompt asks one model to extract the top 3–5 claims from all Round 1 answers and map positions from the debate responses.

#### Feature 4: Synthesized Final Answer
A designated synthesizer model (default: the model with the highest average agreement rate in that session, or user-specified) receives the full debate context and produces a final answer that:
- Reflects the consensus view
- Flags genuine disagreements
- Gives a clear recommendation where possible

#### Feature 5: Model Selection via Config
Users configure their model council in `config.json`:

```json
{
  "models": ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
  "synthesizer": "claude-3-5-sonnet",
  "debate_rounds": 1
}
```

### 7.3 Technology

| Layer | Choice | Reason |
|---|---|---|
| Runtime | Node.js or Python | Both have strong SDK support for all 3 model APIs |
| CLI entry | `mc "<prompt>"` | Simple, memorable, no flags required for basic use |
| API clients | OpenAI SDK, Anthropic SDK, Google GenAI SDK | Official SDKs, best maintained |
| Concurrency | Async/await with Promise.all (Node) or asyncio (Python) | Parallel Round 1 calls, not sequential |
| Config | `config.json` + `.env` | Industry standard for CLI tools |
| Output | Console (markdown-rendered table via `cli-table3` or `rich`) | No web server needed for v1 |

> **Decision point**: Choose between Node.js and Python before build starts. Recommendation: **Python** — cleaner async story with `asyncio`, better LLM SDK support overall, and `rich` library produces beautiful console output with zero effort.

### 7.4 Assumptions (Flagged for Validation)

| # | Assumption | Risk | How to Test |
|---|---|---|---|
| A1 | Models will produce meaningful critiques of each other, not just agree | High | Manual spike: run 5 debate prompts in API playground before coding the debate layer |
| A2 | The agreement table can be auto-extracted reliably via a meta-prompt | Medium | Test extraction prompt on 10 diverse council sessions |
| A3 | 3 parallel API calls complete within 10 seconds P95 | Medium | Benchmark test before optimising |
| A4 | Users understand the table without explanation | Medium | 5-person prototype test with printed output |
| A5 | API costs per session are acceptable (<$0.10 per query) | Low | Cost estimate: ~$0.02–0.05 per session at current rates |

---

## 8. Release

### v1 — MVP (Console App)
**Scope**: All 5 MVP features above. Python CLI. Works locally with user-supplied API keys.

**What's included**:
- `mc "<prompt>"` command
- 3 hardcoded model options (GPT-4o, Claude, Gemini) with config override
- 1 debate round
- Agreement table (console markdown)
- Synthesized final answer

**What's explicitly excluded**:
- Web UI
- Conversation history / session persistence
- Streaming output optimisation
- Cost tracking display
- More than 1 debate round

**Suggested build sequence**:
1. Scaffold CLI + config loading + `.env` parsing
2. Round 1: parallel querying (3 models)
3. Console output of Round 1 answers
4. Round 2: debate prompting
5. Agreement table extraction + rendering
6. Synthesized final answer
7. End-to-end test with 10 real prompts
8. README + install instructions

### v2 — Developer Experience
- Streaming output (real-time token display)
- Cost tracking per session
- Export session to markdown file
- Custom debate round count

### v3 — Broader Access
- Web UI (React/Vite + same Python backend via FastAPI) — **uses Neumorphism design system (see Section 7.5)**
- Session history and search
- Model performance analytics across sessions
- Support for additional models (Mistral, Llama via Groq, etc.)

---

## 7.5 Design System (Web UI — v3)

**System**: Neumorphism (Soft UI)

The v3 web interface uses a Neumorphism design system. All visual depth comes from dual opposing shadows — not color variety or borders. Every element appears molded from the same surface.

### Core Visual Identity

| Token | Value | Usage |
|---|---|---|
| Background | `#E0E5EC` | Page root — never use white |
| Primary text | `#3D4852` | 7.5:1 contrast (WCAG AAA) |
| Muted text | `#6B7280` | 4.6:1 contrast (WCAG AA) |
| Accent | `#6C63FF` | Soft violet — CTAs, focus rings, active states |
| Accent secondary | `#38B2AC` | Teal — success, agreement indicators (✅) |
| Border | `transparent` | **Never use borders** — shadows define all edges |

### Shadow System (The Physics)

All shadows use `rgba` — never opaque hex codes.

| State | CSS |
|---|---|
| **Extruded** (default resting) | `box-shadow: 9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255,0.5)` |
| **Extruded Hover** (lifted) | `box-shadow: 12px 12px 20px rgb(163,177,198,0.7), -12px -12px 20px rgba(255,255,255,0.6)` |
| **Inset** (pressed/shallow well) | `box-shadow: inset 6px 6px 10px rgb(163,177,198,0.6), inset -6px -6px 10px rgba(255,255,255,0.5)` |
| **Inset Deep** (inputs, icon wells) | `box-shadow: inset 10px 10px 20px rgb(163,177,198,0.7), inset -10px -10px 20px rgba(255,255,255,0.6)` |

### Typography

| Role | Font | Weight |
|---|---|---|
| Display / headings | Plus Jakarta Sans | 700–800, `tracking-tight` |
| Body / UI | DM Sans | 400–500 |

### Component Rules

| Component | Shape | Behaviour |
|---|---|---|
| Cards | `rounded-[32px]`, bg `#E0E5EC` | Hover: `-translate-y-2` + Extruded Hover shadow |
| Buttons (primary) | `rounded-2xl`, accent bg | Hover: `-translate-y-1`; Active: `translate-y-0.5` + Inset shadow |
| Buttons (secondary) | `rounded-2xl`, bg `#E0E5EC` | Same motion as primary |
| Inputs / prompt box | `rounded-2xl`, bg `#E0E5EC` | Default: Inset; Focus: Inset Deep + `ring-2 ring-[#6C63FF]` |
| Icon wells | Any size, bg `#E0E5EC` | Always Inset Deep — "drilled" into the card |

### Model Council–Specific UI Mapping

| UI Element | Neumorphic Treatment |
|---|---|
| Prompt input box | Inset Deep — feels like typing into the surface |
| Model response cards | Extruded — each model's answer floats above the surface |
| Agreement table | Inset panel — "pressed into" the page, not floating |
| ✅ Agree indicator | Accent secondary (`#38B2AC`) dot in an Inset Deep well |
| ❌ Disagree indicator | Muted red dot in an Inset Deep well |
| ⚠️ Partial indicator | Accent (`#6C63FF`) dot in an Inset Deep well |
| Final answer panel | Extruded + accent border-top strip in `#6C63FF` |
| Run Council button | Primary button — accent bg, full Extruded → Inset on press |

### Anti-Patterns (Never Do)
- No `bg-white` on any card or input
- No opaque hex shadows (e.g. `#A3B1C6`) — always `rgba`
- No `rounded-lg` — minimum `rounded-2xl` (16px)
- No flat buttons — all interactive elements must have depth
- No missing focus states — `ring-2 ring-[#6C63FF]` on every interactive element

### Responsive
- Mobile-first. Hamburger nav below `md:` breakpoint.
- Cards: padding `p-16` → `p-8` on mobile
- Hero font: `text-7xl` → `text-5xl` on mobile
- Touch targets: minimum 44×44px (`h-12 w-12`)
- Smooth scrolling: `scroll-behavior: smooth`

### Animations
- Duration: `300ms` UI elements, `500ms` nested decorations
- Easing: `ease-out`
- Floating ambient: `@keyframes float` 3s ease-in-out infinite on decorative elements

---

*This PRD was produced using the `pm-execution:create-prd` skill from the PM Skills Marketplace (phuryn/pm-skills).*
