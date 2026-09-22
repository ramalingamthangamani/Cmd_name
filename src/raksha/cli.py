"""The experience itself: boot sequence, main menu, and every scene.

Personal content is never written here -- it is read from ``messages.py``.
"""

from __future__ import annotations

import random
import sys

from . import animation as anim
from . import api
from . import messages as M
from . import ui
from .animation import C
from .ui import Quit

fmt = M.fmt


# ---------------------------------------------------------------------------
# 1. Boot sequence -- the first ten seconds
# ---------------------------------------------------------------------------

def boot() -> None:
    anim.clear()
    anim.hide_cursor()
    ui.blank(2)

    anim.type_block(fmt(M.BOOT_LINES), color=C.SOFT, delay=0.035, line_pause=0.35)
    ui.blank()
    anim.progress(duration=1.7, color=C.DEEP_ROSE)
    ui.blank()

    for check in fmt(M.BOOT_CHECKS):
        anim.type_line(check, color=C.DIM, delay=0.03)
        anim.sleep(0.45)

    ui.blank()
    anim.sleep(0.5)
    anim.type_block(fmt(M.BOOT_PROMPT), color=C.IVORY, delay=0.045, line_pause=0.4)

    # The held breath before the reveal.
    anim.sleep(1.3)
    anim.dots(3, delay=0.42)
    anim.sleep(0.7)

    anim.transition(0.4)
    ui.blank(3)
    anim.reveal_name(M.NAME)
    anim.sleep(0.6)

    ui.blank()
    anim.type_block(
        fmt(M.BOOT_CONFIRMATION),
        color=C.IVORY,
        delay=0.034,
        line_pause=0.3,
        blank_pause=0.55,
    )
    anim.sleep(1.1)
    ui.pause(M.CONTINUE_HINT)


# ---------------------------------------------------------------------------
# 2. Main screen
# ---------------------------------------------------------------------------

def header(animate: bool = True) -> None:
    anim.clear()
    ui.blank()
    ui.banner(M.NAME, fmt(M.TAGLINE), animate=animate)
    ui.blank()
    ui.quiet(fmt(M.SIGNATURE_LINE), C.DIM)
    ui.blank()


def intro() -> None:
    header()
    ui.blank()
    anim.type_block(fmt(M.INTRO_LINES), color=C.IVORY, delay=0.032, line_pause=0.3)
    anim.sleep(1.0)
    ui.pause(M.CONTINUE_HINT)


# ---------------------------------------------------------------------------
# 3. Scenes
# ---------------------------------------------------------------------------

def scene_message() -> None:
    header(animate=False)
    anim.type_line(fmt(M.MESSAGE_OPENING), color=C.DIM, delay=0.03)
    anim.sleep(0.8)
    anim.transition(0.5)

    ui.blank(2)
    anim.type_block(
        fmt(M.MAIN_MESSAGE),
        color=C.IVORY,
        delay=0.042,
        line_pause=0.34,
        blank_pause=0.62,
    )
    anim.sleep(1.2)
    ui.blank()
    ui.rule(width=28)
    ui.blank()
    anim.type_line(fmt(M.MESSAGE_CLOSING), color=C.ROSE, delay=0.07)
    anim.sleep(1.0)
    ui.pause(M.CONTINUE_HINT)


def scene_reasons() -> None:
    header(animate=False)
    anim.type_line(fmt(M.REASONS_LOADING), color=C.DIM, delay=0.03)
    anim.sleep(0.4)
    anim.progress(duration=1.0, bar_width=20, show_percent=False)
    anim.sleep(0.4)

    total = len(M.REASONS)
    for index, reason in enumerate(M.REASONS, start=1):
        anim.transition(0.35)
        ui.blank(3)
        label = "Reason #%02d" % index
        anim.type_line(label, color=C.ROSE, delay=0.03)
        ui.blank()
        anim.type_block(
            fmt(reason),
            color=C.IVORY,
            delay=0.04,
            line_pause=0.3,
            blank_pause=0.5,
        )
        anim.sleep(0.6)
        if index < total:
            ui.pause("Press Enter")
        else:
            anim.sleep(0.8)
            ui.pause(M.CONTINUE_HINT)


