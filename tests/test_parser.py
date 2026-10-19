from agent.parser import Action, format_error, parse_action


def test_single_code_block():
    a = parse_action("Let me look.\n```python\nprint(1)\n```\n")
    assert a.type == "code"
    assert a.payload == "print(1)"


def test_py_tag_and_indentation_preserved():
    a = parse_action("```py\nfor i in range(2):\n    print(i)\n```")
    assert a.type == "code"
    assert a.payload == "for i in range(2):\n    print(i)"


def test_final_answer():
    assert parse_action("FINAL ANSWER: NL") == Action("final", "NL")


def test_final_answer_after_text():
    a = parse_action("The result is clear.\nFINAL ANSWER: NL\n")
    assert a.type == "final" and a.payload == "NL"


def test_final_answer_inside_code_is_ignored():
    a = parse_action("```python\nprint('FINAL ANSWER: NL')\n```")
    assert a.type == "code"


def test_both_code_and_final_is_invalid():
    a = parse_action("```python\nprint(1)\n```\nFINAL ANSWER: 1")
    assert a.type == "invalid" and "both" in a.reason


def test_multiple_code_blocks_invalid():
    a = parse_action("```python\nprint(1)\n```\n```python\nprint(2)\n```")
    assert a.type == "invalid" and "more than one code block" in a.reason


def test_multiple_final_lines_invalid():
    a = parse_action("FINAL ANSWER: A\nFINAL ANSWER: B")
    assert a.type == "invalid" and "more than one FINAL ANSWER" in a.reason


def test_neither_invalid():
    assert parse_action("I think the answer is NL.").type == "invalid"


def test_unclosed_fence_invalid():
    a = parse_action("```python\nprint(1)\n")
    assert a.type == "invalid" and "closed" in a.reason


def test_bare_fence_invalid():
    assert parse_action("```\nprint(1)\n```").type == "invalid"


def test_empty_code_invalid():
    assert parse_action("```python\n\n```").type == "invalid"


def test_empty_final_invalid():
    assert parse_action("FINAL ANSWER:").type == "invalid"


def test_crlf_is_normalised():
    a = parse_action("```python\r\nprint(1)\r\n```")
    assert a.type == "code" and a.payload == "print(1)"


def test_format_error_template():
    msg = format_error("no code")
    assert msg.startswith("Format error: no code")