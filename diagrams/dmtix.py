"""Builds skills/dmtix/dmtix.svg: the doors of dmtix (flow) and the artefacts they write."""
from svgkit import Canvas, T

c = Canvas(1640, 1075, "dmtix: the doors and what they write",
           "The doors in order: bootstrap once per project, optional discuss-project, start, go, and a "
           "checkpoint where the run stops and you review. Below them, the artefacts: method config, "
           "thought notes, live state in tk, narrative records, and the ticks engine.")
YOU, AG = T["you"], T["agent"]
c.text(35, 62, "dmtix: the doors, one rhythm", size=44, weight="bold", fill=T["strong"])
c.text(35, 104, "You decide at the doors. Agents do the run. Every door leaves files behind.", size=24, fill=T["muted"])
c.legend(1390, 52)

c.text(35, 160, "THE DOORS", size=20, weight="bold", fill=T["muted"])
c.text(1605, 160, "left to right", size=20, fill=T["muted"], anchor="end")

XS = [35, 355, 675, 995, 1315]
W, TOP, H = 290, 175, 430


def door(i, name, cmd, who, color, dash=None, fill=T["panel"]):
    x = XS[i]
    c.box(x, TOP, W, H, stroke=color, fill=fill, rx=16, sw=3, dash=dash)
    c.text(x + 22, TOP + 48, name, size=36, weight="bold", fill=color if color == YOU else T["strong"])
    c.text(x + 22, TOP + 82, cmd, size=21, fill=YOU, mono=True)
    c.text(x + 22, TOP + 112, who, size=20, fill=T["muted"])
    return x + 22


def writes(x, lines):
    y = TOP + H - 24 - 24 * (len(lines) - 1)
    c.text(x, y - 30, "writes", size=18, fill=T["muted"])
    c.lines(x, y, lines, size=20, lh=24, fill=YOU, mono=True)


# 1 bootstrap
x = door(0, "Set up", "/dmtix bootstrap", "once per project", YOU)
c.lines(x, TOP + 160, ["check the ticks skill", "tk init", "add lifecycle sections", "to the config", "make the records tree"],
        size=21, lh=30)
writes(x, [".tick/config.md", ".devmeta/"])

# 2 discuss-project (optional)
x = door(1, "Discuss", "/dmtix discuss-project", "optional: you + Claude", YOU, dash="12 9", fill=T["bg"])
c.lines(x, TOP + 160, ["not clear yet?", "Claude asks, you answer", "it hunts unknowns", "ends with a verdict:", "ready, not ready, dropped"],
        size=21, lh=30)
writes(x, ["docs/thoughts/"])

# 3 start
x = door(2, "Start", "/dmtix start", "you decide, the engine drafts", YOU)
c.lines(x, TOP + 160, ["goal and scope", "epics: engine drafts,", "you ratify", "a definition of done", "for every epic"],
        size=21, lh=30)
writes(x, ["_overview.md", "tk roadmap", "current-increment.md"])

# 4 go (agents)
x = door(3, "Go", "/dmtix go", "you start it, agents run", AG)
by = TOP + 134
for k, (t1, t2) in enumerate([("Plan", "split into ticks"), ("Waves", "parallel, own worktrees"),
                              ("Close-out", "review, retro, records")]):
    yy = by + k * 64
    c.box(x - 6, yy, W - 32, 46, stroke=AG, fill=T["panel2"], rx=10)
    c.text(x + 4, yy + 20, t1, size=20, weight="bold", fill=T["strong"])
    c.text(x + 4, yy + 39, t2, size=18, fill=T["muted"])
    if k < 2:
        c.arrow([(x + 130, yy + 46), (x + 130, yy + 64)], color=T["agent_dark"], sw=2)
writes(x, ["ia-cycles/<epic>.md", "project-history.md"])

# 5 checkpoint (you)
x = door(4, "Checkpoint", "the run stops", "back to you", YOU)
c.lines(x, TOP + 160, ["a report is waiting", "you review it,", "smoke-test the result", "and land it yourself"], size=21, lh=30)
c.text(x, TOP + 300, "agents never merge to main", size=18, fill=T["muted"])
writes(x, ["completion.md"])

