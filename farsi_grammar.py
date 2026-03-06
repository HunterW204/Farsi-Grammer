#!/usr/bin/env python3
"""
Farsi Grammar Master
A comprehensive game to learn and retain Farsi grammar —
from ezafe to tenses, word order, passives, conditionals, and more.
"""

import random, json, os, sys, textwrap

SAVE_FILE = os.path.expanduser("~/.farsi_grammar_progress.json")
W = 60


# ── Exercise builder helpers ──────────────────────────────────

def mc(prompt, answer, wrong, hint="", expl=""):
    return dict(kind="mc", prompt=prompt, answer=answer,
                choices=wrong + [answer], hint=hint, expl=expl)

def fill(prompt, answer, hint="", expl=""):
    return dict(kind="fill", prompt=prompt, answer=answer,
                choices=[], hint=hint, expl=expl)

def scr(prompt, answer, hint="", expl=""):
    """Scramble — answer is the correct word order."""
    return dict(kind="scr", prompt=prompt, answer=answer,
                choices=[], hint=hint, expl=expl)


# ── Progress tracking ─────────────────────────────────────────

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_progress(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ── Display helpers ───────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def hr():
    print("─" * W)

def header(title="FARSI GRAMMAR MASTER"):
    clear()
    print("═" * W)
    print(f"  {title}")
    print("═" * W)

def show_lesson(lesson_text):
    for line in lesson_text.strip().splitlines():
        print(f"  {line}")


# ── Exercise runners ──────────────────────────────────────────

def run_mc(ex):
    choices = ex["choices"][:]
    random.shuffle(choices)
    print()
    print(f"  {ex['prompt']}")
    print()
    for i, c in enumerate(choices, 1):
        print(f"    {i}. {c}")
    if ex["hint"]:
        print(f"\n  Hint: {ex['hint']}")
    print()
    while True:
        try:
            raw = input("  Answer (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            break
        print("  Please enter a number 1–4.")
    chosen = choices[int(raw) - 1]
    correct = (chosen == ex["answer"])
    if correct:
        print("\n  Correct!")
    else:
        print(f"\n  Not quite. The answer is: {ex['answer']}")
    if ex["expl"]:
        print(f"  Note: {ex['expl']}")
    return correct

def normalize(s):
    """Loose matching — ignore case, accent marks, punctuation, hyphens."""
    tbl = str.maketrans("âÂôÔîÎûÛéÉ", "aAoOiIuUeE")
    return (s.lower().strip().rstrip("?.!,")
             .translate(tbl).replace("'", "").replace("-", "").replace(" ", ""))

def run_fill(ex):
    print()
    print(f"  {ex['prompt']}")
    if ex["hint"]:
        print(f"  Hint: {ex['hint']}")
    print()
    try:
        raw = input("  Your answer: ").strip()
    except (KeyboardInterrupt, EOFError):
        return None
    correct = normalize(raw) == normalize(ex["answer"])
    if correct:
        print(f"\n  Correct!  ({ex['answer']})")
    else:
        print(f"\n  The answer is: {ex['answer']}")
    if ex["expl"]:
        print(f"  Note: {ex['expl']}")
    return correct

def run_scr(ex):
    words = ex["answer"].split()
    shuffled = words[:]
    attempts = 0
    while shuffled == words and attempts < 20:
        random.shuffle(shuffled)
        attempts += 1
    print()
    print(f"  {ex['prompt']}")
    print(f"\n  Words:  {' | '.join(shuffled)}")
    if ex["hint"]:
        print(f"  Hint: {ex['hint']}")
    print()
    try:
        raw = input("  Type the correct sentence: ").strip()
    except (KeyboardInterrupt, EOFError):
        return None
    correct = normalize(raw) == normalize(ex["answer"])
    if correct:
        print("\n  Correct!")
    else:
        print(f"\n  The answer is: {ex['answer']}")
    if ex["expl"]:
        print(f"  Note: {ex['expl']}")
    return correct

def run_exercise(ex, num, total):
    kind_label = {"mc": "Multiple Choice", "fill": "Fill in the Blank", "scr": "Unscramble"}
    hr()
    print(f"  Question {num}/{total}   [{kind_label.get(ex['kind'], '')}]")
    if ex["kind"] == "mc":
        result = run_mc(ex)
    elif ex["kind"] == "fill":
        result = run_fill(ex)
    else:
        result = run_scr(ex)
    if result is None:
        return None
    input("\n  Press Enter to continue...")
    return result


# ── Topic runner ──────────────────────────────────────────────

def run_topic(topic, progress):
    name = topic["name"]
    exercises = topic["exercises"]

    header(name)
    print()
    show_lesson(topic["lesson"])
    print()
    hr()
    try:
        input("  Press Enter to start the exercises...")
    except (KeyboardInterrupt, EOFError):
        return

    correct = 0
    exs = exercises[:]
    random.shuffle(exs)

    for i, ex in enumerate(exs, 1):
        header(name)
        result = run_exercise(ex, i, len(exs))
        if result is None:
            break
        if result:
            correct += 1

    total = len(exs)
    pct = int(100 * correct / total) if total else 0
    rec = progress.get(name, {"attempts": 0, "best": 0, "last": 0})
    rec["attempts"] = rec.get("attempts", 0) + 1
    rec["best"] = max(rec.get("best", 0), pct)
    rec["last"] = pct
    progress[name] = rec
    save_progress(progress)

    header(name + " — Results")
    print(f"\n  Score: {correct}/{total}  ({pct}%)\n")
    if pct == 100:
        print("  Perfect score! Excellent mastery.")
    elif pct >= 80:
        print("  Great job! You've got a solid grasp of this topic.")
    elif pct >= 60:
        print("  Good effort. Review the lesson and try again soon.")
    else:
        print("  Keep at it — re-read the lesson and practice more.")
    print()
    input("  Press Enter to return to menu...")


# ── Practice weak areas ───────────────────────────────────────

def practice_weak(topics, progress):
    weak = [t for t in topics if progress.get(t["name"], {}).get("last", 0) < 80]
    if not weak:
        weak = topics

    pool = []
    for t in weak:
        for ex in t["exercises"]:
            pool.append((t["name"], ex))
    random.shuffle(pool)
    pool = pool[:12]

    correct = 0
    for i, (tname, ex) in enumerate(pool, 1):
        header(f"Practice — {i}/{len(pool)}")
        print(f"  Topic: {tname}")
        result = run_exercise(ex, i, len(pool))
        if result is None:
            break
        if result:
            correct += 1

    header("Practice Complete")
    print(f"\n  Score: {correct}/{len(pool)}")
    input("\n  Press Enter to return to menu...")


# ══════════════════════════════════════════════════════════════
# GRAMMAR TOPICS
# ══════════════════════════════════════════════════════════════

TOPICS = [

  # ── 1 ────────────────────────────────────────────────────────
  { "name": "1. Personal Pronouns",
    "lesson": """\
Farsi personal pronouns:
  man    = I              mâ     = we
  to     = you (informal) shomâ  = you (pl. / formal)
  u      = he / she / it  ânhâ   = they

Key facts:
  - NO grammatical gender: 'u' means he, she, AND it
  - 'shomâ' is both plural 'you' and polite singular 'you'
  - 'to' is only for friends, family, children
  - Subject pronouns are often dropped — the verb ending
    already shows who the subject is:  miravam = I go""",
    "exercises": [
      mc("What does 'u' mean in Farsi?", "he / she / it",
         ["I", "we", "you (formal)"]),
      mc("How do you say 'we'?", "mâ", ["man", "to", "u"]),
      mc("Which is both plural and formal 'you'?", "shomâ",
         ["to", "u", "ânhâ"]),
      fill("'They went.' starts with ___ (subject pronoun).", "ânhâ",
           hint="3rd person plural"),
      mc("'to' is used for:", "informal singular you",
         ["formal you", "they", "I"]),
      fill("Farsi has ___ grammatical genders.", "0",
           expl="Farsi has NO grammatical gender. 'u' = he, she, and it."),
      mc("When can subject pronouns be omitted?",
         "always — the verb ending shows the subject",
         ["never", "only in past tense", "only 'man'"]),
    ]
  },

  # ── 2 ────────────────────────────────────────────────────────
  { "name": "2. To Be — Present (hastan)",
    "lesson": """\
Present tense of 'to be':
  hastam  = I am          hastim  = we are
  hasti   = you are       hastid  = you (pl.) are
  ast     = he/she/it is  hastand = they are

Negative — replace 'hast-' with 'nist-':
  nistam, nisti, nist, nistim, nistid, nistand

Short enclitic forms attach directly to predicates:
  man khub-am   = I am well       (khub + -am)
  to  khub-i    = you are well    (khub + -i)
  u   khub-ast  = he/she is well  (khub + -ast)""",
    "exercises": [
      mc("'I am' in Farsi:", "hastam", ["hasti", "ast", "nistam"]),
      mc("'They are' in Farsi:", "hastand", ["hastim", "hastid", "hasti"]),
      mc("'He is not' in Farsi:", "nist", ["ast", "hastam", "nabud"]),
      fill("'We are not' = nist___", "im", expl="nistim = we are not"),
      fill("'You (pl.) are' = hast___", "id"),
      mc("The enclitic 'I am' attached to a predicate:", "khub-am",
         ["khub-ast", "khub-i", "khub-im"]),
      fill("'They are not' = nist___", "and", expl="nistand"),
    ]
  },

  # ── 3 ────────────────────────────────────────────────────────
  { "name": "3. To Be — Past (budan)",
    "lesson": """\
Past tense of 'to be':
  budam  = I was       budim  = we were
  budi   = you were    budid  = you (pl.) were
  bud    = he/she was  budand = they were

Negative — add 'na-' prefix:
  nabudam, nabudi, nabud, nabudim, nabudid, nabudand

Example sentences:
  u xaste bud.       = He/she was tired.
  mâ khâne nabudim.  = We were not at home.
  hava sard bud.     = The weather was cold.""",
    "exercises": [
      mc("'She was' in Farsi:", "bud", ["budam", "budi", "budand"]),
      mc("'We were not' in Farsi:", "nabudim",
         ["nabudi", "nabudand", "nistim"]),
      fill("'I was tired' = man xaste ___", "budam"),
      mc("'They were' in Farsi:", "budand", ["budim", "budid", "budan"]),
      fill("'You were not' = na___i", "bud", expl="nabudi = you were not"),
      mc("Past negative of 'to be' uses prefix:", "na-",
         ["ne-", "bi-", "be-"]),
      fill("'He was not here' = u injâ na___", "bud"),
    ]
  },

  # ── 4 ────────────────────────────────────────────────────────
  { "name": "4. Plural Formation",
    "lesson": """\
Two plural suffixes:

  -hâ  : general plural (colloquial & formal)
           ketâb  → ketâb-hâ   (books)
           miz    → miz-hâ     (tables)

  -ân  : formal/literary, preferred for animates
           mard       → mard-ân        (men)
           dâneshju   → dâneshju-yân   (students)  ← -yân after vowel

IMPORTANT: After numbers, use SINGULAR — no plural suffix!
  se ketâb   = three books     (NOT: se ketâb-hâ)
  dah nafar  = ten people""",
    "exercises": [
      mc("Plural of 'ketâb' (book) in everyday speech:", "ketâb-hâ",
         ["ketâb-ân", "ketâbim", "ketâbid"]),
      fill("'dogs' = sag-___", "hâ"),
      mc("Which is CORRECT for 'two books'?", "do ketâb",
         ["do ketâb-hâ", "do ketâb-ân", "ketâb-hâ do"]),
      mc("Formal/literary plural of 'mard' (man):", "mard-ân",
         ["mard-hâ", "mard-im", "mard-id"]),
      fill("'students' (formal) = dâneshju-___", "yân",
           hint="-yân after a vowel"),
      mc("After numbers in Farsi, use:", "the singular form",
         ["-hâ plural", "-ân plural", "either plural"]),
      fill("'cities' = shahr-___", "hâ"),
    ]
  },

  # ── 5 ────────────────────────────────────────────────────────
  { "name": "5. Ezafe Construction",
    "lesson": """\
The ezafe (-e / -ye) links a noun to what follows it:
  • noun + adjective:   ketâb-e khub     (a good book)
  • noun + noun:        dar-e khâne      (door of the house)
  • noun + possessor:   mâdar-e Ali      (Ali's mother)
  • noun + prep phrase: dokhtari az Irân (a girl from Iran)

Pronunciation rule:
  -e   after a consonant:  ketâb-e, mard-e, rang-e
  -ye  after a vowel:      khâne-ye, dâneshgâh-ye

The ezafe vowel is NOT written in standard Farsi
script — it is implied.""",
    "exercises": [
      mc("'A good book' in Farsi:", "ketâb-e khub",
         ["khub ketâb", "ketâb khub", "khub-e ketâb"]),
      fill("'The door of the house' = dar-e ___", "khâne"),
      mc("After a vowel, the ezafe becomes:", "-ye",
         ["-e", "-i", "-â"]),
      fill("'Ali's mother' = mâdar-___ Ali", "e",
           expl="After a consonant: -e"),
      mc("'A big house' = ?", "khâne-ye bozorg",
         ["bozorg khâne", "khâne bozorg", "bozorg-e khâne"]),
      mc("Ezafe is used to:", "link a noun to what follows it",
         ["mark the direct object", "mark the subject", "form plurals"]),
      fill("'The color of the sky' = rang-e ___", "âsmân"),
    ]
  },

  # ── 6 ────────────────────────────────────────────────────────
  { "name": "6. Adjectives",
    "lesson": """\
Adjectives come AFTER the noun, linked by ezafe:
  ketâb-e bozorg    = a big book       (NOT: bozorg ketâb)
  mard-e khub       = a good man
  dokhtar-e bâhush  = an intelligent girl

Key facts:
  - NO gender agreement (unlike French or Spanish)
  - NO number agreement — adjective stays the same for plurals
  - Stack multiple adjectives with ezafe:
    ketâb-e khub-e jadid  = a good new book

Comparison:
  bozorg-tar    = bigger       (-tar = comparative)
  bozorg-tarin  = biggest      (-tarin = superlative)
  Superlative precedes the noun: khub-tarin ketâb (the best book)""",
    "exercises": [
      mc("'A big house' in Farsi:", "khâne-ye bozorg",
         ["bozorg khâne", "bozorg-e khâne", "khâne bozorg"]),
      fill("'A beautiful girl' = dokhtar-e ___", "zibâ",
           hint="zibâ = beautiful"),
      mc("Adjectives in Farsi agree with nouns in:", "nothing — no agreement",
         ["gender", "number", "both"]),
      fill("'bigger' = bozorg___", "tar"),
      mc("'The best book' = ?", "khub-tarin ketâb",
         ["ketâb-e khub-tarin", "ketâb khub-tarin", "khub-tar ketâb"]),
      mc("Where does the adjective go?", "after the noun, with ezafe",
         ["before the noun", "before the verb", "at the end"]),
      fill("'A new red car' = mâshin-e qermez-e ___", "jadid",
           hint="jadid = new"),
    ]
  },

  # ── 7 ────────────────────────────────────────────────────────
  { "name": "7. Possessive Suffixes",
    "lesson": """\
Possessive suffixes attach directly to the noun:
  -am    = my         -emân  = our
  -at    = your       -etân  = your (pl./formal)
  -ash   = his/her    -eshân = their

After a consonant (most nouns):
  ketâb-am  ketâb-at  ketâb-ash
  ketâb-emân  ketâb-etân  ketâb-eshân

After a vowel:
  khâne-am  khâne-at  khâne-ash  (same suffixes)

Alternative emphatic form: noun + ezafe + pronoun
  ketâb-e man = MY book (emphasising possession)""",
    "exercises": [
      mc("'My book' in Farsi:", "ketâb-am",
         ["ketâb-at", "ketâb-ash", "ketâb-emân"]),
      fill("'his/her mother' = mâdar-___", "ash"),
      mc("'our house' = ?", "khâne-emân",
         ["khâne-am", "khâne-eshân", "khâne-etân"]),
      fill("'your (pl./formal) friend' = doost-___", "etân"),
      mc("'their book' = ?", "ketâb-eshân",
         ["ketâb-emân", "ketâb-etân", "ketâb-ash"]),
      fill("'my name' = esm-___", "am"),
      mc("'your (informal) house' = ?", "khâne-at",
         ["khâne-am", "khâne-ash", "khâne-etân"]),
    ]
  },

  # ── 8 ────────────────────────────────────────────────────────
  { "name": "8. Object Marker râ",
    "lesson": """\
'râ' marks a DEFINITE or SPECIFIC direct object.
It comes directly after the noun or pronoun it marks.

  With râ (definite/specific):
    ketâb râ khândam.   = I read THE book.      (specific book)
    u râ didam.         = I saw HIM / HER.
    Ali râ shenâkhtam.  = I recognized Ali.

  Without râ (indefinite / nonspecific):
    ketâbi khândam.     = I read A book.        (some book)
    film didam.         = I watched a film.

Colloquial speech: râ shortens to -o / -ro attached to noun:
  ketâb-o khândam  (spoken)  =  ketâb râ khândam  (formal)""",
    "exercises": [
      mc("'I read the book' (definite):", "ketâb râ khândam",
         ["ketâbi khândam", "ketâb khândam", "râ ketâb khândam"]),
      mc("'I read a book' (indefinite):", "ketâbi khândam",
         ["ketâb râ khândam", "ketâb khândam", "râ ketâbi khândam"]),
      fill("'I saw him/her' = u ___ didam", "râ"),
      mc("'râ' marks objects that are:", "definite or specific",
         ["indefinite", "plural only", "animate only"]),
      fill("'She called me' = u man ___ sedâ zad", "râ"),
      mc("In colloquial speech, râ often becomes:", "-o or -ro attached to noun",
         ["disappears entirely", "-râ attached to verb", "-i suffix"]),
      mc("Which is correct for 'He loves her'?", "u râ dust dârad",
         ["u dust dârad", "dust dârad u", "u dust dârad râ"]),
    ]
  },

  # ── 9 ────────────────────────────────────────────────────────
  { "name": "9. Prepositions",
    "lesson": """\
Basic prepositions (come BEFORE the noun):
  dar      = in, at          be       = to, toward
  az       = from, of        bâ       = with
  barâye   = for             tâ       = until, up to
  bedune   = without

Spatial prepositions (use ezafe to link to noun):
  ruy-e    = on top of       zir-e    = under
  kenâr-e  = beside          jelo-ye  = in front of
  posht-e  = behind          tu-ye    = inside of
  birun-e  = outside of      miân-e   = between

Example:  ruy-e miz = on the table  (not: ruy miz)""",
    "exercises": [
      mc("'in the house' = ?", "dar khâne",
         ["be khâne", "az khâne", "bâ khâne"]),
      mc("'to school' = ?", "be madrese",
         ["dar madrese", "az madrese", "barâye madrese"]),
      fill("'from Tehran' = ___ Tehrân", "az"),
      mc("'on the table' = ?", "ruy-e miz",
         ["dar miz", "zir-e miz", "be miz"]),
      fill("'with my friend' = ___ doost-am", "bâ"),
      mc("'for you' = ?", "barâye to", ["bâ to", "az to", "dar to"]),
      fill("'under the chair' = ___ sandali", "zir-e"),
    ]
  },

  # ── 10 ───────────────────────────────────────────────────────
  { "name": "10. SOV Word Order",
    "lesson": """\
Farsi is Subject–Object–Verb (SOV).
The VERB always goes at the END of the sentence.

  English (SVO):  I      read    the book.
  Farsi   (SOV):  man    ketâb râ    khândam.
                  S      O           V

More examples:
  Ali mâdar-ash râ dust dârad.  = Ali loves his mother.
  u be mâdrese raft.             = He/she went to school.
  mâ diruz film didim.           = We watched a film yesterday.

Rules:
  - Adjectives come AFTER nouns (with ezafe)
  - Time words usually follow the subject
  - Even in questions, the verb stays at the end""",
    "exercises": [
      scr("Put in correct order:  man / ketâb râ / khândam",
          "man ketâb râ khândam", hint="Subject – Object – Verb"),
      mc("In Farsi, the verb goes:", "at the end of the sentence",
         ["at the start", "right after the subject", "anywhere"]),
      scr("Put in correct order:  Ali / be mâdrese / raft",
          "Ali be mâdrese raft"),
      fill("'She reads the newspaper.' — what word comes last?\n  u ruzname râ ___", "mikhânad"),
      mc("Which has correct Farsi word order?", "man âb râ khordam",
         ["man khordam âb râ", "khordam man âb râ", "âb man râ khordam"]),
      scr("Put in correct order:  mâ / diruz / film / didim",
          "mâ diruz film didim"),
      mc("'Ali saw Sara' in Farsi:", "Ali Sârâ râ did",
         ["Ali did Sârâ râ", "did Ali Sârâ râ", "Sârâ râ did Ali"]),
    ]
  },

  # ── 11 ───────────────────────────────────────────────────────
  { "name": "11. Present Tense",
    "lesson": """\
Formation:  mi-  +  PRESENT STEM  +  personal ending
Personal endings:  -am, -i, -ad, -im, -id, -and

Verb stems (infinitive → present stem):
  kardan  (to do)   → kon  :  mikonam, mikoni, mikonad...
  raftan  (to go)   → rav  :  miravam, miravi, miravad...
  khândan (to read) → khân :  mikhânam, mikhâni, mikhânad...
  didan   (to see)  → bin  :  mibinam, mibini, mibinad...
  goftan  (to say)  → gu   :  miguyam, miguyi, miguyad...
  âmadan  (to come) → â    :  miâyam, miâyi, miâyad...
  dânestan(to know) → dân  :  midânam, midâni, midânad...""",
    "exercises": [
      mc("'I go' in Farsi:", "miravam",
         ["mikonam", "miraftam", "beravad"]),
      mc("'She reads' in Farsi:", "mikhânad",
         ["mikhânid", "mikhânam", "mikhândam"]),
      fill("'We do' = mi___im", "kon", expl="mikonim"),
      mc("'They come' in Farsi:", "miâyand",
         ["miâyim", "miâyad", "miâyam"]),
      fill("'You (inf.) see' = mi___i", "bini", expl="mibini"),
      mc("The 'mi-' prefix marks:", "present / habitual tense",
         ["past tense", "future tense", "subjunctive"]),
      fill("'I say' = mi___am", "guy", expl="miguyam"),
    ]
  },

  # ── 12 ───────────────────────────────────────────────────────
  { "name": "12. Negation",
    "lesson": """\
Negation rule depends on the tense:

  Present tense — 'ne-' REPLACES 'mi-':
    mikonam  → nemikonam   (I don't do)
    miravam  → nemiravam   (I don't go)

  Past tense — 'na-' prefix before the verb:
    raftam   → naraftam    (I didn't go)
    kard     → nakard      (he/she didn't do)

  To be — special negative paradigm:
    hastam → nistam   (I am not)
    bud    → nabud    (he/she wasn't)

  Imperative — 'na-' WITHOUT 'be-':
    boro!  → naro!    (don't go!)
    bekon! → nakon!   (don't do!)""",
    "exercises": [
      mc("'I don't go' in Farsi:", "nemiravam",
         ["naraftam", "miravam na", "bemiravam"]),
      mc("'She didn't do' in Farsi:", "nakard",
         ["nemikonad", "kard na", "nakonad"]),
      fill("'We don't read' = ne___im", "mikhân",
           expl="nemikhânim"),
      mc("'Don't go!' (negative imperative):", "naro!",
         ["nabaro!", "nemiro!", "naborid!"]),
      fill("'He was not' = na___", "bud", expl="nabud"),
      mc("Present tense negation prefix:", "ne- (replaces mi-)",
         ["na-", "bi-", "nist-"]),
      fill("'I didn't see' = na___am", "did", expl="nadidam"),
    ]
  },

  # ── 13 ───────────────────────────────────────────────────────
  { "name": "13. Past Tense",
    "lesson": """\
Formation:  PAST STEM  +  personal ending   (NO mi- prefix)

Past stem = infinitive minus -an (usually):
  kardan→kard   raftan→raft   khândan→khând
  didan→did     goftan→goft   âmadan→âmad
  dâshtan→dâsht  zadan→zad   budan→bud

Personal endings: -am, -i, Ø (3rd sg), -im, -id, -and
  raftam, rafti, raft, raftim, raftid, raftand

Key: 3rd person singular has NO ending — just the bare stem:
  raft = he/she/it went    kard = he/she/it did

Negative: na- + past stem:
  naraftam (I didn't go), nakard (he/she didn't do)""",
    "exercises": [
      mc("'She went' in Farsi:", "raft", ["raftam", "raftid", "rafti"]),
      mc("'We did' in Farsi:", "kardim", ["kardam", "kardand", "kardid"]),
      fill("'They read' = khând___", "and", expl="khândand"),
      mc("'I didn't come' in Farsi:", "nayâmadam",
         ["namiâyam", "nayâmad", "nemiâmadam"]),
      fill("'You (inf.) saw' = did___", "i", expl="didi"),
      mc("Past stem of 'goftan' (to say):", "goft",
         ["gu", "guf", "gofte"]),
      fill("'He didn't do' = na___", "kard", expl="nakard"),
    ]
  },

  # ── 14 ───────────────────────────────────────────────────────
  { "name": "14. Future Tense",
    "lesson": """\
Formation:  conjugated khâstan (no mi-)  +  past stem of main verb

Auxiliary conjugation:
  khâham / khâhi / khâhad / khâhim / khâhid / khâhand

Examples:
  khâham raft    = I will go
  khâhad kard    = he/she will do
  khâhim khând   = we will read
  khâhand did    = they will see

Negative — na- before khâh-:
  nakhâham raft  = I will not go

Spoken tip: Present tense is commonly used for near future:
  fardâ miram    = I'm going tomorrow  (lit. tomorrow I go)""",
    "exercises": [
      mc("'I will go' in Farsi:", "khâham raft",
         ["khâham raftan", "miravam", "beravad"]),
      mc("'She will do' in Farsi:", "khâhad kard",
         ["khâhim kard", "khâhad kardan", "mikonad"]),
      fill("'We will read' = khâhim ___", "khând"),
      mc("'I will not go' in Farsi:", "nakhâham raft",
         ["nemiravam", "namiravad", "benaravam"]),
      fill("'They will see' = khâh___ did", "and",
           expl="khâhand did"),
      mc("In spoken Farsi, near future is often expressed with:",
         "present tense",
         ["a separate future suffix", "past tense", "subjunctive only"]),
      fill("'You will do' = khâh___ kard", "i",
           expl="khâhi kard"),
    ]
  },

  # ── 15 ───────────────────────────────────────────────────────
  { "name": "15. Subjunctive Mood",
    "lesson": """\
Formation:  be-  +  PRESENT STEM  +  personal endings
Personal endings: -am, -i, -ad, -im, -id, -and

  kardan → bekonam, bekoni, bekonad, bekonim, bekonid, bekonand
  raftan → beravam, beravi, beravad, beravim, beravid, beravand
  âmadan → biyâyam, biyâyi, biyâyad, biyâyim, biyâyid, biyâyand

Triggers for subjunctive:
  mikhâham  (I want):  mikhâham bekonam    (I want to do it)
  bâyad     (must):    bâyad beravi         (you must go)
  shâyad    (maybe):   shâyad biyâyad       (he/she might come)
  Also after: tâ (so that), nemitavânestan (to be unable), etc.

Negative — drop be-, add na-:
  nakonam (that I not do),  naravam (that I not go)""",
    "exercises": [
      mc("'that I do' (subjunctive):", "bekonam",
         ["mikonam", "konam", "bekonid"]),
      mc("'you must go' = bâyad ___:", "beravi",
         ["miravi", "raftam", "beravid"]),
      fill("'I want to read' = mikhâham be___am", "khân",
           expl="mikhâham bekhânam"),
      mc("'maybe he comes' = shâyad ___:", "biyâyad",
         ["miâyad", "âmad", "biyâyid"]),
      fill("Negative subjunctive: drop be-, add ___ before the stem", "na-"),
      mc("'bâyad' means:", "must / should",
         ["maybe", "I want", "I can"]),
      fill("'that we not go' = na___im", "rav", expl="naravim"),
    ]
  },

  # ── 16 ───────────────────────────────────────────────────────
  { "name": "16. Imperative Mood",
    "lesson": """\
Singular (informal):  be-  +  present stem
  boro!     = go!          bekon!    = do!
  bekhân!   = read!        biyâ!     = come!
  bebin!    = look / see!  bekhâb!   = sleep!
  beneshín! = sit down!

Plural / formal:  be-  +  present stem  +  -id
  borid!     = go! (pl.)   bekonid!  = do! (pl.)
  bekhânid!  = read! (pl.)

Negative imperative:  na-  +  present stem  (NO be-)
  naro!     = don't go!    nakon!    = don't do!
  nakhân!   = don't read!  nayâ!     = don't come!""",
    "exercises": [
      mc("'Go!' (singular informal):", "boro!",
         ["naro!", "beravad!", "raft!"]),
      mc("'Do it!' (plural/formal):", "bekonid!",
         ["bekonam!", "nakon!", "bekonad!"]),
      fill("'Read!' (singular) = be___!", "khân", expl="bekhân!"),
      mc("'Don't come!' (neg. imperative):", "nayâ!",
         ["biyâ!", "nemiâyi!", "nabiyâ!"]),
      fill("'Look / See!' (singular) = be___!", "bin", expl="bebin!"),
      mc("Negative imperative is formed with:", "na- + stem (no be-)",
         ["be- + na- + stem", "ne- + stem", "stem + -ma"]),
      fill("'Don't sleep!' = na___!", "khâb", expl="nakhâb!"),
    ]
  },

  # ── 17 ───────────────────────────────────────────────────────
  { "name": "17. Progressive Aspect",
    "lesson": """\
Formation:  dâshtan (conjugated)  +  full present tense verb
Expresses an action IN PROGRESS right now.

  dâram  mikonam   = I am doing
  dâri   mikoni    = you are doing
  dârad  mikonad   = he/she is doing
  dârim  mikonim   = we are doing
  dârid  mikonid   = you (pl.) are doing
  dârand mikonand  = they are doing

Past progressive:  past of dâshtan  +  present tense verb
  dâshtam mikardam  = I was doing
  dâsht   miraft    = he/she was going

Negative — negate dâshtan:
  nadâram miravam   = I am not going""",
    "exercises": [
      mc("'I am going' in Farsi:", "dâram miravam",
         ["miravam", "dâram raftan", "dâshtam miravam"]),
      mc("'She is reading' in Farsi:", "dârad mikhânad",
         ["mikhânad", "dârad khândan", "dârad mikhânid"]),
      fill("'We are doing' = dârim mi___im", "kon",
           expl="dârim mikonim"),
      mc("'I was eating' in Farsi:", "dâshtam mikhordam",
         ["dâram mikhordam", "dâshtam khordam", "mikhordam"]),
      fill("'They are coming' = dârand mi___and", "ây",
           expl="dârand miâyand"),
      mc("Progressive is formed with:", "dâshtan + present tense verb",
         ["mi- prefix alone", "bâyad + verb", "be- + stem"]),
      fill("'You are not going' = na___i miravi", "dâr",
           expl="nadâri miravi"),
    ]
  },

  # ── 18 ───────────────────────────────────────────────────────
  { "name": "18. Present Perfect",
    "lesson": """\
Formation:  PAST PARTICIPLE  +  present enclitic of budan

Past participle  =  past stem  +  -e:
  raft→rafte   kard→karde   did→dide
  khând→khânde   âmad→âmade   goft→gofte

Present enclitics of budan:
  -am, -i, -e/-ast (3rd sg), -im, -id, -and

  rafte-am  = I have gone
  karde-i   = you have done
  dide      = he/she has seen   (or dide-ast)
  rafte-im  = we have gone
  karde-id  = you (pl.) have done
  dide-and  = they have seen

Negative — na- before the past participle:
  narafte-am  = I have not gone""",
    "exercises": [
      mc("Past participle of 'raftan' (to go):", "rafte",
         ["raft", "raftan", "rafter"]),
      mc("'I have gone' in Farsi:", "rafte-am",
         ["raftam", "miravad", "beravad"]),
      fill("'She has done' = karde-___", "ast",
           hint="3rd person singular; plain 'karde' is also fine"),
      mc("'We have read' in Farsi:", "khânde-im",
         ["khândam", "mikhânim", "khânde-and"]),
      fill("Past participle of 'didan' (to see) = ___", "dide"),
      mc("'I have not come' = ?", "nayâmade-am",
         ["namiâyam", "nayâmadam", "nabiyâyam"]),
      fill("'They have seen' = dide-___", "and"),
    ]
  },

  # ── 19 ───────────────────────────────────────────────────────
  { "name": "19. Past Perfect",
    "lesson": """\
Formation:  PAST PARTICIPLE  +  past of budan

Past of budan: budam / budi / bud / budim / budid / budand

  rafte budam   = I had gone
  karde budi    = you had done
  dide bud      = he/she had seen
  khânde budim  = we had read
  rafte budid   = you (pl.) had gone
  karde budand  = they had done

Used for actions completed BEFORE another past action:
  vaghti âmadam, Ali rafte bud.
  = When I arrived, Ali had already gone.

Negative:  na-  +  past participle  +  budan:
  narafte budam  = I had not gone""",
    "exercises": [
      mc("'I had gone' in Farsi:", "rafte budam",
         ["raftam", "rafte-am", "bude raftam"]),
      mc("'She had read' in Farsi:", "khânde bud",
         ["khând", "khânde-ast", "khândam"]),
      fill("'We had done' = karde ___im", "bud",
           expl="karde budim"),
      mc("'They had seen' in Farsi:", "dide budand",
         ["dide-and", "did budand", "dide budan"]),
      fill("'You had not gone' = na___ budi", "rafte"),
      mc("Past perfect describes:", "an action completed before another past event",
         ["a current action", "a future action", "a habitual action"]),
      fill("'He had come' = âmade ___", "bud",
           expl="âmade bud"),
    ]
  },

  # ── 20 ───────────────────────────────────────────────────────
  { "name": "20. Passive Voice",
    "lesson": """\
Formation:  PAST PARTICIPLE  +  shodan (to become)

  Present passive:  xânde mishavad     = it is read / being read
  Past passive:     xânde shod         = it was read
  Future passive:   xânde khâhad shod  = it will be read
  Perfect passive:  xânde shode-ast    = it has been read

shodan — present:
  mishavam, mishavi, mishavad, mishavim, mishavid, mishavand
shodan — past:
  shodam, shodi, shod, shodim, shodid, shodand

To express the agent (by…):  be vasile-ye + noun
  ketâb be vasile-ye Ali xânde shod.
  = The book was read by Ali.""",
    "exercises": [
      mc("'The door was opened' = ?", "dar bâz shod",
         ["dar bâz kard", "dar bâz mishod", "dar bâz konad"]),
      fill("'It is written' = neveshte mi___ad", "shav",
           expl="neveshte mishavad"),
      mc("'The book will be read' = ?", "ketâb xânde khâhad shod",
         ["ketâb xânde mishavad", "ketâb xânde shod", "ketâb xânde bud"]),
      fill("Passive voice uses past participle + ___", "shodan"),
      mc("'By Ali' (agent) in Farsi:", "be vasile-ye Ali",
         ["az Ali", "bâ Ali", "barâye Ali"]),
      fill("'It has been done' = karde shode-___", "ast"),
      mc("Passive in Farsi uses:", "past participle + shodan",
         ["past participle + kardan", "mi- + past stem", "be- + stem + shodan"]),
    ]
  },

  # ── 21 ───────────────────────────────────────────────────────
  { "name": "21. Question Formation",
    "lesson": """\
YES/NO questions — two ways:
  1. Add 'âyâ' at the start (formal):
       âyâ miâyi?    = Are you coming?
  2. Rising intonation alone (spoken):
       miâyi?         = Are you coming?

QUESTION WORDS (WH-questions):
  chi / che  = what       ki       = who
  kojâ       = where      key      = when
  cheghadr   = how much   chetour  = how
  cherâ      = why        chand    = how many

Word order stays SOV even in questions!
  Ali kojâ raft?     = Where did Ali go?   (Ali where went?)
  chi khândi?        = What did you read?
  cherâ nayâmadi?    = Why didn't you come?""",
    "exercises": [
      mc("'Where did Ali go?':", "Ali kojâ raft?",
         ["kojâ Ali raft?", "Ali raft kojâ?", "kojâ raft Ali?"]),
      mc("'What did you read?':", "chi khândi?",
         ["chi mikhâni?", "che khândid?", "chi khândam?"]),
      fill("'Why didn't you come?' = ___ nayâmadi?", "cherâ"),
      mc("Yes/no questions can be formed with:", "âyâ at start OR rising intonation",
         ["only âyâ", "only rising intonation", "a special verb suffix"]),
      fill("'Who came?' = ___ âmad?", "ki"),
      mc("'How much does it cost?':", "cheghadr ast?",
         ["chetour ast?", "cherâ ast?", "chand ast?"]),
      fill("'When will you come?' = ___ miâyi?", "key"),
    ]
  },

  # ── 22 ───────────────────────────────────────────────────────
  { "name": "22. Compound Verbs",
    "lesson": """\
Compound verb  =  noun / adjective  +  light verb (very common!)

With kardan (to do / make):
  kâr kardan      = to work        telefon kardan  = to call
  tamiz kardan    = to clean       hess kardan     = to feel

With shodan (to become):
  xaste shodan    = to get tired   gom shodan      = to get lost
  xoshhal shodan  = to become happy   âsheq shodan = to fall in love

With dâshtan (states / feelings):
  dust dâshtan    = to like / love     yâd dâshtan = to remember

With zadan (idiomatic uses):
  harf zadan      = to speak       rang zadan      = to paint
  dam zadan       = to rest

NEGATION goes on the light verb:
  kâr nemikonam   = I'm not working   (NOT: nakâr mikonam)""",
    "exercises": [
      mc("'to work' in Farsi:", "kâr kardan",
         ["kâr budan", "kâr shodan", "kâr zadan"]),
      mc("'to get tired' in Farsi:", "xaste shodan",
         ["xaste kardan", "xaste dâshtan", "xaste budan"]),
      fill("'to speak' = harf ___", "zadan"),
      mc("'I like/love him' in Farsi:", "u râ dust dâram",
         ["u râ dust mikonam", "u râ dust misham", "u dust dâshtam"]),
      fill("'I am not working' = kâr ne___am", "mikonam",
           expl="kâr nemikonam — negation is on the light verb"),
      mc("'to call (by phone)' in Farsi:", "telefon kardan",
         ["telefon zadan", "telefon shodan", "telefon dâshtan"]),
      fill("'to get lost' = gom ___", "shodan"),
    ]
  },

  # ── 23 ───────────────────────────────────────────────────────
  { "name": "23. Relative Clauses",
    "lesson": """\
Relative clauses use 'ke' (that / who / which).
The antecedent noun often takes '-i' (indefiniteness marker).

  mard-i ke âmad          = the man who came
  ketâb-i ke khândam      = the book that I read
  zan-i ke dust dâram     = the woman whom I like
  chizi ke goftam         = the thing that I said

'ke' also introduces complement clauses after verbs:
  mibinam ke miâyi.       = I see that you are coming.
  fekr mikonam ke raft.   = I think that he went.

Rules:
  - The relative clause comes IMMEDIATELY after its noun
  - The verb inside stays at the end of the relative clause""",
    "exercises": [
      mc("'the man who came':", "mard-i ke âmad",
         ["mard ke âmad", "mard âmad ke", "ke mard âmad"]),
      fill("'the book that I read' = ketâb-i ___ khândam", "ke"),
      mc("'ke' in relative clauses means:", "that / who / which",
         ["and", "but", "because"]),
      fill("'I think that...' = fekr mikonam ___...", "ke"),
      mc("'the woman I like' = ?", "zan-i ke dust dâram",
         ["zan ke dâram dust", "zan-i dust dâram ke", "ke zan-i dust dâram"]),
      fill("The antecedent in a relative clause often takes suffix: ___", "-i"),
      mc("Where does the relative clause go?",
         "immediately after the noun it modifies",
         ["at the start of the sentence", "at the end of the sentence",
          "before the subject"]),
    ]
  },

  # ── 24 ───────────────────────────────────────────────────────
  { "name": "24. Conditional Sentences",
    "lesson": """\
'agar' (if) introduces the conditional clause.

REAL / POSSIBLE  (agar + subjunctive  →  present or future):
  agar biyâyi, khoshhâl misham.
  = If you come, I'll be happy.

UNREAL / HYPOTHETICAL PRESENT  (agar + past  →  result + -i):
  agar miâmadi, khoshhâl mishodi.
  = If you came (hypothetically), I'd be happy.

PAST UNREAL  (agar + past perfect  →  past conditional):
  agar âmade budi, khoshhâl shode budam.
  = If you had come, I would have been happy.

Useful:
  vagarna / dar gheyrelinsurat = otherwise
  vali / ammâ = but""",
    "exercises": [
      mc("'If you come, I'll be happy' uses:",
         "agar + subjunctive",
         ["agar + past tense", "agar + future khâham", "agar + imperative"]),
      fill("'if' in Farsi = ___", "agar"),
      mc("'agar miâmadi, khoshhâl mishodi' expresses:",
         "an unreal/hypothetical present condition",
         ["a real future condition", "a past fact", "a command"]),
      fill("'If you had come…' = agar âmade ___, khoshhâl shode budam",
           "budi"),
      mc("Real/possible conditions use which mood?", "subjunctive",
         ["imperative", "plain past tense", "future tense"]),
      fill("Past unreal conditionals: agar + ___ perfect", "past"),
      mc("'agar nemiâyi, namiram' means:",
         "if you don't come, I won't go",
         ["if you came, I went", "if you will come, go", "come or I won't go"]),
    ]
  },

]


# ══════════════════════════════════════════════════════════════
# MENUS
# ══════════════════════════════════════════════════════════════

def show_main_menu(progress):
    header()
    print()
    done     = sum(1 for t in TOPICS if t["name"] in progress)
    mastered = sum(1 for t in TOPICS
                   if progress.get(t["name"], {}).get("best", 0) >= 80)
    print(f"  Topics studied: {done}/{len(TOPICS)}    Mastered (≥80%): {mastered}/{len(TOPICS)}")
    print()
    hr()
    print()
    print("  1.  Study a topic")
    print("  2.  Practice weak areas")
    print("  3.  View all progress")
    print("  4.  Quit")
    print()

def show_topic_list(progress):
    header("SELECT A TOPIC")
    print()
    for i, t in enumerate(TOPICS, 1):
        rec  = progress.get(t["name"], {})
        best = rec.get("best", -1)
        if best < 0:
            tag = "  new"
        elif best >= 80:
            tag = f"★ {best}%"
        else:
            tag = f"  {best}%"
        print(f"  {i:2}.  {t['name']:<38}  {tag}")
    print()
    print("   0.  Back")
    print()

def show_progress(progress):
    header("YOUR PROGRESS")
    print()
    attempted = mastered = 0
    for t in TOPICS:
        rec = progress.get(t["name"], {})
        if rec:
            attempted += 1
            best = rec.get("best", 0)
            last = rec.get("last", 0)
            att  = rec.get("attempts", 0)
            if best >= 80:
                mastered += 1
                status = "★ mastered"
            elif best >= 60:
                status = "○ learning"
            else:
                status = "✗ needs work"
            print(f"  {t['name']}")
            print(f"      best {best}%  last {last}%  attempts {att}  — {status}")
        else:
            print(f"  {t['name']}")
            print(f"      not yet studied")
        print()
    hr()
    print(f"  Studied: {attempted}/{len(TOPICS)}    Mastered: {mastered}/{len(TOPICS)}")
    print()
    input("  Press Enter to return...")


# ── Entry point ───────────────────────────────────────────────

def main():
    progress = load_progress()

    while True:
        show_main_menu(progress)
        try:
            choice = input("  Choose (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            choice = "4"

        if choice == "1":
            while True:
                show_topic_list(progress)
                try:
                    raw = input("  Topic number (0 to go back): ").strip()
                except (KeyboardInterrupt, EOFError):
                    break
                if raw == "0":
                    break
                if raw.isdigit() and 1 <= int(raw) <= len(TOPICS):
                    run_topic(TOPICS[int(raw) - 1], progress)
                else:
                    print("  Invalid choice — enter a number from the list.")
                    input("  Press Enter...")

        elif choice == "2":
            practice_weak(TOPICS, progress)

        elif choice == "3":
            show_progress(progress)

        elif choice == "4":
            header()
            print("\n  .خداحافظ — Goodbye! Keep studying Farsi!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
