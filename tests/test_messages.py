"""The content file is the thing most likely to be hand-edited, so it gets
the strictest tests: a typo here breaks the surprise at the worst moment."""

import pytest

from raksha import cli
from raksha import messages as M


def _flatten(value):
    if isinstance(value, str):
        return [value]
    out = []
    for item in value:
        out.extend(_flatten(item))
    return out


ALL_BLOCKS = [
    M.BOOT_LINES, M.BOOT_CHECKS, M.BOOT_PROMPT, M.BOOT_CONFIRMATION,
    M.INTRO_LINES, M.MAIN_MESSAGE, M.REASONS, M.LOVE_EXE_STEPS,
    M.LOVE_EXE_ERROR, M.LOVE_EXE_CAUSE, M.LOVE_EXE_DIAGNOSTICS,
    M.LOVE_EXE_FOOTER, M.MEMORIES, M.MEMORY_CLOSING, M.RANDOM_THOUGHTS,
    M.QUESTION_WARNING, M.QUESTION_HEADER, M.QUESTION, M.QUESTION_OPTIONS,
    M.ANSWER_YES, M.ANSWER_MAYBE, M.ANSWER_TIME, M.ANSWER_BACK,
    M.SEND_INTRO, M.SEND_PROMPT_HELP, M.SEND_PRIVACY_NOTICE, M.SEND_SUCCESS,
    M.SEND_SENT_LINES, M.SEND_FAILURE, M.SEND_CANCELLED, M.SEND_EMPTY,
    M.SEND_TOO_LONG, M.SECRET_MESSAGE, M.EXIT_STEPS, M.EXIT_MESSAGE,
    M.EXIT_FINAL,
]

SINGLE_LINES = [
    M.NAME, M.TAGLINE, M.SIGNATURE_LINE, M.MESSAGE_OPENING, M.MESSAGE_CLOSING,
    M.REASONS_LOADING, M.LOVE_EXE_FAILING_STEP, M.LOVE_EXE_STATUS,
    M.MEMORY_INTRO, M.QUESTION_PREPARING, M.SEND_PROMPT_LABEL,
    M.SEND_CONFIRM_TITLE, M.SEND_SUCCESS_TITLE, M.SECRET_TITLE,
    M.SECRET_CLOSING, M.MENU_TITLE, M.MENU_HINT, M.INVALID_CHOICE,
    M.CONTINUE_HINT,
]


def test_every_block_formats_without_keyerror():
    """A stray { or an unknown placeholder would crash mid-scene."""
    for block in ALL_BLOCKS:
        M.fmt(block)
    for line in SINGLE_LINES:
        M.fmt(line)


def test_fmt_substitutes_the_name():
    assert M.fmt("Welcome, {name}.") == "Welcome, %s." % M.NAME
    assert M.fmt(["{name}", "x"]) == [M.NAME, "x"]


def test_name_is_set():
    assert M.NAME.strip()


def test_minimum_content_counts():
    assert len(M.REASONS) >= 10
    assert len(M.RANDOM_THOUGHTS) >= 20
    assert len(M.MEMORIES) >= 1
    assert len(M.QUESTION_OPTIONS) == 4


def test_lines_stay_narrow_enough_to_centre():
    """Long lines wrap and destroy the centred layout."""
    for block in ALL_BLOCKS:
        for line in _flatten(block):
            assert len(M.fmt(line)) <= 54, "too long to centre: %r" % line


def test_menu_keys_are_unique_and_handlers_exist():
    keys = [key for key, _, _ in M.MENU_ITEMS]
    assert len(keys) == len(set(keys))
    for _key, _label, handler in M.MENU_ITEMS:
        assert handler == "exit" or handler in cli.SCENES


def test_menu_has_an_exit_and_a_send_option():
    handlers = [h for _, _, h in M.MENU_ITEMS]
    assert "exit" in handlers
    assert "send" in handlers


def test_secret_triggers_do_not_collide_with_menu_keys():
    keys = {key.lower() for key, _, _ in M.MENU_ITEMS}
    for trigger in M.SECRET_TRIGGERS:
        assert trigger.lower() not in keys


@pytest.mark.parametrize("block", [M.ANSWER_MAYBE, M.ANSWER_TIME, M.ANSWER_BACK])
def test_soft_answers_stay_gentle(block):
    """No option may read as pressure. Guard the words that would."""
    text = " ".join(block).lower()
    for word in ("but ", "should", "have to", "must ", "why not", "come on"):
        assert word not in text, "pressuring language in a soft answer: %r" % word
