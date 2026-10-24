from agent.answers import answers_match

# Public dev answer of task 1753 (34 fee IDs).
TASK_1753 = (
    "384, 394, 276, 150, 536, 286, 163, 36, 680, 939, 428, 813, 556, 51, 53, "
    "572, 960, 64, 709, 454, 595, 725, 473, 347, 477, 608, 868, 741, 231, 107, "
    "626, 249, 123, 381"
)


def test_exact_text_match():
    assert answers_match("NL", "NL")


def test_text_mismatch():
    assert not answers_match("IT", "NL")


def test_surrounding_whitespace_is_ignored():
    assert answers_match("  NL \n", "NL")


def test_text_is_case_sensitive():
    assert not answers_match("nl", "NL")


def test_option_format_is_strict():
    assert answers_match("B. BE", "B. BE")
    assert not answers_match("B.BE", "B. BE")
    assert not answers_match("BE", "B. BE")


def test_not_applicable():
    assert answers_match("Not Applicable", "Not Applicable")
    assert not answers_match("NL", "Not Applicable")


def test_number_within_tolerance():
    assert answers_match("-0.948103", "-0.94810300000017")


def test_number_outside_tolerance():
    assert not answers_match("0.1232", "0.123217")


def test_number_formatting_is_ignored():
    assert answers_match("0.1232170", "0.123217")


def test_list_order_is_ignored():
    assert answers_match("276,384,394", "384, 394, 276")


def test_full_task_1753_list_in_another_order():
    shuffled = ", ".join(reversed(TASK_1753.split(", ")))
    assert answers_match(shuffled, TASK_1753)


def test_list_missing_or_extra_item_fails():
    assert not answers_match("384, 394", "384, 394, 276")
    assert not answers_match("384, 394, 276, 999", "384, 394, 276")


def test_list_numeric_formatting_is_ignored():
    assert answers_match("384.0, 394", "384, 394")


def test_empty_list():
    assert answers_match("", "")
    assert not answers_match("", "384")
    assert not answers_match("384", "")


def test_fee_answer_is_exact_text():
    assert answers_match("E:13.57", "E:13.57")
    assert not answers_match("E: 13.57", "E:13.57")
    assert not answers_match("F:13.57", "E:13.57")


def test_nan_is_not_treated_as_a_number():
    assert not answers_match("nan", "NaN")