def scene_love_exe() -> None:
    header(animate=False)
    anim.type_line(fmt("Launching Love.exe..."), color=C.SOFT, delay=0.035)
    anim.sleep(0.6)
    anim.transition(0.35)
    ui.blank(2)

    for step in fmt(M.LOVE_EXE_STEPS):
        anim.progress(step, duration=1.1, color=C.DEEP_ROSE)
        anim.sleep(0.25)

    ui.blank()
    anim.failing_progress(fmt(M.LOVE_EXE_FAILING_STEP), stop_at=0.75)
    ui.blank()
    anim.type_block(fmt(M.LOVE_EXE_ERROR), color=C.WINE, delay=0.05, line_pause=0.4)
    anim.sleep(0.9)

    anim.transition(0.5)
    ui.blank(2)
    anim.type_block(fmt(M.LOVE_EXE_CAUSE), color=C.IVORY, delay=0.04, line_pause=0.35)
    anim.sleep(0.8)

    ui.blank()
    for line in fmt(M.LOVE_EXE_DIAGNOSTICS):
        anim.type_line(line, color=C.DIM, delay=0.016)
        anim.sleep(0.3)

    anim.sleep(0.7)
    anim.transition(0.4)
    ui.blank(3)
    anim.type_line("Love.exe status:", color=C.SOFT, delay=0.04)
    ui.blank()
    ui.double_box(["", fmt(M.LOVE_EXE_STATUS), ""], width=34, color=C.ROSE)
    ui.blank()
    for line in fmt(M.LOVE_EXE_FOOTER):
        anim.type_line(line, color=C.DIM, delay=0.03)
    anim.sleep(1.0)
    ui.pause(M.CONTINUE_HINT)


def scene_memories() -> None:
    header(animate=False)
    anim.type_line(fmt(M.MEMORY_INTRO), color=C.DIM, delay=0.03)
    anim.sleep(0.3)
    anim.progress(duration=1.2, bar_width=20, show_percent=False)
    anim.sleep(0.5)

    for index, memory in enumerate(M.MEMORIES, start=1):
        anim.transition(0.4)
        ui.blank(4)
        ui.quiet("%02d / %02d" % (index, len(M.MEMORIES)), C.FAINT)
        ui.blank(2)
        anim.type_line(fmt(memory), color=C.IVORY, delay=0.05)
        anim.sleep(1.1)
        ui.blank()
        ui.rule(width=20)
        ui.pause("Press Enter")

    anim.transition(0.4)
    ui.blank(3)
    anim.type_block(fmt(M.MEMORY_CLOSING), color=C.SOFT, delay=0.04, line_pause=0.35)
    anim.sleep(0.9)
    ui.pause(M.CONTINUE_HINT)


def scene_random_love() -> None:
    header(animate=False)
    anim.spinner("Choosing one at random", duration=1.1)
    anim.sleep(0.3)

    seen: list[int] = []
    while True:
        # Avoid repeating a thought until the whole deck has been shown.
        if len(seen) >= len(M.RANDOM_THOUGHTS):
            seen = []
        pool = [i for i in range(len(M.RANDOM_THOUGHTS)) if i not in seen]
        index = random.choice(pool)
        seen.append(index)

        anim.transition(0.35)
        ui.blank(3)
        anim.type_line("Random Thought #%02d" % (index + 1), color=C.ROSE, delay=0.03)
        ui.blank()
        anim.type_block(
            fmt(M.RANDOM_THOUGHTS[index]),
            color=C.IVORY,
            delay=0.042,
            line_pause=0.32,
            blank_pause=0.55,
        )
        anim.sleep(0.9)

        ui.blank(2)
        ui.quiet("[Enter] another    [B] back", C.FAINT)
        if ui.ask(">").lower() in ("b", "back", "q"):
            return


