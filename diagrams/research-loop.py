"""Builds skills/research-loop/research-loop.svg: the doors of research-loop (flow) and the files they use."""
from svgkit import Canvas, T

c = Canvas(1640, 1125, "research-loop: the doors and the files",
           "Five doors: init once per repository, charter with the human, go (the lead runs the loop: assess, "
           "freeze, run, verdict, record), check (the ruler's holder scores and runs the independent check), "
           "and report. Below them the files: the research facts, the program's records in git on the lead's "
           "branch, the kept folder outside git that holds the ruler, and the report.")
YOU, AG = T["you"], T["agent"]
c.text(35, 62, "research-loop: a lead runs, a holder keeps the ruler", size=44, weight="bold", fill=T["strong"])
c.text(35, 104, "You set the question and the bar. The lead never grades its own work.", size=24, fill=T["muted"])
c.legend(1390, 52)

c.text(35, 160, "THE DOORS", size=20, weight="bold", fill=T["muted"])
c.text(1605, 160, "left to right", size=20, fill=T["muted"], anchor="end")

XS = [35, 355, 675, 995, 1315]
W, TOP, H = 290, 175, 430


def door(i, name, cmd, who, color, dash=None, fill=T["panel"]):
    x = XS[i]
    c.box(x, TOP, W, H, stroke=color, fill=fill, rx=16, sw=3, dash=dash)
    c.text(x + 22, TOP + 48, name, size=36, weight="bold", fill=YOU if color == YOU else T["strong"])
    c.text(x + 22, TOP + 82, cmd, size=21, fill=YOU, mono=True)
    c.text(x + 22, TOP + 112, who, size=20, fill=T["muted"])
    return x + 22


def writes(x, lines, label="writes"):
    y = TOP + H - 24 - 24 * (len(lines) - 1)
    c.text(x, y - 30, label, size=18, fill=T["muted"])
    c.lines(x, y, lines, size=20, lh=24, fill=YOU, mono=True)


# 1 init
x = door(0, "Init", "init", "once per repository", YOU)
c.lines(x, TOP + 160, ["read how the repo", "does research now", "adopt it, keep its names", "ask you what it cannot", "see; explain the setup"],
        size=21, lh=30)
writes(x, [".devmeta/research.md", "docs/research/README.md"])

# 2 charter
x = door(1, "Charter", "charter <slug>", "once per program, with you", YOU)
c.lines(x, TOP + 160, ["your purpose, your words", "the questions, the bar", "the ruler, who holds it", "the allowance, the end", "nothing runs before your go"],
        size=21, lh=30)
writes(x, ["charter.md", "program.md"])

# 3 go (the lead)
x = door(2, "Go", "go", "the lead: runs, no waiting", AG)
steps = [("Assess", "measure the floor first"), ("Freeze", "the rule, committed first"),
         ("Run", "sub-agents, cheap models"), ("Verdict", "read off the frozen rule"),
         ("Record", "files; then assess again")]
for k, (t1, t2) in enumerate(steps):
    yy = TOP + 122 + k * 46
    c.box(x - 6, yy, W - 32, 38, stroke=AG, fill=T["panel2"], rx=10)
    c.text(x + 4, yy + 17, t1, size=18, weight="bold", fill=T["strong"])
    c.text(x + 4, yy + 33, t2, size=16, fill=T["muted"])
    if k < 4:
        c.arrow([(x + 130, yy + 38), (x + 130, yy + 46)], color=T["agent_dark"], sw=2, head=False)
writes(x, ["loops/<NNN>-<short>.md"])

# 4 check (the holder)
x = door(3, "Check", "check <slug>", "the holder: owns the ruler", AG)
c.lines(x, TOP + 160, ["hold the keys, outside git", "read a freeze", "score the run on keys", "send counts, never the key",
                       "the independent check:", "a fresh agent, little context"], size=21, lh=30)
writes(x, ["<kept>/.../scores/", "<kept>/.../check-<date>/"], label="writes")

# 5 report
x = door(4, "Report", "report <slug>", "once, when an end is met", AG)
c.lines(x, TOP + 160, ["the lead writes it", "each question: the answer", "and what it rests on", "what it changes", "what to do next"],
        size=21, lh=30)
