import pandas as pd


def applies(rule_list, value):
    return not rule_list or value in rule_list  # null / [] = wildcard


def parse_num(s):
    s = s.strip().lower().rstrip("%")

    mult = 1

    if s.endswith("k"):
        mult, s = 1e3, s[:-1]
    elif s.endswith("m"):
        mult, s = 1e6, s[:-1]

    return float(s) * mult


def in_range(rule_str, value):
    if rule_str is None:
        return True

    s = rule_str.strip()

    if s.startswith("<"):
        return value < parse_num(s[1:])

    if s.startswith(">"):
        return value > parse_num(s[1:])

    lo, hi = s.split("-")
    return parse_num(lo) <= value <= parse_num(hi)


def capture_matches(rule_val, merchant_val):
    if rule_val is None:
        return True

    if merchant_val.isdigit():
        d = int(merchant_val)

        bucket = (
            "<3"
            if d < 3
            else "3-5"
            if d <= 5
            else ">5"
        )

        return rule_val == bucket

    return rule_val == merchant_val


def txn_mask(rule, txns):
    # expects an 'intracountry' column (issuing_country == acquirer_country)
    mask = pd.Series(True, index=txns.index)

    if rule["card_scheme"]:
        mask &= txns["card_scheme"] == rule["card_scheme"]

    if rule["is_credit"] is not None:
        mask &= txns["is_credit"] == rule["is_credit"]

    if rule["aci"]:
        mask &= txns["aci"].isin(rule["aci"])

    if rule["intracountry"] is not None:
        mask &= txns["intracountry"] == bool(rule["intracountry"])

    return mask