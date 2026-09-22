"""
============================================================================
 EVERYTHING PERSONAL LIVES IN THIS ONE FILE.
============================================================================

Edit anything below and the whole experience changes. No other file in the
package contains personal content -- the rest is just stage lighting.

Formatting notes:
  * Plain strings are printed with a typewriter effect, line by line.
  * Use blank lines ("") inside a block to create a deliberate pause.
  * Keep lines under ~46 characters so they stay centered and readable
    in a small terminal window.
  * "{name}" anywhere in a line is replaced with NAME below.
============================================================================
"""

# ---------------------------------------------------------------------------
# 1. WHO THIS IS FOR
# ---------------------------------------------------------------------------

#: Shown spaced out on the reveal screen and in every header.
NAME = "Raksha"

#: Subtitle under the main banner.
TAGLINE = "A little secret for you"

#: The small line that sits beneath the banner.
SIGNATURE_LINE = "made with a lot of thought."


# ---------------------------------------------------------------------------
# 2. BOOT SEQUENCE
# ---------------------------------------------------------------------------

BOOT_LINES = [
    "Initializing...",
    "",
    "Loading something important...",
]

BOOT_CHECKS = [
    "Checking...",
    "Checking...",
    "Checking...",
]

BOOT_PROMPT = [
    "One final thing...",
    "",
    "Who is this program for?",
]

BOOT_CONFIRMATION = [
    "Identity confirmed.",
    "",
    "Welcome, {name}.",
    "",
    "This isn't really a program.",
    "",
    "It's a message...",
    "that happens to have an executable file.",
]


# ---------------------------------------------------------------------------
# 3. MAIN SCREEN INTRO  (shown once, after the boot sequence)
# ---------------------------------------------------------------------------

INTRO_LINES = [
    "I could have just sent you a message.",
    "",
    "But where's the fun in that?",
    "",
    "So...",
    "",
    "I turned my feelings into a Python package.",
]


# ---------------------------------------------------------------------------
# 4. OPTION 1 -- OPEN MY MESSAGE
# ---------------------------------------------------------------------------

MESSAGE_OPENING = "Opening something I've been wanting to say..."

MAIN_MESSAGE = [
    "{name},",
    "",
    "There are things that are difficult to",
    "say normally.",
    "",
    "So I made a program instead.",
    "",
    "You are not just another person in my life.",
    "",
    "Somehow...",
    "",
    "you became someone I look forward to,",
    "someone I think about,",
    "and someone whose presence means",
    "more to me than I probably say.",
    "",
    "And if this little program made you smile...",
    "",
    "then it did exactly what I wanted it to do.",
]

MESSAGE_CLOSING = "For you, {name}."


# ---------------------------------------------------------------------------
# 5. OPTION 2 -- WHY RAKSHA?
#     Each entry is a list of lines. Add or remove freely; they are
#     numbered automatically.
# ---------------------------------------------------------------------------

REASONS_LOADING = "Loading reasons..."

REASONS = [
    ["Because talking to you never feels ordinary."],
    [
        "Because somehow, you make normal days",
        "feel a little more special.",
    ],
    [
        "Because you listen properly.",
        "Not politely. Properly.",
    ],
    [
        "Because you have opinions,",
        "and you are not shy about them.",
    ],
    [
        "Because your laugh arrives before",
        "the joke is finished.",
    ],
    [
        "Because you are kind in the quiet way",
        "that nobody applauds.",
    ],
    [
        "Because you make me want to be",
        "slightly less of a disaster.",
    ],
    [
        "Because silence with you is comfortable,",
        "and that is rarer than it sounds.",
    ],
    [
        "Because you remember small things",
        "that other people let fall.",
    ],
    [
        "Honestly...",
        "",
        "I could keep adding reasons.",
        "",
        "But then this terminal would never finish.",
    ],
]


# ---------------------------------------------------------------------------
# 6. OPTION 3 -- LOVE.EXE
# ---------------------------------------------------------------------------

LOVE_EXE_STEPS = [
    "Scanning heart...",
    "Checking feelings...",
    "Calculating attachment...",
]

LOVE_EXE_FAILING_STEP = "Checking ability to stop thinking about {name}..."

LOVE_EXE_ERROR = [
    "ERROR.",
    "",
    "Operation failed.",
]

LOVE_EXE_CAUSE = [
    "Cause:",
    "",
    "{name} detected.",
    "",
    "System cannot continue normally.",
]