def scene_question() -> None:
    header(animate=False)
    ui.blank()
    anim.type_block(fmt(M.QUESTION_WARNING), color=C.SOFT, delay=0.04, line_pause=0.35)
    ui.blank()
    ui.key_list([("Y", "Yes"), ("N", "No")])
    ui.blank()

    answer = ui.confirm_keys(["y", "n", "yes", "no"])
    if answer.startswith("n"):
        anim.transition(0.3)
        ui.blank(3)
        anim.type_block(fmt(M.ANSWER_BACK), color=C.SOFT, delay=0.04)
        anim.sleep(0.8)
        ui.pause(M.CONTINUE_HINT)
        return

    anim.transition(0.4)
    ui.blank(3)
    anim.type_line(fmt(M.QUESTION_PREPARING), color=C.DIM, delay=0.04)
    ui.blank()
    anim.progress(duration=2.0, color=C.DEEP_ROSE)
    anim.sleep(0.9)

    anim.transition(0.6)
    ui.blank(2)
    ui.double_box(
        [""] + [ui.spaced_name(M.NAME)] + [""] + fmt(M.QUESTION_HEADER) + [""],
        width=48,
    )
    anim.sleep(1.4)

    ui.blank(2)
    anim.type_block(fmt(M.QUESTION), color=C.ROSE, delay=0.075, line_pause=0.42)
    anim.sleep(1.5)

    ui.blank(2)
    ui.choice_list(fmt(M.QUESTION_OPTIONS))
    ui.blank()

    choice = ui.confirm_keys(["1", "2", "3", "4"])
    responses = {
        "1": M.ANSWER_YES,
        "2": M.ANSWER_MAYBE,
        "3": M.ANSWER_TIME,
        "4": M.ANSWER_BACK,
    }

    anim.transition(0.6)
    ui.blank(3)
    if choice == "1":
        anim.dots(3, delay=0.5)
        anim.sleep(0.5)
    anim.type_block(
        fmt(responses[choice]),
        color=C.IVORY,
        delay=0.055,
        line_pause=0.4,
        blank_pause=0.65,
    )
    anim.sleep(1.3)
    ui.pause(M.CONTINUE_HINT)


# ---------------------------------------------------------------------------
# 4. Send Me a Message
# ---------------------------------------------------------------------------

def _compose() -> str:
    """Collect a multi-line message. Returns "" when nothing was written."""
    ui.blank()
    for line in fmt(M.SEND_PROMPT_HELP):
        ui.quiet(line, C.FAINT)
    ui.blank()
    anim.type_line(fmt(M.SEND_PROMPT_LABEL), color=C.ROSE, delay=0.03)
    ui.blank()

    indent = max(0, (anim.term_columns() - 46) // 2)
    lines: list[str] = []
    blanks = 0
    while True:
        try:
            line = ui.ask_raw(">", indent=indent)
        except Quit:
            break
        stripped = line.strip()
        if stripped == ".":
            break
        if stripped == "":
            blanks += 1
            if blanks >= 2 or not lines:
                break
            lines.append("")
            continue
        blanks = 0
        lines.append(line.rstrip())
        if len("\n".join(lines)) > api.MAX_MESSAGE_LENGTH:
            break

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).strip()


def _preview(message: str) -> None:
    ui.blank()
    ui.rule(width=46)
    ui.blank()
    for line in message.split("\n"):
        ui.quiet(line if line else " ", C.IVORY)
    ui.blank()
    ui.rule(width=46)