c.text(x, TOP + 330, "often: /dmtix start", size=19, fill=YOU, mono=True)
writes(x, ["report.md"])

# arrows between doors
for i in range(4):
    dashed = "8 6" if i == 0 else None
    if i == 2:   # go <-> check: counts come back
        c.arrow([(XS[i] + W + 3, TOP + 172), (XS[i + 1] - 3, TOP + 172)], color=T["agent_dark"], sw=3)
        c.arrow([(XS[i + 1] - 3, TOP + 200), (XS[i] + W + 3, TOP + 200)], color=T["agent_dark"], sw=3)
    else:
        c.arrow([(XS[i] + W + 3, TOP + 172), (XS[i + 1] - 3, TOP + 172)], color=T["agent_dark"], sw=3, dash=dashed)

# artefact layer
AY, AH = 690, 300
c.text(35, 664, "THE FILES", size=20, weight="bold", fill=T["muted"])


def art(x, w, name, sub, dash=None, stroke=None):
    c.box(x, AY, w, AH, stroke=stroke or T["line"], fill=T["bg"], rx=14, sw=2, dash=dash)
    c.text(x + 20, AY + 40, name, size=28, weight="bold", fill=T["strong"])
    c.text(x + 20, AY + 68, sub, size=18, fill=T["muted"])


def note(x, y, s, w):
    c.wrapped(x, y, s, w, size=18, fill=T["muted"])


art(XS[0], W, "Research facts", "one file, on the trunk")
c.lines(XS[0] + 20, AY + 104, [".devmeta/research.md", "docs/research/README.md"], size=20, lh=26, fill=YOU, mono=True)
note(XS[0] + 20, AY + 180, "rulers, allowance, bounds, where the kept folder is; the index of programs", W - 40)

RX, RW = XS[1], XS[2] + W - XS[1]
art(RX, RW, "Records: docs/research/<slug>/", "in git, on the lead's branch; committed each loop")
c.lines(RX + 20, AY + 104, ["charter.md", "program.md", "loops/"], size=20, lh=26, fill=YOU, mono=True)
c.lines(RX + 56, AY + 182, ["<NNN>-<short>.md", "<NNN>-<short>.scores.md", "<NNN>-<short>.manifest.md"], size=18, lh=24, fill=YOU, mono=True)
c.lines(RX + 400, AY + 104, ["arms/", "findings/", "checks/", "report.md"], size=20, lh=26, fill=YOU, mono=True)
note(RX + 20, AY + 268, "program.md starts with a status box: go resumes from it, never from memory", RW - 40)

KX = XS[3]
art(KX, W, "Kept folder", "outside git and every worktree", dash="12 9", stroke=YOU)
c.lines(KX + 20, AY + 104, ["<kept>/research/<slug>/", "ruler/  scores/", "data/   log.md"], size=19, lh=26, fill=YOU, mono=True)
note(KX + 20, AY + 190, "keys and hidden answers; a guard in the lead's worktree hides them", W - 40)

art(XS[4], W, "The report", "same records folder")
c.lines(XS[4] + 20, AY + 104, ["report.md", "findings/"], size=20, lh=26, fill=YOU, mono=True)
note(XS[4] + 20, AY + 168, "built from the verdicts, never from memory; names what to build, if anything", W - 40)

# door -> artefact arrows
def down(xx, y0=TOP + H + 4, y1=AY - 4):
    c.arrow([(xx, y0), (xx, y1)], color=T["agent"], sw=3)

down(XS[0] + W // 2)
down(XS[1] + W // 2)
down(XS[2] + W // 2)
down(XS[3] + W // 2)
down(XS[4] + W // 2)
# the holder reads the lead's records (read-only), shown dashed

# split bar
c.box(35, 1017, 1570, 80, stroke=T["line"], fill=T["panel"], rx=14, sw=2)
c.text(57, 1052, "Two roles, never one", size=28, weight="bold", fill=T["strong"])
c.text(57, 1082, "The lead never reads the ruler. The holder never writes on the lead's branch. "
       "The rule is committed before the run; the verdict is read off it.", size=19, fill=T["muted"])

c.save("skills/research-loop/research-loop.svg")
