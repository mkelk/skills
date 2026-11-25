"""Builds skills/ticks/ticks.svg: the engine loop for one epic (flow) and the artefacts it uses."""
from svgkit import Canvas, T

c = Canvas(1640, 1000, "ticks: the loop for one epic and the files it uses",
           "Flow: you decide the roadmap, then the orchestrator plans the epic into ticks, runs waves of "
           "parallel implementers each in its own worktree with a tick gate, merges and runs the wave gate, "
           "runs a final review and a close-out retro, then continues with the next epic. At a project "
           "boundary the run stops for your checkpoint. Below: the tick files, config, learnings and profile "
           "in .tick, the worktrees and branches, the tk views, and the reports.")
YOU, AG = T["you"], T["agent"]
c.text(35, 62, "ticks: one loop per epic", size=44, weight="bold", fill=T["strong"])
c.text(35, 104, "You decide the roadmap. One orchestrator owns the state. Implementers only write code.",
       size=24, fill=T["muted"])
c.legend(1390, 52)

c.text(35, 160, "THE LOOP", size=20, weight="bold", fill=T["muted"])
c.text(1605, 160, "left to right; the next epic starts the loop again", size=20, fill=T["muted"], anchor="end")

W, G, TOP, H = 200, 28, 175, 380
XS = [35 + i * (W + G) for i in range(7)]


def stage(i, name, who, color, lines, dash=None, fill=T["panel"]):
    x = XS[i]
    c.box(x, TOP, W, H, stroke=color, fill=fill, rx=16, sw=3, dash=dash)
    c.text(x + 16, TOP + 40, name, size=28, weight="bold", fill=color if color == YOU else T["strong"])
    c.text(x + 16, TOP + 68, who, size=19, fill=T["you"] if color == YOU else T["muted"])
    return x + 16, c.lines(x + 16, TOP + 112, lines, size=20, lh=27)


stage(0, "Roadmap", "you", YOU, ["epics and their", "order", "a definition of", "done for each", "epic"])
x, _ = stage(1, "Plan", "orchestrator", AG, ["split the epic", "into ticks", "put them in", "waves", "add a review", "tick and a", "close-out tick"])

# waves: nested implementers
x, _ = stage(2, "Waves", "implementers", AG, ["parallel, each in", "its own worktree"])
for k, lab in enumerate(["tick A", "tick B", "tick C"]):
    yy = TOP + 180 + k * 56
    c.box(x - 4, yy, W - 24, 44, stroke=AG, fill=T["bg"], rx=10)
    c.text(x + 6, yy + 19, lab, size=19, weight="bold", fill=T["strong"])
    c.text(x + 6, yy + 38, "tick gate", size=17, fill=T["muted"])
c.text(x, TOP + 362, "each runs the tick gate", size=16, fill=T["muted"])

stage(3, "Merge", "orchestrator", AG, ["merge each branch", "run the wave gate", "on the merged", "tree", "then close the", "wave's ticks"])
stage(4, "Final review", "agents", AG, ["review the whole", "epic diff", "findings go back", "to the code's", "author"])
stage(5, "Close-out", "orchestrator", AG, ["check the epic", "against its done", "run the retro,", "write the", "learnings", "plan the next", "epic"])
stage(6, "Checkpoint", "you, at a project end", YOU,
      ["the run stops", "you read the", "completion report", "and decide"], dash="12 9", fill=T["you_tint"])

ay = TOP + 190
for i in range(6):
    col = T["you"] if i in (0, 5) else T["agent_dark"]
    dash = "8 6" if i == 5 else None
    c.arrow([(XS[i] + W + 3, ay), (XS[i + 1] - 3, ay)], color=col, sw=3, dash=dash)

# loop back: next epic (close-out -> plan)
yb = TOP + H + 30
c.arrow([(XS[5] + W // 2, TOP + H + 3), (XS[5] + W // 2, yb), (XS[1] + W // 2, yb), (XS[1] + W // 2, TOP + H + 4)],
        color=T["agent_dark"], sw=3)
c.text((XS[3] + XS[5]) // 2 + 60, yb - 8, "next epic: same loop, no new prompt", size=19, fill=T["muted"], anchor="middle")

# artefact layer
AY, AH = 640, 325
c.text(35, 628, "THE ARTEFACTS", size=20, weight="bold", fill=T["muted"])
BW = 380
BX = [35, 35 + 395, 35 + 790, 35 + 1185]


def art(i, name, sub):
    x = BX[i]
    c.box(x, AY, BW if i < 3 else 385, AH, stroke=T["line"], fill=T["bg"], rx=14, sw=2)
    c.text(x + 20, AY + 40, name, size=28, weight="bold", fill=T["strong"])
    c.text(x + 20, AY + 68, sub, size=18, fill=T["muted"])
    return x + 20


x = art(0, "Tracker", "in .tick/, kept in git")
c.lines(x, AY + 108, ["tick files", "  epics, ticks, state", ".tick/config.md", ".tick/profile.md", ".tick/learnings.md", ".tick/learnings-ref.md"],
        size=20, lh=26, fill=YOU, mono=True)
c.wrapped(x, AY + 275, "config is yours; profile and learnings are the engine's", BW - 40, size=17, fill=T["muted"])

x = art(1, "Code", "isolated, then merged")
c.lines(x, AY + 108, ["git worktree", "git branch"], size=20, lh=26, fill=YOU, mono=True)
c.text(x, AY + 172, "one per tick, or per chain of ticks", size=18, fill=T["muted"])
c.wrapped(x, AY + 232, "implementers write code here and never touch the tracker. Worktrees and branches stay until the final review is done.",
          BW - 40, size=17, fill=T["muted"])

x = art(2, "Views", "to look at, not to edit")
c.lines(x, AY + 108, ["tk roadmap", "tk board", "tk graph <epic>", "tk next <epic>"], size=20, lh=26, fill=YOU, mono=True)
c.wrapped(x, AY + 232, "roadmap shows epics in waves; graph shows ticks in waves; next gives the next action",
          BW - 40, size=17, fill=T["muted"])

x = art(3, "Reports", "prose, written by the loop")
c.lines(x, AY + 108, ["retro report", "completion report"], size=20, lh=26, fill=YOU, mono=True)
c.wrapped(x, AY + 180, "the retro report comes at each epic close-out; the completion report comes at a project checkpoint. Where they are kept is set in the config.",
          BW - 45, size=17, fill=T["muted"])

# flow -> artefact arrows

c.arrow([(XS[0] + W - 20, TOP + H + 4), (XS[0] + W - 20, AY - 4)], color=T["you"], sw=3)   # roadmap -> tracker
c.arrow([(XS[2] + W // 2, TOP + H + 4), (XS[2] + W // 2, AY - 4)], sw=3)                     # waves -> code
c.arrow([(XS[5] + W // 2 + 40, TOP + H + 4), (XS[5] + W // 2 + 40, AY - 4)], sw=3)           # close-out -> reports
c.arrow([(XS[6] + W // 2, TOP + H + 4), (XS[6] + W // 2, AY - 4)], color=T["you"], sw=3)     # checkpoint reads reports

c.save("skills/ticks/ticks.svg")
