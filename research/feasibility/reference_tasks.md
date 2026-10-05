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


---

## Task 1305

Task ID: 1305 (dev, hard)
Question: For account type H and MCC description "Eating Places and
Restaurants", what would be the average fee that the card scheme GlobalCard
would charge for a transaction value of 10 EUR? (EUR, 6 decimals)
Answer format: number rounded to 6 decimals

Note: rule matching follows manual section 5 (null or empty list = applies to
all values). Fee formula: fee = fixed_amount + rate * value / 10000.

Step 1:
Action: Look up the MCC code for "Eating Places and Restaurants" in
`merchant_category_codes.csv`
Expected intermediate result: 5812 (exactly one matching row)
Objectively checkable: Yes

Step 2:
Action: Filter `fees.json` rules: card_scheme == GlobalCard, account_type
contains H (or is wildcard), merchant_category_code contains 5812 (or is
wildcard)
Expected intermediate result: 46 rules, IDs: 5, 38, 92, 114, 140, 141, 160,
162, 192, 204, 221, 257, 267, 276, 280, 319, 325, 357, 359, 403, 427, 428,
456, 477, 498, 513, 556, 572, 612, 660, 666, 682, 688, 704, 709, 725, 741,
792, 813, 861, 888, 891, 892, 899, 917, 921
Objectively checkable: Yes (compare as a set)

Step 3:
Action: Compute the fee per matching rule for a 10 EUR transaction
Expected intermediate result: one value per rule ID, e.g. 5: 0.199,
38: 0.139, 725: 0.019, 921: 0.032 (full dict printed by the solution script).
Compare with a tolerance (1e-9), since floats print as e.g. 0.15000000000000002
Objectively checkable: Yes

Step 4:
Action: Average the 46 fees
Expected intermediate result: 0.123217
Objectively checkable: Yes

Step 5:
Action: Interpret "average fee" as the unweighted mean over matching rules
(not volume-weighted)
Expected intermediate result: unweighted mean; the only reading that
reproduces the public answer
Objectively checkable: No (an interpretation, validated only by the public
answer)

Final answer: 0.123217 (matches public answer)
Steps: 5 total, 4 checkable

---

## Running tally

| Task | Steps | Checkable | Ratio |
|------|-------|-----------|-------|
| 5    | 3     | 3         | 1.00  |
| 49   | 8     | 7         | 0.88  |
| 1305 | 5     | 4         | 0.80  |
| **Total** | **16** | **14** | **0.875** |


---

## Task 1753

Task ID: 1753 (dev, hard)
Question: What are the applicable fee IDs for Belles_cookbook_store in March 2023?
Answer format: comma-separated list of fee IDs

Note: "applicable" is not defined in the manual. Working definition (reproduces
the public answer): a rule applies if its merchant-level and monthly conditions
match AND at least one March transaction matches its transaction-level
conditions (card_scheme, is_credit, aci, intracountry).

Step 1:
Action: Look up the merchant in `merchant_data.json`
Expected intermediate result: account_type R, capture_delay '1' (falls in
the '<3' bucket), merchant_category_code 5942, acquirer lehman_brothers
Objectively checkable: Yes

Step 2:
Action: Filter payments to the merchant, year 2023, March
(day_of_year 60-90, non-leap year)
Expected intermediate result: 1277 transactions
Objectively checkable: Yes

Step 3:
Action: Compute March monthly volume (sum of eur_amount) and fraud level
(fraud volume / total volume, in %)
Expected intermediate result: 116436.32 EUR, 10.2488%
Objectively checkable: Yes

Step 4:
Action: Filter fee rules on merchant-level and monthly conditions
(account_type, MCC, capture_delay, monthly_volume, monthly_fraud_level;
null/empty = wildcard)
Expected intermediate result: 47 rules: 36, 51, 53, 64, 65, 80, 107, 123,
150, 163, 183, 231, 249, 276, 286, 304, 347, 381, 384, 394, 428, 454, 473,
477, 498, 536, 556, 572, 595, 608, 626, 631, 678, 680, 709, 725, 741, 813,
849, 861, 868, 871, 892, 924, 939, 942, 960
Objectively checkable: Yes (compare as a set)

