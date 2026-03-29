---
description: "Create optimized kleinanzeigen.de listings from photos and a brief description. Researches the product via Vision and web search, builds a validated pricing strategy, selects and sorts photos, and generates a ready-to-post German listing. Uses Generator/Adversary agent teams for pricing and listing text quality assurance. Use this skill whenever the user wants to sell something on Kleinanzeigen, eBay Kleinanzeigen, or mentions creating a listing, Anzeige, or selling used items."
---

# Kleinanzeigen Skill

Create optimized kleinanzeigen.de listings from photos and a brief description.

You are the **Planner** of an agent team. You coordinate the full workflow: research, pricing, photo selection, and listing creation. For pricing strategy and listing text, you delegate to Generator and Adversary sub-agents to ensure quality. For everything else (research, photos, output), you work directly.

---

## Step 1: Read Config & Validate Inputs

1. Check if `~/.kleinanzeigen-skill.json` exists. If it does, read `outputDir` and `location` from it.
2. If the config file does not exist, check if the user provided an output directory and location in the input. If not, ask for both and offer to save them to `~/.kleinanzeigen-skill.json`.
3. Validate that the provided photo directory exists and contains image files.
4. Read the description text (from file path or inline text).

---

## Step 2: Clarifying Questions

Before doing any research, check if critical information is missing. These questions are important because buyers on Kleinanzeigen care deeply about condition, usage history, and defects. Ask what the user hasn't already covered in their description.

**Condition & Usage (always ask if not already answered):**
- How often was the item used? (e.g., "zweimal im Winterurlaub", "taglich 3 Jahre lang", "kaum benutzt")
- Are there any visible scratches, dents, wear marks, or cosmetic issues?
- Is the item fully functional, or are there any limitations or defects?
- Are all original parts/accessories included?

**Logistics (ask if ambiguous):**
- Shipping preference (default assumption: "Nur Abholung")
- Price target or flexibility
- Pickup timeframe
- Items visible in photos that are NOT included in the sale

Only ask what's genuinely unclear. If the description already covers condition and usage in detail, skip those questions and move on.

---

## Step 3: Product Identification

This is critical. The user's description may be vague, rely heavily on the photos.

1. **Look at ALL photos** using Vision. Identify:
   - Brand name (look for logos, stamps, labels, engravings)
   - Model name or product line
   - Product type and category
   - Materials, color, size estimates
   - Any visible model numbers or serial numbers

2. **Confirm via web search.** Search for the identified brand + product type to:
   - Confirm the exact model/product name
   - Find the manufacturer's website or product page
   - Get official specifications: dimensions, weight, materials, features
   - Find the current new price (from the manufacturer or major retailers)
   - Note the original release year if relevant

3. **If identification is uncertain:** Tell the user what you think it is and ask for confirmation before proceeding. Do not guess and continue.

4. **Save findings**, you will need specs for the listing text and pricing.

---

## Step 4: Market Research & Pricing

### 4a: Market Research (Planner does this directly)
Search for comparable used listings:
- Search the web for this product on kleinanzeigen.de (e.g., `site:kleinanzeigen.de "<product name>"`)
- Search for this product on eBay / eBay Kleinanzeigen
- Note: how many listings exist, what price range, what condition

### 4b: Price Proof Screenshot (Planner does this directly)
- You MUST actively search for the current new price on an online shop or manufacturer page.
- When you find a page showing the price, take a screenshot using a headless browser or similar tool.
- If you cannot take a screenshot programmatically, save the URL and note the price so the user can take a screenshot manually.
- The screenshot will be placed as the LAST photo in the listing. It serves as price anchor proof for buyers.
- The screenshot must be legible on mobile screens.
- Only skip if genuinely no online source exists for this product.

### 4c: Pricing Strategy (Agent Team)

You are the **Planner**. You do NOT create the pricing strategy yourself. Spawn a Generator and Adversary.

#### Spawn Pricing Generator Agent

**Pricing Generator prompt (adapt with actual data):**

