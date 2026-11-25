"""Builds skills/streams/streams.svg: how the seat runs streams (flow) and the files it keeps (artefacts)."""
from svgkit import Canvas, T

c = Canvas(1640, 1010, "streams: one seat, many streams",
           "Top: you talk to the seat in the main checkout. The seat cuts streams, each a branch in its own "
           "worktree run by its own session as a dmtix increment: one mainline and side streams. Streams land "
           "on the trunk; for now the seat does the landing by hand and pushes on your word. Below: the "
           "artefacts. The project file .devmeta/streams.md and each stream's brief and records are committed; "
           "coord/ in the git common dir (streams table, log, schedules, asks) is never committed.")
YOU, AG, MU, ST = T["you"], T["agent"], T["muted"], T["strong"]
c.text(35, 62, "streams: one seat, many streams", size=44, weight="bold", fill=ST)
c.text(35, 104, "You talk to the seat. The seat cuts streams and reads them all. Each stream runs its own increment.",
       size=24, fill=MU)
c.legend(1390, 52)

c.text(35, 160, "THE FLOW", size=20, weight="bold", fill=MU)
TOP, H = 175, 440

# you
c.box(35, TOP, 240, H, stroke=YOU, fill=T["you_tint"], rx=16, sw=3)
c.text(57, TOP + 48, "You", size=36, weight="bold", fill=YOU)
c.text(57, TOP + 82, "ask, decide, approve", size=20, fill=MU)
c.lines(57, TOP + 140, ["/streams init", "/streams status", "/streams queue", "/streams cut", "/streams land"],
        size=20, lh=34, fill=YOU, mono=True)
c.wrapped(57, TOP + 340, "say \"ship it\" before a push", 196, size=19, fill=MU)

# seat
SX, SW = 355, 330
c.box(SX, TOP, SW, H, stroke=AG, fill=T["panel"], rx=16, sw=3)
c.text(SX + 22, TOP + 48, "Seat", size=36, weight="bold", fill=ST)
c.text(SX + 22, TOP + 82, "main checkout, on the trunk", size=20, fill=MU)
c.lines(SX + 22, TOP + 130, ["cut: branch, worktree,", "brief, a row in the table", "status: running, waiting,",
                              "stalled, from files", "keep-running: hourly pass", "land: merge, check, push"],
        size=21, lh=32)
c.box(SX + 16, TOP + 336, SW - 32, 84, stroke=YOU, fill=T["bg"], rx=10, sw=2, dash="8 6")
c.text(SX + 30, TOP + 366, "First cut? It asks you:", size=20, weight="bold", fill=YOU)
c.text(SX + 30, TOP + 396, "side stream or mainline?", size=22, fill=YOU)

# streams
XX, XW = 765, 470
c.box(XX, TOP, XW, H, stroke=AG, fill=T["bg"], rx=16, sw=3)
c.text(XX + 22, TOP + 48, "Streams", size=36, weight="bold", fill=ST)
c.text(XX + 22, TOP + 82, "one branch, one worktree, one session each", size=20, fill=MU)
for k, (nm, sub, br) in enumerate([("mainline", "the main line of work", "inc07-2026-03-02"),
                                    ("side stream", "beside the mainline", "docs-2026-03-05"),
                                    ("side stream", "beside the mainline", "billing-2026-03-04")]):
    yy = TOP + 110 + k * 108
    c.box(XX + 18, yy, XW - 36, 92, stroke=AG, fill=T["panel2"], rx=10)
    c.text(XX + 34, yy + 30, nm, size=22, weight="bold", fill=ST)
    c.text(XX + 34, yy + 54, sub, size=18, fill=MU)
    c.text(XX + 34, yy + 78, "../app-" + br.split("-")[0], size=18, fill=YOU, mono=True)
    c.text(XX + XW - 34, yy + 30, "one dmtix increment", size=19, anchor="end")
    c.text(XX + XW - 34, yy + 54, "/dmtix go in its own session", size=18, anchor="end", fill=MU)
    c.text(XX + XW - 34, yy + 78, br, size=17, anchor="end", fill=YOU, mono=True)