# arrows between doors
for i in range(4):
    dashed = "8 6" if i in (0, 1) else None
    col = T["agent_dark"] if i != 3 else T["agent_dark"]
    c.arrow([(XS[i] + W + 3, TOP + 172), (XS[i + 1] - 3, TOP + 172)], color=col, sw=3, dash=dashed)

# artefact layer
AY, AH = 695, 235
c.text(35, 665, "THE ARTEFACTS: what the doors write and read", size=20, weight="bold", fill=T["muted"])


def art(x, w, name, sub, items, lh=26):
    c.box(x, AY, w, AH, stroke=T["line"], fill=T["bg"], rx=14, sw=2)
    c.text(x + 20, AY + 40, name, size=28, weight="bold", fill=T["strong"])
    c.text(x + 20, AY + 68, sub, size=18, fill=T["muted"])
    return c.lines(x + 20, AY + 104, items, size=20, lh=lh, fill=YOU, mono=True)


art(XS[0], W, "Method", "how you work; rarely edited", [".tick/config.md"])
c.wrapped(XS[0] + 20, AY + 168, "go reads it at each epic close-out and at the checkpoint", W - 40, size=18, fill=T["muted"])
art(XS[1], W, "Thoughts", "dated notes, one per talk", ["docs/thoughts/", "  YYYY-MM-DD-slug.md"])
c.wrapped(XS[1] + 20, AY + 168, "plain talk and notes: no ticks, no code", W - 40, size=18, fill=T["muted"])
art(XS[2], W, "Live state", "what is true now", ["tk roadmap", "tk board", ".tick/profile.md"])
c.wrapped(XS[2] + 20, AY + 200, "epics and ticks; go keeps them current", W - 40, size=18, fill=T["muted"])

RX, RW = XS[3], XS[4] + W - XS[3]
c.box(RX, AY, RW, AH, stroke=T["line"], fill=T["bg"], rx=14, sw=2)
c.text(RX + 20, AY + 40, "Records", size=28, weight="bold", fill=T["strong"])
c.text(RX + 20, AY + 68, "what happened, in prose; kept in git", size=18, fill=T["muted"])
c.lines(RX + 20, AY + 104, [".devmeta/", "  current-increment.md", "  project-history.md"], size=20, lh=26, fill=YOU, mono=True)
c.lines(RX + 330, AY + 104, ["  increments/<id>/", "    _overview.md", "    ia-cycles/", "    completion.md"], size=20, lh=26, fill=YOU, mono=True)
c.text(RX + 20, AY + 205, "bootstrap makes the tree; start, go and the checkpoint fill it", size=18, fill=T["muted"])

# door -> artefact arrows
def down(xx, y0=TOP + H + 4, y1=AY - 4, color=None):
    c.arrow([(xx, y0), (xx, y1)], color=color or T["agent"], sw=3)

down(XS[0] + W // 2)
down(XS[1] + W // 2, color=T["agent"])
down(XS[2] + W // 2 - 40)                     # start -> live state
c.arrow([(XS[2] + W - 50, TOP + H + 4), (XS[2] + W - 50, 650), (RX + 40, 650), (RX + 40, AY - 4)], sw=3)  # start -> records
down(RX + 150)                                # go -> records
down(XS[4] + W // 2)                          # checkpoint -> records

# engine bar
c.box(35, 957, 1570, 72, stroke=T["line"], fill=T["panel"], rx=14, sw=2)
c.text(57, 992, "Engine", size=28, weight="bold", fill=T["strong"])
c.text(190, 992, "~/.claude/skills/ticks/", size=21, fill=YOU, mono=True)
c.text(57, 1018, "go hands over to the ticks skill. All the loop logic lives there, not in dmtix. One engine per machine.",
       size=19, fill=T["muted"])

c.save("skills/dmtix/dmtix.svg")