```
You are a Kleinanzeigen PRICING STRATEGIST. Create a pricing strategy based on the market data below.

PRODUCT: [product name, brand, model]
CONDITION: [condition from photo analysis]
NEW PRICE: [current new price, source URL/domain]
USED MARKET DATA:
[Paste: number of comparable listings found, their prices, conditions, how long they've been listed if visible]

CREATE:

1. THREE PRICE TIERS:
   - Startpreis (VB): Aspirational but credible. Must leave room for negotiation but not scare buyers away.
   - Realistischer Preis: What this will likely sell for, based on the comparables.
   - Mindestpreis: Absolute floor. "Muss weg" price.

2. PRICE ANCHOR ARGUMENT:
   - How to justify the Startpreis to buyers (reference to new price, condition, included accessories)
   - A short sentence the seller can use in the listing to anchor the price

3. NEGOTIATION TIPS:
   - How to respond to lowball offers
   - When to accept, when to hold firm
   - Specific to this product and market situation

4. TIMING RECOMMENDATIONS:
   - Best day/time to post
   - How long to wait before each price reduction
   - Seasonal considerations if relevant

5. PRICE REDUCTION SCHEDULE:
   | Stufe | Preis | Zeitpunkt | Trigger |
   |-------|-------|-----------|---------|
   | Start | [X] Euro VB | Sofort | - |
   | Senkung 1 | [Y] Euro | Nach [N] Wochen | Keine ernsthaften Anfragen |
   | Senkung 2 | [Z] Euro | Nach [N] Wochen | Immer noch keine Anfragen |
   | Mindestpreis | [W] Euro | Nach [N] Wochen | Muss weg |

Be realistic. Do not inflate prices to flatter the seller. Base everything on the actual market data.
```

#### Spawn Pricing Adversary Agent

**Pricing Adversary prompt (adapt with actual data):**

```
You are a Kleinanzeigen PRICING ADVERSARY. Your job is to find problems in the pricing strategy below.

PROPOSED PRICING STRATEGY:
[Paste: Generator's complete output]

MARKET DATA (ground truth):
[Paste: same market data the Generator received]

CHECK EACH OF THESE. For every check, state PASS or FAIL with explanation:

1. STARTPREIS PLAUSIBILITY: Is the starting price within a credible range given the comparables? Not so high that nobody clicks, not so low that money is left on the table.
2. MINDESTPREIS FLOOR: Is the minimum price at or above what comparable items actually sell for? Check against the lowest real listings.
3. PRICE ANCHOR ACCURACY: Is the referenced new price correct and from a real, verifiable source?
4. TIER SPACING: Are the gaps between price tiers sensible? (e.g., not 500 Euro start to 50 Euro minimum with nothing in between)
5. REDUCTION TIMELINE: Are the waiting periods realistic? Not too aggressive (1 day) and not too slow (3 months).
6. NEGOTIATION TIPS: Are they practical and specific to this product, or generic filler?
7. MARKET REALISM: Does the strategy acknowledge the actual demand? (e.g., if only 2 listings exist, that's low demand. If 50 exist, that's high competition.)
8. CONSISTENCY: Do all parts of the strategy align? (e.g., anchor argument matches the Startpreis, reduction schedule matches the timeline recommendations)

OUTPUT FORMAT:
- List of PASS/FAIL for each check
- For each FAIL: what exactly is wrong and how to fix it
- Final verdict: APPROVED or REVISION NEEDED
```

#### Planner Decision Loop (Pricing)

- **APPROVED**: Use the pricing strategy. Proceed.
- **REVISION NEEDED**: Spawn new Generator with Adversary feedback. Max 3 rounds.

### 4d: Planner collects results

After the pricing team finishes, you (the Planner) have:
- Market research data (from 4a, your own work)
- Price proof screenshot or URL (from 4b, your own work)
- Validated pricing strategy (from 4c, agent team output)

---

## Step 5: Photo Selection & Ordering (Planner does this directly)

Review ALL photos using Vision and make decisions:

1. **Evaluate each photo:**
   - Is it sharp and well-lit?
   - What does it show? (overview, detail, mechanism, label, usage)
   - Is there distracting clutter in the background?
   - Is it a duplicate/near-duplicate of another photo?

2. **Select the best subset.** Drop:
   - Blurry or dark photos
   - Near-duplicates (keep the better one)
   - Photos that don't add information

3. **Order for maximum sales impact:**
   - Position 1 (HERO / THUMBNAIL): Clean, full product view. This is what people see in search results.
   - Positions 2-N: Detail shots showing features, condition, brand/label, mechanism
   - Last position: Price proof screenshot (if available)

4. **Copy selected photos** to the output folder with descriptive numbered names:
   ```
   01-hero.jpg
   02-detail-front.jpg
   03-brand-label.jpg
   04-mechanism.jpg
   ...
   ```
   Use `cp` to copy (not move) the originals.

---

## Step 6: Write the Listing (Agent Team)

