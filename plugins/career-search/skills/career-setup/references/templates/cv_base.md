# CV Base EN

*The only place CV wording lives. Every line has a fixed ID. A tailored CV is this base plus a list of changes per ID in a config. **Bold** in a line = emphasis in the PDF. ✅ = approved wording, ⏳ = still open. A trailing `*( ... )*` note is stripped from the PDF and may not contain a `)` itself.*

---

## Variants per vacancy type

One headline and one profile per vacancy type; the same letter belongs together. The headline level must match the posted title of the vacancies this variant is for.

| Variant | When | Headline |
|---|---|---|
| **A** | <vacancy type A> | ⏳ <Title> · <Domain> · <Strength> |
| **B** | <vacancy type B> | ⏳ <Title> · <Domain> · <Strength> |

- **[PRO-A]** ⏳ <Profile for variant A: 4–6 sentences, implicit first person, conclusion first.>
- **[PRO-B]** ⏳ <Profile for variant B.>

---

## Header

- **[HDR-01]** ✅ <Full Name>
- **[HDR-02]** ✅ <email>
- **[HDR-03]** ✅ <phone> · <City, Country>
- **[HDR-05]** ✅ <linkedin.com/in/...>
- **[HDR-04]** → see variants

## Core expertise

- **[TAG-01]** ⏳ <Tag>
- **[TAG-02]** ⏳ <Tag>

## Experience

### <Company (Parent group)> · <start year> — <end year>

- **[CO1-00]** ⏳ <Company note: what it sold, to whom, size, ownership.>

#### <Role title> · <start year> — <end year>

- **[R1-00b]** ⏳ <Role context line: scope, reporting line, team.>
- **[R1-01]** ⏳ <Bullet: verb first, result with a number.>
- **[R1-02]** ⏳ <Bullet.>

#### <Earlier role> · <start year> — <end year>

- **[R2-01]** ⏳ <Bullet.>

### <Earlier company> · <start year> — <end year>

- **[CO2-00]** ⏳ <Company note.>

#### <Role title>

- **[R3-01]** ⏳ <Bullet.>

## Education & certification

### Certifications

- **[EDU-01]** ⏳ <Certification> · <Issuer> · <Year>

### Degrees

- **[EDU-02]** ⏳ <Degree> · <School> · <years> · <Distinction>

## Selected projects · <year> – present

*(Optional featured block. Rendered when a config sets `ai_option: 2`; with option 1, a single line in Education (an EDU line without " · " separators) is shown instead.)*

- **[AI-01]** ⏳ **<Project>**: <what it does, what it shows>.

## Languages

- **[LNG-01]** ✅ <Language> — <Level>

## Tools & technical literacy

- **[TEC]** ⏳ <Tool> · <Tool> · <Tool>

<!--
Structure rules the renderer relies on:
- Experience: "### Company · years", then "#### Role · years". The first ID under a company is its company note; an ID ending in -00b is the role context line; a line starting "Stack ·" renders as a stack line.
- The experience section must be titled Experience, Expérience or Ervaring.
- Section titles are printed as section labels. Sections are recognised by the prefix of their first ID: TAG, EDU, AI, LNG, TEC.
- "### Subheading" inside a plain section groups the IDs under it (Education → Certifications / Degrees).
- Education entries: "Degree · School · Year [· Distinction]".
- Languages: "Language — Level". Tools: one TEC line, items separated by " · ".
- Never renumber IDs: configs refer to them. New lines get a new ID in the same prefix family.
-->