# trunk
TX, TW = 1315, 290
c.box(TX, TOP, TW, H, stroke=AG, fill=T["panel"], rx=16, sw=3)
c.text(TX + 22, TOP + 48, "Trunk", size=36, weight="bold", fill=ST)
c.text(TX + 22, TOP + 82, "usually main", size=20, fill=MU)
c.lines(TX + 22, TOP + 140, ["a finished stream", "is merged here,", "the checks run,", "then the seat", "pushes the trunk"],
        size=21, lh=32)
c.text(TX + 22, TOP + 340, "landing is by hand", size=20, weight="bold", fill=ST)
c.text(TX + 22, TOP + 366, "for now: a checklist", size=20, fill=MU)
c.text(TX + 22, TOP + 392, "the seat follows", size=20, fill=MU)

# flow arrows
c.arrow([(278, TOP + 150), (352, TOP + 150)], color=YOU, sw=3)
c.arrow([(688, TOP + 150), (762, TOP + 150)], color=T["agent_dark"], sw=3)
c.text(692, TOP + 134, "cut", size=19, fill=MU)
c.arrow([(1238, TOP + 150), (1312, TOP + 150)], color=T["agent_dark"], sw=3)
c.text(1243, TOP + 134, "land", size=19, fill=MU)

# artefact layer
AY, AH = 665, 320
c.text(35, 650, "THE ARTEFACTS", size=20, weight="bold", fill=MU)


def tag(x, y, s, committed):
    col = T["agent_dark"] if committed else YOU
    c.text(x, y, s, size=18, weight="bold", fill=col)


def art(x, w, name, sub, items, committed, note, nlh=22):
    c.box(x, AY, w, AH, stroke=T["line"], fill=T["bg"], rx=14, sw=2)
    c.text(x + 20, AY + 40, name, size=28, weight="bold", fill=ST)
    c.text(x + 20, AY + 66, sub, size=18, fill=MU)
    c.lines(x + 20, AY + 102, items, size=19, lh=26, fill=YOU, mono=True)
    c.wrapped(x + 20, AY + 232, note, w - 40, size=18, lh=nlh, fill=MU)
    tag(x + 20, AY + AH - 18, "committed" if committed else "never committed", committed)


art(35, 330, "Project file", "facts the skill cannot guess",
    [".devmeta/streams.md", "- trunk", "- resources", "- at cut", "- at landing"], True,
    "written once by init; the seat reads it at every door")
art(395, 430, "coord/", "in the git common dir, one per machine",
    ["streams.md: one row per stream", "log.md: holds, hand-offs", "schedules.md: what runs on a clock",
     "asks.md: what waits on you"], False,
    "every worktree sees the same folder; status and queue read it; streams write the log")
art(855, 350, "At cut", "written into the new worktree",
    ["../app-<name>/", "docs/thoughts/", "> <date>-<name>-brief.md"], True,
    "the brief: where the stream is, what it holds, its neighbours, the rules")
art(1235, 370, "Stream records", "dmtix writes them on the branch",
    [".devmeta/increments/<id>/", "> _overview.md", "> ia-cycles/", "> completion.md"], True,
    "what happened, in prose; the seat reads completion.md before a landing")

# flow -> artefact arrows
c.arrow([(520, TOP + H + 4), (520, AY - 4)], color=T["agent"], sw=3)      # seat -> coord
c.arrow([(1000, TOP + H + 4), (1000, AY - 4)], color=T["agent"], sw=3)    # cut -> brief
c.arrow([(1420, TOP + H + 4), (1420, AY - 4)], color=T["agent"], sw=3)    # streams/dmtix -> records
c.arrow([(200, TOP + H + 4), (200, AY - 4)], color=YOU, sw=3)             # you/init -> project file

c.save("skills/streams/streams.svg")
