# Scoring Model

Version 1.0 — <date>

Two scores per role. **Fit** answers how much the candidate wants the role. **Winnability** answers how likely they are to get it. **Priority** is the product, and it decides where the next hour goes, not what they would accept.

The pipeline stores only six component scores per role (0–5): `senScore`, `domScore`, `locScore`, `evScore`, `lvlScore`, `rteScore`. Fit, Winnability, Priority and band are computed from those six. Never store the derived numbers.

---

## Fit (0-100)

    Fit = min( 10*Sen + 5*Dom + 5*Loc , cap[Sen] )

Weights: seniority 50, domain 25, location 25. Adjust the weights only deliberately, and log it below.

### Seniority of mandate (weight 50)

Measures the seniority of the kind of mandate the candidate is looking for. Seniority in a mandate they are not looking for does not count.

| 5 | <the target level and above> |
| 4 | <one step below> |
| 3 | <two steps below> |
| 2 | <three steps below> |
| 1 | <individual contributor in the target function> |
| 0 | <individual contributor outside the target function> |

**Score the role that is on the table.** A promised upgrade or a role still being shaped is scored at what is specified today and flagged in the card's detail.

### Domain (weight 25)

Scores the end market the role serves, not the vendor category.

| 5 | <core domain> |
| 4 | <adjacent domains> |
| 3 | <transferable domains> |
| 2 | <generic, or employer not disclosed> |
| 1 | <far from the candidate's experience> |
| 0 | <actively avoided> |

### Location (weight 25)

| 5 | <daily commute or fully remote> |
| 4 | <further, still daily> |
| 3 | <hybrid with a weekly commute; also the default when the on-site policy is unknown> |
| 2 | <on-site, but explicitly negotiable> |
| 1 | <relocation or outside the practical zone> |

### Seniority cap

| Sen 0 | Fit capped at 25 |
| Sen 1 | Fit capped at 45 |
| Sen 2 | Fit capped at 60 |
| Sen 3+ | no cap |

### Bands

| A | 80-100 | Apply properly: tailored CV, cover letter, warm route. |
| B | 65-79 | Apply with standard tailoring. |
| C | 50-64 | Only with a warm intro, or when the pipeline thins out. |
| D | below 50 | Do not apply. Keep the company on the radar if the company itself is attractive. |

---

## Winnability (0-100)

    Win = ( 0.50*Evidence + 0.25*LevelRead + 0.25*Route ) * 20

### Evidence (weight 50)

| 5 | Every must-have has a named proof point. |
| 4 | One soft gap, explainable in a cover letter. |
| 3 | A real gap that adjacent experience partly covers. |
| 2 | A hard gap that a domain-native candidate closes for free. |
| 1 | The core of the role is outside the track record. |

### Level read (weight 25)

| 5 | Level symmetric. |
| 4 | Half a notch off, invisible in practice. |
| 3 | One notch off, explainable. |
| 2 | Two notches off, reads as over- or underqualified. |
| 1 | The level mismatch alone will filter the candidate out. |

### Route (weight 25)

| 5 | Warm intro or a live conversation already running. |
| 4 | Contact accepted, conversation opened. |
| 3 | Hiring manager identified and contacted. |
| 2 | Contact identified, nothing sent, or a recruiter with no name behind the posting. |
| 1 | Cold application into a large pool, no visible entry. |

---

## Priority

    Priority = Fit * Win / 100

## Flags, not criteria

Noted on the card, kept out of the score: company viability, compensation band, what the company really is underneath the product line, <the candidate's own flags>.

## Change log

- **1.0 (<date>)** — First version.