Step 5:
Action: Keep rules matching at least one March transaction
(card_scheme, is_credit, aci, intracountry)
Expected intermediate result: 34 rules: 36, 51, 53, 64, 107, 123, 150, 163,
231, 249, 276, 286, 347, 381, 384, 394, 428, 454, 473, 477, 536, 556, 572,
595, 608, 626, 680, 709, 725, 741, 813, 868, 939, 960
Objectively checkable: Yes (compare as a set)

Step 6:
Action: Interpret "applicable" (merchant-level match + at least one matching
transaction; refused transactions included)
Expected intermediate result: the definition above; the only one tested,
and it reproduces the public answer
Objectively checkable: No (interpretation, validated only by the public answer)

Final answer: the 34 IDs from step 5 (matches public answer as a set)
Steps: 6 total, 5 checkable

---

## Running tally

| Task | Steps | Checkable | Ratio |
|------|-------|-----------|-------|
| 5    | 3     | 3         | 1.00  |
| 49   | 8     | 7         | 0.88  |
| 1305 | 5     | 4         | 0.80  |
| 1753 | 6     | 5         | 0.83  |
| **Total** | **22** | **19** | **0.86** |


---

## Task 1871

Task ID: 1871 (dev, hard)
Question: In January 2023 what delta would Belles_cookbook_store pay if the
relative fee of the fee with ID=384 changed to 1?
Answer format: number rounded to 14 decimals

Note: "relative fee" maps to the `rate` field. Delta = new total fee - old
total fee over the transactions that rule 384 applies to; fixed_amount
cancels out. The public answer carries float noise (-0.94810300000017), so
compare with a tolerance (1e-9).

Step 1:
Action: Load merchant record and fee rule 384
Expected intermediate result: merchant R / capture_delay '1' / MCC 5942.
Rule 384: card_scheme NexPay, is_credit True, aci [C, B], fixed_amount 0.05,
rate 14; account_type, capture_delay, monthly_fraud_level, monthly_volume,
MCC and intracountry are wildcards
Objectively checkable: Yes

Step 2:
Action: Filter payments to the merchant, year 2023, January (day_of_year 1-31)
Expected intermediate result: 1201 transactions
Objectively checkable: Yes

Step 3:
Action: Compute January monthly volume and fraud level
(fraud volume / total volume, in %)
Expected intermediate result: 113260.42 EUR, 10.3131%
Objectively checkable: Yes

Step 4:
Action: Check that rule 384 matches the merchant/month conditions
Expected intermediate result: True (47 merchant/month rules match, including
384; the list is identical to March's 47). Trivially true here because every
merchant-level field of rule 384 is a wildcard
Objectively checkable: Yes

Step 5:
Action: Find January transactions that rule 384 applies to
(NexPay, credit, ACI in {C, B})
Expected intermediate result: 12 transactions, total volume 729.31 EUR
Objectively checkable: Yes

Step 6:
Action: Compute old and new fee totals over those 12 transactions
(rate 14 -> 1) and the delta
Expected intermediate result: old total 1.621034, new total 0.672931,
delta -0.948103 (closed form: (1 - 14) * 729.31 / 10000)
Objectively checkable: Yes (tolerance 1e-9)

Step 7:
Action: Interpret the question ("relative fee" = rate; delta = new - old;
only the affected transactions)
Expected intermediate result: as stated in the note above
Objectively checkable: No (interpretation, validated only by the public answer)

Final answer: -0.94810300000017 (matches public answer within 1e-9)
Steps: 7 total, 6 checkable

---

## Running tally

| Task | Steps | Checkable | Ratio |
|------|-------|-----------|-------|
| 5    | 3     | 3         | 1.00  |
| 49   | 8     | 7         | 0.88  |
| 1305 | 5     | 4         | 0.80  |
| 1753 | 6     | 5         | 0.83  |
| 1871 | 7     | 6         | 0.86  |
| **Total** | **29** | **25** | **0.86** |