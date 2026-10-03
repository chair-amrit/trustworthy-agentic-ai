# Reference Tasks: DABStep Feasibility Check

Purpose: test whether DABStep tasks support objective step-level correctness
checks, since the benchmark ships only final answers. Source: `adyen/DABstep`,
dev split (public answers available).

## Labeling rule

A step is **Checkable** only if an independent computation gives a single,
deterministic value (a count, shape, number, or set). It is **Not checkable**
if it rests on a judgment call, an ambiguous definition, or multiple equally
valid approaches.

Checkability = checkable steps / total steps

## Data

`payments.csv` (138,236 rows x 21 columns). Definitions come from
`manual.md` and `payments-readme.md`.

---

## Task 5

Task ID: 5 (dev, easy)
Question: Which issuing country has the highest number of transactions?
Answer format: country code only

Step 1:
Action: Load `payments.csv` into a dataframe
Expected intermediate result: shape = (138236, 21)
Objectively checkable: Yes

Step 2:
Action: Count transactions per `issuing_country`
Expected intermediate result: NL 29622, IT 28329, BE 23040, SE 21716,
FR 14175, LU 7171, ES 7109, GR 7074
Objectively checkable: Yes

Step 3:
Action: Take the country with the highest count
Expected intermediate result: NL
Objectively checkable: Yes

Final answer: NL (matches public answer)
Steps: 3 total, 3 checkable