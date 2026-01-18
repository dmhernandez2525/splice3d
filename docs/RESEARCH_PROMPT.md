# Splice3D Competitive Research Prompt

> Use this prompt with a research agent or AI assistant to gather market intelligence on multi-color 3D printing solutions.

---

## Research Objective

Analyze the competitive landscape for multi-color/multi-material 3D printing solutions, with focus on filament splicers and tool changers. The goal is to identify:

1. Must-have features for market viability
2. Pain points users experience with existing solutions
3. Opportunities for Splice3D differentiation
4. Technical approaches that work well (or fail)

---

## Research Prompt

```
You are a market research analyst specializing in 3D printing hardware and software. Conduct comprehensive research on the multi-color 3D printing ecosystem, focusing on filament splicing and multi-material solutions.

## Part 1: Competitor Deep Dive

### 1.1 Mosaic Manufacturing (Palette)

Research the Palette product line (Palette 3, Palette 3 Pro):

- What is the current pricing and feature set?
- How does the splicing mechanism work technically?
- What is Canvas slicer and how does it integrate?
- What are common user complaints on Reddit, forums, and reviews?
- What is the typical waste percentage (purge/transition)?
- How reliable is the "ping" system for print synchronization?
- What materials are officially supported?
- What is the learning curve for new users?
- Search: "Palette 3 review", "Palette 3 problems", "Canvas slicer issues"

### 1.2 Prusa Research (MMU)

Research the Multi Material Upgrade (MMU2S, MMU3):

- What improvements did MMU3 bring over MMU2S?
- What are the most common failure modes?
- How does the filament tip shaping work?
- What is the typical reliability (successful tool changes %)?
- How long does a typical 5-color print take vs single color?
- What is the purge tower waste like?
- Search: "MMU3 reliability", "MMU2S problems", "Prusa MMU tips"

### 1.3 BigBrain3D (3DChameleon)

Research the 3DChameleon system:

- How does the Y-splitter mechanism work?
- What printers is it compatible with?
- What are typical user experiences?
- How does it compare to Palette on waste?
- What is the price point and value proposition?
- Search: "3DChameleon review", "3DChameleon vs Palette"

### 1.4 ERCF (Enraged Rabbit Carrot Feeder)

Research this open-source MMU alternative:

- What is the current version and active development status?
- What printers/firmware does it support (Klipper requirement)?
- What is the build complexity and cost?
- How does reliability compare to commercial solutions?
- What does the community look like (Discord, GitHub)?
- Search: "ERCF build guide", "ERCF reliability", "Enraged Rabbit problems"

### 1.5 Other Solutions

Briefly research:
- Bambu Lab AMS (Automatic Material System)
- Prusa XL tool changer
- E3D tool changer
- Mosaic Array (industrial)
- Any emerging startups in this space

## Part 2: User Pain Points Analysis

### 2.1 Common Complaints (search Reddit, forums, Facebook groups)

Search for and summarize common issues with:
- "multi color 3d printing waste"
- "palette 3 purge tower"
- "MMU reliability issues"
- "multi material printing failed"
- "filament change problems"

Categorize pain points into:
1. Waste/material consumption
2. Reliability/jamming
3. Print time increase
4. Calibration difficulty
5. Software/slicer issues
6. Cost of ownership

### 2.2 Feature Requests

What features do users commonly request that don't exist?
- Search: "wish multi color printing had"
- Search: "ideal MMU features"

### 2.3 Success Stories

What makes users happy with their multi-color setup?
- Search: "MMU3 finally working"
- Search: "Palette 3 worth it"

## Part 3: Technical Analysis

### 3.1 Splicing Approaches

Compare the technical approaches:

| Approach | Products | Pros | Cons |
|----------|----------|------|------|
| Real-time splicing | Palette | ? | ? |
| Tool changing | MMU, ERCF | ? | ? |
| Pre-splicing | Splice3D concept | ? | ? |
| Y-splitter | 3DChameleon | ? | ? |

### 3.2 Waste Reduction Techniques

Research how different systems minimize waste:
- Purge tower designs
- Purge into infill
- Transition towers
- Sparse purge
- Flush volumes optimization

### 3.3 Position Tracking Methods

How do systems track filament position?
- Stepper counting (most common)
- Encoder wheels
- Optical sensors
- The Mosaic "ping" system

## Part 4: Market Opportunity Analysis

### 4.1 Market Size

Estimate the market for multi-color solutions:
- Number of 3D printers sold annually
- Percentage of users interested in multi-color
- Price sensitivity research

### 4.2 Underserved Segments

Identify user groups not well-served by current solutions:
- Non-Prusa printer owners
- High-waste-sensitive users
- Complex multi-color print makers (1000+ changes)
- Print farm operators
- Educational institutions

### 4.3 Pricing Analysis

What are users willing to pay?
- DIY kit pricing expectations
- Commercial unit pricing
- Recurring costs (consumables)

## Part 5: Recommendations for Splice3D

Based on research, provide:

1. **Must-Have Features** (table stakes for market entry)
   - List features that any solution must have

2. **Differentiators** (unique value proposition)
   - What can Splice3D do that others cannot?

3. **Avoid These Mistakes** (learn from competitors)
   - What failures should Splice3D learn from?

4. **Community Building**
   - How have successful open-source 3D printing projects built community?
   - Examples: Voron, ERCF, Klipper

5. **Go-to-Market Strategy**
   - What would a good launch strategy look like?
   - Early adopter identification
   - Documentation and tutorial needs

## Output Format

Please provide research in the following format:

### Executive Summary (1 page)
- Key findings
- Market opportunity
- Top 3 recommendations

### Detailed Findings (organized by section above)
- Include sources/links where possible
- Include relevant quotes from users
- Include data/statistics where available

### Appendix
- List of sources consulted
- Raw quotes from forums/reviews
- Links to relevant discussions
```