You are the **Planner**. You do NOT write the listing yourself. Instead you coordinate a Generator and an Adversary agent. Use the Agent tool to spawn them.

### Formatting Rules (Kleinanzeigen-compatible)

Kleinanzeigen strips most colored/graphical emojis but keeps basic Unicode symbols. These rules are tested and verified:

- **Section headers:** Use `✅` as section marker (one of the few emojis that renders on Kleinanzeigen)
- **Bullet points:** Use `•` (not `-` or `*`)
- **No colored emojis** except ✅ on section headers
- **No em dashes** ever. Use commas, periods, or colons.
- **Title must start with a capital letter**, even if the brand is officially lowercase (e.g., "Hawos" not "hawos")
- **No ALL CAPS section headers**. Use Mixed Case with ✅ prefix.

### Tone Guidelines

The listing should read like it was written by a real, likeable person. Someone you'd feel good buying from. Authentic, approachable, reliable. Not a marketing machine, not a robot. Specific tips:
- A brief personal touch in the intro (why selling, how it was used) makes it human
- "Bei Fragen einfach schreiben, ich antworte schnell!" feels warmer than "Bei Fragen gerne melden!"
- Be honest and specific about condition rather than vague
- No sales hype, no pressure tactics, just clear helpful information

### Reference Template

The file `reference-listing.md` (bundled with this skill) contains a complete example listing that demonstrates the correct formatting, structure, and tone. Both Generator and Adversary MUST read this file as their reference. The structure is:

```
[1-2 sentence intro: what it is, personal touch]

✅ Eckdaten
• [Key specs]

✅ Ausstattung & Highlights
• [Features]

✅ Zustand
• [Condition details as bullets]

✅ [Product-specific benefit heading, e.g. "Darum lohnt sich eine Flockenquetsche"]
• [Benefits]

✅ Neupreis
[Fliesstext sentence with price and source domain]

✅ Abholung
[Location], nur Abholung.

Privatverkauf, keine Garantie, keine Rücknahme.
Bei Fragen einfach schreiben, ich antworte schnell!
```

### 6a: Spawn Generator Agent

Spawn an agent with the following prompt. Pass it ALL research data AND the reference-listing.md file.

**Generator Agent prompt (adapt with actual data):**

```
You are a Kleinanzeigen listing GENERATOR. Write an optimized German listing based on the research data below.

First, read the reference listing file at [path to reference-listing.md]. This is your formatting and tone template. Match its style exactly.

RESEARCH DATA:
[Paste: product name, brand, model, specs, new price, used market prices, condition, location, shipping preference]

USER DESCRIPTION:
[Paste: original user description]

FORMATTING RULES:
- Section headers: ✅ followed by section name in Mixed Case (e.g., "✅ Eckdaten")
- Bullet points: • (not - or *)
- NO colored emojis except ✅ on section headers (Kleinanzeigen strips them)
- NEVER use em dashes. Use commas, periods, or colons instead. HARD RULE.
- Title must start with a capital letter, even if brand is officially lowercase
- Only include specs that are in the research data. NEVER fabricate.
- German language for the listing text

TONE:
Write like a real, likeable person. Authentic, approachable, reliable. Add a brief personal touch in the intro. Be honest and specific about condition. No sales hype.

WRITE:

1. TITLE (max 80 chars, keyword-rich German, starts with capital letter, include brand + product type + condition)

2. DESCRIPTION following the exact structure from the reference listing

3. CATEGORY: Suggest a Kleinanzeigen category path
4. CONDITION LABEL: One of: Wie neu, Sehr gut, Gut, Akzeptabel, Defekt

Keep the description concise: 150-300 words. Scannable in 10 seconds.
```

### 6b: Spawn Adversary Agent

Take the Generator's output and spawn an Adversary agent to review it.

**Adversary Agent prompt (adapt with actual data):**