def scene_send() -> None:
    header(animate=False)
    anim.type_block(fmt(M.SEND_INTRO), color=C.IVORY, delay=0.03, line_pause=0.25)

    message = _compose()

    while True:
        problem = api.validate(message)
        if problem == "empty":
            anim.transition(0.3)
            ui.blank(3)
            anim.type_block(fmt(M.SEND_EMPTY), color=C.SOFT, delay=0.04)
            ui.blank()
            ui.key_list([("E", "Write something"), ("C", "Go back")])
            ui.blank()
            if ui.confirm_keys(["e", "c"]) == "c":
                return
            anim.transition(0.25)
            header(animate=False)
            message = _compose()
            continue
        if problem == "too_long":
            anim.transition(0.3)
            ui.blank(3)
            anim.type_block(fmt(M.SEND_TOO_LONG), color=C.SOFT, delay=0.04)
            ui.quiet("(limit: %d characters)" % api.MAX_MESSAGE_LENGTH, C.FAINT)
            ui.blank()
            ui.key_list([("E", "Edit"), ("C", "Cancel")])
            ui.blank()
            if ui.confirm_keys(["e", "c"]) == "c":
                return
            anim.transition(0.25)
            header(animate=False)
            message = _compose()
            continue

        # Confirmation screen, with the privacy notice she sees every time.
        anim.transition(0.35)
        ui.blank(2)
        _preview(message)
        ui.blank(2)
        ui.rule(width=46)
        ui.blank()
        for line in fmt(M.SEND_PRIVACY_NOTICE):
            if line:
                ui.quiet(line, C.SOFT)
            else:
                ui.blank()
        ui.blank()
        ui.rule(width=46)
        ui.blank()
        anim.type_line(fmt(M.SEND_CONFIRM_TITLE), color=C.IVORY, delay=0.025)
        ui.blank()
        ui.key_list([("Y", "Send"), ("E", "Edit"), ("C", "Cancel")])
        ui.blank()

        answer = ui.confirm_keys(["y", "e", "c"])
        if answer == "c":
            anim.transition(0.3)
            ui.blank(3)
            anim.type_block(fmt(M.SEND_CANCELLED), color=C.SOFT, delay=0.04)
            anim.sleep(0.7)
            ui.pause(M.CONTINUE_HINT)
            return
        if answer == "e":
            anim.transition(0.25)
            header(animate=False)
            ui.quiet("(your message so far is below -- retype it as you like)", C.FAINT)
            _preview(message)
            message = _compose()
            continue
        break

    # ---- send ----
    anim.transition(0.4)
    ui.blank(3)
    steps = fmt(M.SEND_SENDING_STEPS)

    anim.progress(steps[0], duration=1.0, color=C.DEEP_ROSE)
    ui.blank()

    result = api.send_message(message, sender_name=M.NAME)

    anim.progress(steps[1] if len(steps) > 1 else "Sending...", duration=1.2, color=C.DEEP_ROSE)
    anim.sleep(0.4)

    anim.transition(0.5)
    ui.blank(2)

    if result.ok:
        anim.type_block(fmt(M.SEND_SENT_LINES), color=C.IVORY, delay=0.04, line_pause=0.3)
        anim.sleep(0.9)
        anim.transition(0.4)
        ui.blank(3)
        ui.double_box(["", fmt(M.SEND_SUCCESS_TITLE), ""], width=48)
        ui.blank(2)
        anim.type_block(fmt(M.SEND_SUCCESS), color=C.IVORY, delay=0.045, line_pause=0.32)
    else:
        anim.type_block(fmt(M.SEND_FAILURE), color=C.WINE, delay=0.04, line_pause=0.32)
        if result.reason:
            ui.blank()
            ui.quiet("(%s)" % result.reason, C.FAINT)

    anim.sleep(1.1)
    ui.pause(M.CONTINUE_HINT)


# ---------------------------------------------------------------------------
# 5. Secret
# ---------------------------------------------------------------------------

def scene_secret() -> None:
    anim.transition(0.3)
    ui.blank(2)
    anim.spinner("Verifying", duration=0.9)
    anim.sleep(0.4)
    anim.transition(0.4)
    ui.blank(2)
    ui.double_box(["", fmt(M.SECRET_TITLE), ""], width=48, color=C.ROSE)
    anim.sleep(1.0)
    ui.blank(2)
    anim.type_block(
        fmt(M.SECRET_MESSAGE),
        color=C.IVORY,
        delay=0.048,
        line_pause=0.34,
        blank_pause=0.6,
    )
    anim.sleep(1.2)
    anim.transition(0.6)
    ui.blank(4)
    anim.reveal_name(M.NAME)
    ui.blank()
    anim.type_line(fmt(M.SECRET_CLOSING), color=C.ROSE, delay=0.08)
    anim.sleep(1.4)
    ui.pause(M.CONTINUE_HINT)


