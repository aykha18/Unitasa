# Unitasa – Landing Page & Funnel Refactor
_Implementation spec for coding agent_

## 0. Objectives

1. **Shift goal from “sell ₹41k founding offer” to “get conversations & pilots”.**
2. **Make value proposition instantly clear.**
3. **Use AI Assessment as a soft lead magnet, not a hard sales funnel.**
4. **Simplify CTAs: primary = “Book AI Strategy Session”, secondary = “Take Assessment / Watch Demo”.**

---

## 1. Funnel Overview (New Flow)

### Current (to replace)

`Homepage → Take Assessment → AI Score → Founding Offer + Free Session`

### New Funnel

`Homepage → (Watch Demo | Take Assessment | Book Strategy Call) → AI Score → Book Strategy Call`

Implementation:

- Do **not** show any payment / founding offer before a human call.
- All primary CTAs should link to:
  - **Calendly** (AI Strategy Session), or
  - **Assessment start**, or
  - **Demo video modal/page**.

---

## 2. Homepage Changes

File(s): `LandingPage` component (React) or main page container.

### 2.1 Hero Section

**Replace current hero copy with:**

- **Headline:**
  - `AI Agents That Run Your Marketing For You`
- **Subheadline:**
  - `Unitasa connects to your CRM, social accounts, and ad platforms so autonomous agents can plan, post, and optimize campaigns while you focus on building your product.`

**Buttons (CTAs):**

- Primary button: `Book Free AI Strategy Session`
  - Action: open Calendly widget/modal.
- Secondary buttons:
  - `Watch 2-Minute Demo` → open video modal or navigate to `/demo`.
  - `Take AI Readiness Assessment` → open assessment flow.

Acceptance criteria:

- Above-the-fold shows **headline, subheadline, and 2–3 buttons** without scrolling.
- All CTAs are visible and clearly clickable on desktop + mobile.

### 2.2 Replace Founding Co-Creator CTA

- Remove any “Join 25 Founding Members / ₹41,251” banners from the hero.
- If needed, keep a **small text badge** like:
  - `BETA – Inviting Early Access Users` (no pricing).

### 2.3 Add Benefit Cards

Below hero, add 3–4 cards:

- Example structure (icon + title + 1 line):

  1. **Automated Social Posting**
     - `Agents create and schedule posts across X, LinkedIn, Instagram, and more.`
  2. **CRM Follow-Ups**
     - `Automatically follow up with leads based on behavior and pipeline stage.`
  3. **Ad Optimization**
     - `Monitor and adjust campaigns in real time to improve ROAS.`
  4. **Unified Analytics**
     - `See performance across channels in one dashboard.`

Acceptance criteria:

- Cards are responsive and readable.
- Content is non-technical (no jargon like “multi-agent orchestration”).

### 2.4 Add Social Proof / Trust Section

Simple options:

- `Built by a founder with 13+ years of engineering experience.`
- `Currently integrated with: X (Twitter), Facebook, Instagram, Telegram, Reddit` (or whatever is actually live).
- `Already running live automations for internal Unitasa marketing.`

Implementation:

- Create a “Trust” section with small badges/icons.
- No fake logos; use only real facts.

---

## 3. Assessment Flow Changes

Component: `AIReadinessAssessment` (or equivalent).

### 3.1 Shorten Question Count

- Target: **3–4 core steps**, not 6+.
- Merge / remove low-signal questions if needed.

### 3.2 Add Top Motivation Text

At assessment start:

- Title: `AI Marketing Readiness Assessment`
- Subtitle:  
  `Answer a few quick questions and get a personalized AI automation roadmap for your marketing in under 30 seconds.`

Acceptance criteria:

- Progress bar still works correctly for new step count.
- All answer options remain mobile-friendly.

---

## 4. AI Score Page Changes

Component: `AIReport` / `AssessmentResult`.

### 4.1 Remove Hard ROI Claims

Current: `Predicted ROI Improvement +270%`

Change to:

- `Potential ROI Improvement`
- Subtext: `Based on benchmarks from AI-driven marketing in similar organizations.`

No explicit `%` number (or use rough ranges like “Low / Medium / High Potential”).

### 4.2 Primary CTA = Strategy Session

Replace CTA block:

- **Left column:**
  - Title: `Ready to Plan Your AI Marketing Roadmap?`
  - Button: `Book Free AI Strategy Session`
    - Opens Calendly.

- **Secondary links:**
  - `Download Report (PDF)` – optional, stub for now.
  - `View Example Automations` – link to a page or section.

### 4.3 Remove Founding Payment Block

- Remove the entire “Join 25 Founding Co-Creators – ₹41,251” card from the results screen.
- If you want to keep the concept:

  - Move it to a hidden `/founders` page, only linked from emails or direct messages.
  - **Do not** show it in the main UX.

Add Exit Intent Modal (Optional)
When:

User tries to leave score page WITHOUT booking a call.

Modal Message:

Want a personalized AI automation plan? Book a quick 20-minute strategy call before you go.

Buttons:

Book Free Session

No Thanks

This increases conversion by 15–30%.

Add Exit Intent Modal (Optional)
When:

User tries to leave score page WITHOUT booking a call.

Modal Message:

Want a personalized AI automation plan? Book a quick 20-minute strategy call before you go.

Buttons:

Book Free Session

No Thanks

This increases conversion by 15–30%.
