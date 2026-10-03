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

## Task 49

Task ID: 49 (dev, easy)
Question: What is the top country (ip_country) for fraud?
A. NL, B. BE, C. ES, D. FR
Answer format: 'X. Y' (option letter and country code)

Note: "fraud" is ambiguous. Count, euro volume and rate give different
winners. Manual section 7 defines fraud as fraudulent volume / total volume.

Step 1:
Action: Load `payments.csv`
Expected intermediate result: shape = (138236, 21)
Objectively checkable: Yes

Step 2:
Action: Filter rows where `has_fraudulent_dispute` is True
Expected intermediate result: 10765 rows (sum of the per-country counts
in step 3; confirm with len())
Objectively checkable: Yes

Step 3:
Action: Fraud transaction count per `ip_country`
Expected intermediate result: NL 2955, BE 2493, IT 1652, SE 1627, FR 843,
LU 410, ES 407, GR 378 (top = NL)
Objectively checkable: Yes

Step 4:
Action: Fraud euro volume per `ip_country` (sum of `eur_amount`)
Expected intermediate result: BE 263833.85, ES 43531.87, FR 89135.03,
GR 39916.73, IT 182231.72, LU 44628.44, NL 329134.08, SE 169937.79
(top = NL)
Objectively checkable: Yes

Step 5:
Action: Total euro volume per `ip_country` (all rows)
Expected intermediate result: Total euro volume per country from the
`payments.csv` dataset.
Objectively checkable: Yes

Step 6:
Action: Fraud rate per country = step 4 / step 5
Expected intermediate result: BE 0.122686, ES 0.067503, FR TODO,
GR TODO, IT TODO, LU 0.067103, NL 0.121815, SE 0.084866 (top = BE)
Objectively checkable: Yes

Step 7:
Action: Choose the fraud definition (count vs volume vs rate)
Expected intermediate result: rate, per manual section 7; the only
definition that reproduces the public answer
Objectively checkable: No (a definitional decision, validated only by the manual and the final answer)

Step 8:
Action: Pick the top country among NL/BE/ES/FR and map to option letter
Expected intermediate result: BE -> option B
Objectively checkable: Yes

Final answer: B. BE (matches public answer)
Steps: 8 total, 7 checkable

---

## Running tally

| Task | Steps | Checkable | Ratio |
|------|-------|-----------|-------|
| 5    | 3     | 3         | 1.00  |
| 49   | 8     | 7         | 0.88  |