# ---------------------------------------------------------------------------
# 6. Exit
# ---------------------------------------------------------------------------

def scene_exit() -> None:
    anim.transition(0.35)
    ui.blank(2)
    for step in fmt(M.EXIT_STEPS):
        anim.progress(step, duration=1.0, color=C.DEEP_ROSE)
        anim.sleep(0.2)

    ui.blank()
    anim.sleep(0.5)
    anim.type_block(
        fmt(M.EXIT_MESSAGE),
        color=C.IVORY,
        delay=0.045,
        line_pause=0.34,
        blank_pause=0.6,
    )
    anim.sleep(1.2)
    anim.transition(0.6)
    ui.blank(4)
    anim.type_block(fmt(M.EXIT_FINAL), color=C.SOFT, delay=0.06, line_pause=0.45)
    ui.blank(2)
    anim.sleep(0.9)


# ---------------------------------------------------------------------------
# 7. Menu loop
# ---------------------------------------------------------------------------

SCENES = {
    "message": scene_message,
    "reasons": scene_reasons,
    "love_exe": scene_love_exe,
    "memories": scene_memories,
    "random_love": scene_random_love,
    "question": scene_question,
    "send": scene_send,
    "secret": scene_secret,
}


def main_menu() -> None:
    items = [(key, fmt(label), handler) for key, label, handler in M.MENU_ITEMS]
    keys = {key: handler for key, _label, handler in items}
    triggers = [t.lower() for t in M.SECRET_TRIGGERS]
    first = True

    while True:
        header(animate=first)
        first = False
        ui.blank()
        ui.menu(fmt(M.MENU_TITLE), items)
        ui.blank()
        ui.quiet(fmt(M.MENU_HINT), C.FAINT)
        ui.blank()

        choice = ui.ask(">")
        lowered = choice.lower()

        if not lowered:
            # A bare Enter is not a mistake worth commenting on.
            continue

        if lowered in keys:
            handler = keys[lowered]
            if handler == "exit":
                scene_exit()
                return
            SCENES[handler]()
            continue

        if lowered in triggers:
            scene_secret()
            continue

        if lowered in ("q", "quit", "exit", "bye"):
            scene_exit()
            return

        ui.blank()
        ui.quiet(fmt(M.INVALID_CHOICE), C.WINE)
        anim.sleep(1.1)


# ---------------------------------------------------------------------------
# 8. Entry point
# ---------------------------------------------------------------------------

def _goodbye_on_interrupt() -> None:
    """Ctrl+C should still feel like part of the experience."""
    anim.show_cursor()
    ui.blank(2)
    try:
        ui.quiet("Closing gently.", C.SOFT)
        ui.blank()
        ui.quiet(fmt("Goodnight, {name}."), C.ROSE)
        ui.blank()
    except Exception:
        pass


def run(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--version" in argv or "-V" in argv:
        from . import __version__

        print("raksha %s" % __version__)
        return 0

    if "--help" in argv or "-h" in argv:
        print("raksha -- a small terminal experience.\n")
        print("Usage: raksha [--skip-intro] [--fast] [--version]\n")
        print("  --skip-intro   go straight to the menu")
        print("  --fast         no animation delays")
        return 0

    if "--fast" in argv:
        anim.FAST = True

    try:
        anim.hide_cursor()
        if "--skip-intro" not in argv:
            boot()
            intro()
        main_menu()
        return 0
    except (KeyboardInterrupt, Quit):
        _goodbye_on_interrupt()
        return 0
    finally:
        anim.show_cursor()
        anim.write(C.RESET if anim.COLOR else "")
        anim.flush()


def main() -> None:
    """Console-script entry point."""
    raise SystemExit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