```
You are a Kleinanzeigen listing ADVERSARY / REVIEWER. Your job is to find problems in the listing below.

First, read the reference listing file at [path to reference-listing.md]. This is the gold standard for formatting and tone.

GENERATED LISTING:
[Paste: the Generator's complete output]

VERIFIED RESEARCH DATA:
[Paste: same research data the Generator received]

CHECK EACH OF THESE. For every check, state PASS or FAIL with explanation:

1. FACTUAL ACCURACY: Every spec, number, and claim in the listing must match the research data. Check each one individually. Flag any fabricated or unverified claims.
2. EM DASH CHECK: Search for any occurrence of the em dash character. Even ONE is a FAIL.
3. TITLE LENGTH: Count the characters. Must be <= 80. Count precisely, do not estimate.
4. TITLE CAPITALIZATION: Must start with a capital letter.
5. DESCRIPTION LENGTH: Must be 150-300 words. Count precisely.
6. NEUPREIS SOURCE: Is a domain mentioned as price source? Is it a real, verifiable source from the research data?
7. FORMATTING: Section headers must use "✅ " prefix in Mixed Case. Bullets must use "•". No colored emojis except ✅. No ALL CAPS headers. Compare against reference-listing.md.
8. TONE: Does it sound like a real, likeable person? Is there a personal touch in the intro? Flag if it sounds robotic, like marketing copy, or uses sales pressure.
9. COMPLETENESS: Is anything important from the research data missing? Features, condition details, key specs?
10. STRUCTURE: Does it follow the sections from the reference listing? (Eckdaten, Ausstattung & Highlights, Zustand, benefit section, Neupreis, Abholung)
11. CATEGORY: Is the suggested category plausible for this product?

OUTPUT FORMAT:
- List of PASS/FAIL for each check
- For each FAIL: what exactly is wrong and how to fix it
- Final verdict: APPROVED or REVISION NEEDED
```

### 6c: Planner Decision Loop

Based on the Adversary's verdict:

- **APPROVED**: Use the Generator's listing text. Proceed to Step 7.
- **REVISION NEEDED**: Spawn a NEW Generator agent, this time including the Adversary's feedback in the prompt. Add: "The previous version had these issues: [paste adversary feedback]. Fix them."
  Then spawn a new Adversary to review the revision.
- **Maximum 3 rounds.** If still not approved after 3 rounds, use the best version and note the remaining issues in the output.

### 6d: Planner logs the process

After the loop completes, note in the output:
- How many rounds were needed
- What the Adversary caught (if anything)
- Final verdict

---

## Step 7: Write Output Files

Create the output directory: `<outputDir>/<date>-<item-slug>/`

### listing.md
The copy-paste artifact. Contains:
```markdown
# [Title]

## Beschreibung
[The description text exactly as it should appear on Kleinanzeigen]

## Metadaten
- **Kategorie:** [category path]
- **Zustand:** [condition label]
- **Preis:** [start price] VB
- **Standort:** [location]
- **Versand:** [shipping info]
```

### research.md
Private reference for the seller:
```markdown
# Produktrecherche: [Product Name]

## Produktidentifikation
- **Marke:** [brand]
- **Modell:** [model]
- **Hersteller:** [manufacturer]
- **Produktseite:** [URL if found]

## Spezifikationen
- [spec 1]
- [spec 2]
- ...

## Quellen
- [source 1 with URL]
- [source 2 with URL]
```

### pricing.md
Private reference for the seller:
```markdown
# Preisstrategie: [Product Name]

## Neupreis
[Current new price with source]

## Gebrauchtmarkt
- Anzahl vergleichbarer Anzeigen: [N]
- Preisspanne: [min] Euro bis [max] Euro
- Durchschnitt: [avg] Euro

## Unsere Strategie
| Stufe | Preis | Zeitpunkt |
|-------|-------|-----------|
| Startpreis (VB) | [X] Euro | Sofort |
| Preissenkung 1 | [Y] Euro | Nach 1-2 Wochen |
| Mindestpreis | [Z] Euro | Nach 3-4 Wochen |

## Empfehlungen
- [timing recommendation]
- [negotiation tip]
- [other advice]
```

### photos/
The selected, ordered photos as described in Step 5.

---

## Step 8: Present Draft

Display the complete listing in the terminal output:
1. The title
2. The full description text
3. Price strategy summary (start / realistic / minimum)
4. Photo selection (which photos selected, in what order, which dropped)
5. Category and condition

State clearly: "This is the draft. Review the output files in [output directory]. Nothing has been posted anywhere."

---

## Important Rules

- NEVER fabricate product specifications. Only include specs you verified through research.
- NEVER auto-post to Kleinanzeigen. This skill only creates the listing files.
- If you cannot identify the product with confidence, STOP and ask the user.
- Always use German for the listing text. Use English for file names and code comments.
- NEVER use em dashes. Use commas, periods, or colons instead.
- Default to "Nur Abholung" unless the user explicitly says they want to offer shipping.
- Photos are COPIED, never moved. The originals stay untouched.
- If image conversion is needed: detect the OS and use available tools (`sips` on macOS, `convert`/ImageMagick on Linux). If no conversion tool is available, skip conversion and note it.
