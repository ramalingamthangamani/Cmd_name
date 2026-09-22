"""End-to-end drive of the CLI with scripted keystrokes.

Every scene is played through, including invalid input, Ctrl+C and the
secret trigger, so a broken scene fails here rather than in front of her.
"""

import builtins

import pytest

from raksha import animation as anim
from raksha import api, cli
from raksha import messages as M


@pytest.fixture(autouse=True)
def instant(monkeypatch):
    """No delays, no cursor tricks, deterministic width."""
    monkeypatch.setattr(anim, "FAST", True)
    monkeypatch.setattr(anim, "sleep", lambda *_: None)
    monkeypatch.setattr(anim, "term_columns", lambda: 80)
    monkeypatch.setattr(anim, "clear", lambda: None)


class Script:
    """Feeds scripted answers to input(); raises Quit when exhausted."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.answers:
            raise EOFError
        return self.answers.pop(0)


def drive(monkeypatch, answers):
    script = Script(answers)
    monkeypatch.setattr(builtins, "input", script)
    return script


def no_network(monkeypatch):
    def explode(*a, **k):
        raise AssertionError("this scene must not touch the network")

    monkeypatch.setattr(api.urllib.request, "urlopen", explode)


# ---------------------------------------------------------------------------
# Boot and menu
# ---------------------------------------------------------------------------

def test_boot_reveals_the_name(monkeypatch, capsys):
    drive(monkeypatch, [""])
    no_network(monkeypatch)
    cli.boot()
    out = capsys.readouterr().out
    assert " ".join(M.NAME.upper()) in out
    assert "Identity confirmed." in out
    assert "Welcome, %s." % M.NAME in out


def test_menu_lists_every_option_and_exits(monkeypatch, capsys):
    drive(monkeypatch, ["9"])
    no_network(monkeypatch)
    cli.main_menu()
    out = capsys.readouterr().out
    for key, label, _ in M.MENU_ITEMS:
        assert "[%s]" % key in out
        assert M.fmt(label) in out
    assert "Connection closed." in out


def test_invalid_input_is_refused_then_recovers(monkeypatch, capsys):
    drive(monkeypatch, ["banana", "42", "9"])
    no_network(monkeypatch)
    cli.main_menu()
    out = capsys.readouterr().out
    assert out.count(M.INVALID_CHOICE) == 2
    assert "Connection closed." in out


def test_bare_enter_at_the_menu_is_not_scolded(monkeypatch, capsys):
    """Pressing Enter to look again should not read as a telling-off."""
    drive(monkeypatch, ["", "  ", "9"])
    no_network(monkeypatch)
    cli.main_menu()
    assert M.INVALID_CHOICE not in capsys.readouterr().out


def test_bom_and_carriage_returns_are_tolerated(monkeypatch, capsys):
    """PowerShell prefixes piped input with a BOM; it must not break choices."""
    drive(monkeypatch, ["﻿9"])
    no_network(monkeypatch)
    cli.main_menu()
    out = capsys.readouterr().out
    assert M.INVALID_CHOICE not in out
    assert "Connection closed." in out


def test_eof_exits_gracefully(monkeypatch):
    drive(monkeypatch, [])  # immediate EOF, as Ctrl+D / closed pipe
    no_network(monkeypatch)
    assert cli.run(["--skip-intro"]) == 0


def test_keyboard_interrupt_exits_gracefully(monkeypatch, capsys):
    def interrupt(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr(builtins, "input", interrupt)
    no_network(monkeypatch)
    assert cli.run(["--skip-intro"]) == 0
    assert "Goodnight" in capsys.readouterr().out


def test_version_and_help_do_not_start_the_experience(capsys):
    assert cli.run(["--version"]) == 0
    assert "raksha" in capsys.readouterr().out
    assert cli.run(["--help"]) == 0
    assert "Usage" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

def test_message_scene(monkeypatch, capsys):
    drive(monkeypatch, [""])
    no_network(monkeypatch)
    cli.scene_message()
    out = capsys.readouterr().out
    assert M.fmt(M.MAIN_MESSAGE[0]) in out
    assert M.fmt(M.MESSAGE_CLOSING) in out


def test_reasons_scene_shows_every_reason(monkeypatch, capsys):
    drive(monkeypatch, [""] * (len(M.REASONS) + 1))
    no_network(monkeypatch)
    cli.scene_reasons()
    out = capsys.readouterr().out
    for i in range(1, len(M.REASONS) + 1):
        assert "Reason #%02d" % i in out


def test_love_exe_fails_then_reports_running(monkeypatch, capsys):
    drive(monkeypatch, [""])
    no_network(monkeypatch)
    cli.scene_love_exe()
    out = capsys.readouterr().out
    assert "ERROR." in out
    assert "%s detected." % M.NAME in out
    assert M.LOVE_EXE_STATUS in out


def test_memory_lane_shows_each_memory(monkeypatch, capsys):
    drive(monkeypatch, [""] * (len(M.MEMORIES) + 2))
    no_network(monkeypatch)
    cli.scene_memories()
    out = capsys.readouterr().out
    for memory in M.MEMORIES:
        assert M.fmt(memory) in out


def test_random_love_repeats_until_back(monkeypatch, capsys):
    drive(monkeypatch, ["", "", "b"])
    no_network(monkeypatch)
    cli.scene_random_love()
    out = capsys.readouterr().out
    assert out.count("Random Thought #") == 3


def test_secret_scene(monkeypatch, capsys):
    drive(monkeypatch, [""])
    no_network(monkeypatch)
    cli.scene_secret()
    out = capsys.readouterr().out
    assert M.SECRET_TITLE in out
    assert M.fmt(M.SECRET_CLOSING) in out


@pytest.mark.parametrize("trigger", M.SECRET_TRIGGERS)
def test_secret_trigger_from_the_menu(monkeypatch, capsys, trigger):
    drive(monkeypatch, [trigger, "", "9"])
    no_network(monkeypatch)
    cli.main_menu()
    assert M.SECRET_TITLE in capsys.readouterr().out


# ---------------------------------------------------------------------------
# The question
# ---------------------------------------------------------------------------

def test_question_can_be_declined_at_the_warning(monkeypatch, capsys):
    drive(monkeypatch, ["n", ""])
    no_network(monkeypatch)
    cli.scene_question()
    out = capsys.readouterr().out
    assert M.fmt(M.QUESTION[0]) not in out
    assert M.ANSWER_BACK[0] in out


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("1", M.ANSWER_YES),
        ("2", M.ANSWER_MAYBE),
        ("3", M.ANSWER_TIME),
        ("4", M.ANSWER_BACK),
    ],
)
def test_every_answer_is_answered_warmly(monkeypatch, capsys, choice, expected):
    drive(monkeypatch, ["y", choice, ""])
    no_network(monkeypatch)
    cli.scene_question()
    out = capsys.readouterr().out
    for line in M.fmt(expected):
        if line:
            assert line in out


def test_question_rejects_nonsense_before_accepting(monkeypatch, capsys):
    drive(monkeypatch, ["y", "9", "zzz", "2", ""])
    no_network(monkeypatch)
    cli.scene_question()
    out = capsys.readouterr().out
    assert "Not one of the options." in out
    assert M.ANSWER_MAYBE[0] in out


# ---------------------------------------------------------------------------
# Send Me a Message
# ---------------------------------------------------------------------------

def sent_ok(monkeypatch):
    calls = []

    def fake(message, sender_name="Raksha"):
        calls.append((message, sender_name))
        return api.SendResult(True, "", 200)

    monkeypatch.setattr(cli.api, "send_message", fake)
    return calls


def sent_fail(monkeypatch, reason="unreachable: timeout"):
    calls = []

    def fake(message, sender_name="Raksha"):
        calls.append((message, sender_name))
        return api.SendResult(False, reason)

    monkeypatch.setattr(cli.api, "send_message", fake)
    return calls


def test_send_happy_path(monkeypatch, capsys):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["I really didn't expect this...", "This is so sweet.", ".", "y", ""])
    cli.scene_send()
    out = capsys.readouterr().out

    assert len(calls) == 1
    assert calls[0][0] == "I really didn't expect this...\nThis is so sweet."
    assert calls[0][1] == M.NAME
    assert M.SEND_SUCCESS_TITLE in out
    assert M.SEND_SUCCESS[0] in out


def test_privacy_notice_is_shown_before_sending(monkeypatch, capsys):
    sent_ok(monkeypatch)
    drive(monkeypatch, ["hello", ".", "y", ""])
    cli.scene_send()
    out = capsys.readouterr().out
    for line in M.SEND_PRIVACY_NOTICE:
        if line:
            assert line in out
    # the notice appears before the delivery confirmation
    assert out.index(M.SEND_PRIVACY_NOTICE[0]) < out.index(M.SEND_SUCCESS_TITLE)


def test_send_cancelled_sends_nothing(monkeypatch, capsys):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["hello", ".", "c", ""])
    cli.scene_send()
    assert calls == []
    assert M.SEND_CANCELLED[0] in capsys.readouterr().out


def test_send_edit_replaces_the_message(monkeypatch, capsys):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["first draft", ".", "e", "second draft", ".", "y", ""])
    cli.scene_send()
    assert len(calls) == 1
    assert calls[0][0] == "second draft"


def test_empty_message_is_never_sent(monkeypatch, capsys):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["", "c", ""])
    cli.scene_send()
    assert calls == []
    assert M.SEND_EMPTY[0] in capsys.readouterr().out


def test_empty_then_written_is_sent(monkeypatch):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["", "e", "now I have words", ".", "y", ""])
    cli.scene_send()
    assert len(calls) == 1
    assert calls[0][0] == "now I have words"


def test_oversized_message_is_refused_locally(monkeypatch, capsys):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["x" * (api.MAX_MESSAGE_LENGTH + 50), "c", ""])
    cli.scene_send()
    assert calls == []
    assert M.SEND_TOO_LONG[0] in capsys.readouterr().out


def test_failure_never_claims_success(monkeypatch, capsys):
    sent_fail(monkeypatch)
    drive(monkeypatch, ["hello", ".", "y", ""])
    cli.scene_send()
    out = capsys.readouterr().out
    assert "NOT delivered" in out
    assert M.SEND_SUCCESS_TITLE not in out
    assert "sent successfully" not in out.lower()


def test_blank_line_twice_ends_composition(monkeypatch):
    calls = sent_ok(monkeypatch)
    drive(monkeypatch, ["one", "", "two", "", "", "y", ""])
    cli.scene_send()
    assert calls[0][0] == "one\n\ntwo"


#: Keystrokes that carry each offline scene through to its end.
OFFLINE_SCRIPTS = {
    "message": [""],
    "reasons": [""] * (len(M.REASONS) + 1),
    "love_exe": [""],
    "memories": [""] * (len(M.MEMORIES) + 2),
    "random_love": ["b"],
    "question": ["y", "1", ""],
    "secret": [""],
}


@pytest.mark.parametrize("name", sorted(set(cli.SCENES) - {"send"}))
def test_no_other_scene_touches_the_network(monkeypatch, capsys, name):
    """Everything except the send scene must work fully offline."""
    no_network(monkeypatch)
    drive(monkeypatch, OFFLINE_SCRIPTS[name])
    cli.SCENES[name]()
    assert capsys.readouterr().out.strip()


def test_offline_scripts_cover_every_scene():
    assert set(OFFLINE_SCRIPTS) | {"send"} == set(cli.SCENES)