---

## Supplementary Research Queries

### Reddit Communities to Search

- r/3Dprinting
- r/prusa3d
- r/voroncorexy
- r/ender3
- r/BambuLab
- r/3dprintingdeal

### Search Queries

```
Waste/Efficiency:
- "multi color printing waste reduction"
- "purge tower alternative"
- "flush volume optimization"
- "palette purge waste percentage"
- "AMS waste compared to"

Reliability:
- "MMU3 success rate"
- "Palette 3 reliability 2024"
- "ERCF jam rate"
- "multi material print failure"

User Experience:
- "easiest multi color setup"
- "multi color printing beginner"
- "palette vs mmu vs"
- "is AMS worth it"

Technical:
- "filament splicing mechanism"
- "how does palette work inside"
- "MMU tip shaping explained"
- "encoder wheel filament"
```

### YouTube Channels to Review

- CNC Kitchen (technical testing)
- Teaching Tech (tutorials/reviews)
- Made with Layers (Palette content)
- Nero3D (Voron/ERCF)
- ModBot (modifications)

### Forums and Communities

- Printables.com forums
- Prusa forums (forum.prusa3d.com)
- Voron Discord (#ercf channel)
- Facebook: "Mosaic Palette Users"
- Facebook: "Multi-Material 3D Printing"

---

## Research Output Template

Use this template to organize findings:

```markdown
# Splice3D Competitive Research Report

**Date:** [DATE]
**Researcher:** [NAME/AI]

## Executive Summary

[2-3 paragraph summary of key findings]

## Competitor Analysis

### Mosaic Palette
- **Strengths:**
- **Weaknesses:**
- **User Sentiment:**
- **Technical Details:**

### Prusa MMU
[Same format]

### 3DChameleon
[Same format]

### ERCF
[Same format]

### Other Solutions
[Same format]

## Pain Point Analysis

### Top 5 User Complaints (ranked by frequency)
1.
2.
3.
4.
5.

### Most Requested Features
1.
2.
3.

## Technical Comparison

| Feature | Palette | MMU | 3DChameleon | ERCF | Splice3D |
|---------|---------|-----|-------------|------|----------|
| Waste % |         |     |             |      |          |
| Reliability |     |     |             |      |          |
| Max colors |      |     |             |      |          |
| Price |           |     |             |      |          |
| Open source |     |     |             |      |          |

## Recommendations

### Must-Have Features
- [ ]
- [ ]
- [ ]

### Differentiation Opportunities
-
-
-

### Mistakes to Avoid
-
-
-

## Sources

1. [Source 1](URL)
2. [Source 2](URL)
...
```

---

## Follow-up Research Areas

After initial research, consider deep dives into:

1. **Splice Quality Testing**
   - What makes a strong filament splice?
   - Temperature, time, compression parameters
   - Material-specific considerations

2. **Position Tracking Innovation**
   - Encoder wheel designs
   - Alternative marking methods (dimples, RF, optical)
   - Drift compensation algorithms

3. **Slicer Integration**
   - How do Canvas, PrusaSlicer, Cura handle multi-color?
   - What metadata is needed for splicing?
   - Plugin architecture exploration

4. **Print Farm Applications**
   - What do print farms need from multi-color?
   - Automation requirements
   - Reliability thresholds

---

## Notes for Research Agent

- Prioritize recent information (2024-2026)
- Focus on user experiences over marketing claims
- Look for quantitative data (waste %, success rates, costs)
- Capture specific quotes that illustrate pain points
- Note any emerging technologies or startups
- Consider international markets (EU, Asia) if relevant