LOVE_EXE_DIAGNOSTICS = [
    "Attempting recovery ............ failed",
    "Attempting to be normal ........ failed",
    "Attempting to play it cool ..... failed",
]

LOVE_EXE_STATUS = "RUNNING"

LOVE_EXE_FOOTER = [
    "Uninstall is not available on this system.",
]


# ---------------------------------------------------------------------------
# 7. OPTION 4 -- MEMORY LANE
#     Placeholders on purpose. Replace with your own.
# ---------------------------------------------------------------------------

MEMORY_INTRO = "Loading memories..."

MEMORIES = [
    "That conversation I still remember.",
    "That day we laughed for no reason.",
    "That moment I realized you were different.",
    "That random little thing you probably forgot.",
]

MEMORY_CLOSING = [
    "Some of these you remember.",
    "",
    "Some of these only I do.",
    "",
    "Both are fine.",
]


# ---------------------------------------------------------------------------
# 8. OPTION 5 -- RANDOM LOVE
#     Each entry is a list of lines, shown as "Random Thought #NN".
# ---------------------------------------------------------------------------

RANDOM_THOUGHTS = [
    [
        "If I had to choose one notification",
        "to receive every day...",
        "",
        "I'd choose yours.",
    ],
    [
        "Some people make your day better",
        "without even trying.",
        "",
        "You are one of those people.",
    ],
    [
        "System notification:",
        "",
        "{name} is currently occupying",
        "an unreasonable amount of storage",
        "in someone's heart.",
    ],
    [
        "You are the only person",
        "I have ever written documentation for.",
    ],
    [
        "Most conversations end.",
        "",
        "Ours just pause.",
    ],
    [
        "Warning:",
        "",
        "Prolonged exposure to {name}",
        "causes permanent smiling.",
    ],
    [
        "I have a very good memory",
        "for things you said casually.",
    ],
    [
        "You are my favourite interruption.",
    ],
    [
        "Somewhere between 'hello'",
        "and 'goodnight',",
        "",
        "you became a habit",
        "I have no intention of breaking.",
    ],
    [
        "Query executed:",
        "",
        "SELECT * FROM people",
        "WHERE presence = 'effortless';",
        "",
        "1 row returned.",
    ],
    [
        "If overthinking about you",
        "were a skill,",
        "",
        "I would be dangerously employable.",
    ],
    [
        "You do not have to do anything",
        "to be the best part of a day.",
        "",
        "Which is unfair to everyone else.",
    ],
    [
        "There is a version of me",
        "that is calmer,",
        "",
        "and it exists mostly",
        "when I am talking to you.",
    ],
    [
        "Status report:",
        "",
        "Still thinking about you.",
        "Uptime: considerable.",
    ],
    [
        "Your name is the shortest sentence",
        "that makes me pay attention.",
    ],
    [
        "I like that you are a whole person",
        "with your own weather.",
        "",
        "I just like standing in it.",
    ],
    [
        "Some people are a mood.",
        "",
        "You are a climate.",
    ],
    [
        "Cache cleared.",
        "Cookies deleted.",
        "History wiped.",
        "",
        "You: still there.",
    ],
    [
        "I do not need a reason",
        "to want to talk to you.",
        "",
        "Which is, in itself, the reason.",
    ],
    [
        "You are not a distraction.",
        "",
        "You are the thing",
        "everything else distracts me from.",
    ],
    [
        "The nicest thing about you",
        "is that you would be embarrassed",
        "reading this.",
    ],
    [
        "Fun fact:",
        "",
        "this package has zero dependencies,",
        "",
        "and exactly one reason to exist.",
    ],
]


# ---------------------------------------------------------------------------
# 9. OPTION 6 -- THE QUESTION
# ---------------------------------------------------------------------------

QUESTION_WARNING = [
    "Warning.",
    "",
    "This section contains one question.",
    "",
    "Are you sure you want to continue?",
]

QUESTION_PREPARING = "Preparing question..."

QUESTION_HEADER = [
    "There is something I want",
    "to ask you.",
]

#: The question itself. Change this to whatever you actually want to ask.
QUESTION = [
    "Would you like to be",
    "a little more than",
    "just a beautiful part",
    "of my life?",
]

QUESTION_OPTIONS = [
    "Yes",
    "Maybe",
    "I need time",
    "Go back",
]

ANSWER_YES = [
    "...",
    "",
    "Okay.",
    "",
    "You just made someone",
    "very, very happy.",
    "",
    "No rush on anything else.",
    "Today is enough.",
]

ANSWER_MAYBE = [
    "That's okay.",
    "",
    "Some answers deserve time.",
    "",
    "I'll happily wait.",
]

ANSWER_TIME = [
    "Take all the time you need.",
    "",
    "No pressure.",
    "",
    "Some things are worth thinking about.",
]

ANSWER_BACK = [
    "Of course.",
    "",
    "The question isn't going anywhere.",
    "",
    "Neither am I.",
]


# ---------------------------------------------------------------------------
# 10. OPTION 7 -- SEND ME A MESSAGE
# ---------------------------------------------------------------------------

SEND_INTRO = [
    "If you want to say something back,",
    "this is where you say it.",
    "",
    "Write as much or as little as you like.",
]

SEND_PROMPT_HELP = [
    "Type your message. Enter starts a new line.",
    "Finish with a single '.' on its own line",
    "or press Enter twice.",
]

SEND_PROMPT_LABEL = "{name}'s message:"

#: Shown before sending. Keep it honest and plain.
SEND_PRIVACY_NOTICE = [
    "Your message will be sent to the person",
    "who created this surprise.",
    "",
    "Only the message you choose to send will",
    "be submitted.",
]

SEND_CONFIRM_TITLE = "Send this message?"

SEND_SENDING_STEPS = [
    "Connecting...",
    "Sending your message...",
]

SEND_SENT_LINES = [
    "Message sent successfully.",
    "",
    "Your message is on its way.",
]

SEND_SUCCESS_TITLE = "MESSAGE DELIVERED"

SEND_SUCCESS = [
    "Your message has been sent.",
    "",
    "Now...",
    "",
    "someone is probably smiling",
    "at their inbox.",
]

SEND_FAILURE = [
    "Unable to send the message right now.",
    "",
    "Your message was NOT delivered.",
    "",
    "Please check your internet connection",
    "and try again later.",
]

SEND_CANCELLED = [
    "Nothing was sent.",
    "",
    "The offer stays open.",
]

SEND_EMPTY = [
    "There's nothing there yet.",
    "",
    "Write something first.",
]

SEND_TOO_LONG = [
    "That's a beautiful amount of words.",
    "",
    "Slightly more than the envelope holds,",
    "though. Trim it a little?",
]


# ---------------------------------------------------------------------------
# 11. SECRET  (menu option, or type 143 / the name at the menu)
# ---------------------------------------------------------------------------

SECRET_TITLE = "SECRET MESSAGE UNLOCKED"

SECRET_MESSAGE = [
    "You found the secret.",
    "",
    "But honestly...",
    "",
    "there was never really a secret.",
    "",
    "The whole program was made",
    "because of you.",
    "",
    "Every screen.",
    "Every message.",
    "Every little animation.",
    "",
    "You.",
]

SECRET_CLOSING = "You are loved."

#: Typing any of these at the main menu opens the secret.
SECRET_TRIGGERS = ["143", "raksha", "secret", "love"]


# ---------------------------------------------------------------------------
# 12. EXIT
# ---------------------------------------------------------------------------

EXIT_STEPS = [
    "Closing {name}.exe...",
    "Saving memories...",
]

EXIT_MESSAGE = [
    "Before you go...",
    "",
    "Remember:",
    "",
    "Someone spent time making this",
    "just to see you smile.",
    "",
    "Goodnight, {name}.",
    "",
    "Until next time...",
]

EXIT_FINAL = [
    "Connection closed.",
    "",
    "But the feeling isn't.",
]


# ---------------------------------------------------------------------------
# 13. MENU
#     (key, label, handler-name). Reorder or rename labels freely; the
#     handler names are wired up in cli.py.
# ---------------------------------------------------------------------------

MENU_TITLE = "SELECT AN OPTION"

MENU_ITEMS = [
    ("1", "Open My Message", "message"),
    ("2", "Why {name}?", "reasons"),
    ("3", "Love.exe", "love_exe"),
    ("4", "Memory Lane", "memories"),
    ("5", "Random Love", "random_love"),
    ("6", "The Question", "question"),
    ("7", "Send Me a Message", "send"),
    ("8", "Secret", "secret"),
    ("9", "Exit", "exit"),
]

MENU_HINT = "Choose a number, then press Enter."

INVALID_CHOICE = "That isn't one of the options. Try again."

CONTINUE_HINT = "Press Enter to continue"


def fmt(text):
    """Substitute {name} / {tagline} into a line or a list of lines."""
    values = {"name": NAME, "tagline": TAGLINE}
    if isinstance(text, (list, tuple)):
        return [fmt(item) for item in text]
    return text.format(**values)
