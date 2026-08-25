#!/usr/bin/env python3
"""Place the two tengwar modules either side of the clock in shell.json.

Idempotent: run it twice and nothing moves. If the clock has been moved to
another section, the tengwar follow it there rather than assuming the centre.
"""
import json, sys

SRC = "~/.config/omarchy/bar/modules/tengwar.qml"
LEFT = {"id": "tengwar-left", "type": "qml", "source": SRC, "phrase": "elen-sila"}
RIGHT = {"id": "tengwar-right", "type": "qml", "source": SRC, "phrase": "omentielvo"}


def main(path):
    with open(path) as fh:
        cfg = json.load(fh)

    layout = cfg.setdefault("bar", {}).setdefault("layout", {})
    if not any(k in layout for k in ("left", "center", "right")):
        layout.setdefault("center", [])

    # Drop any previous copies wherever they sit, so this can be re-run.
    for section, widgets in layout.items():
        layout[section] = [w for w in widgets
                           if str(w.get("id", "")) not in ("tengwar-left", "tengwar-right")]

    target, index = None, None
    for section, widgets in layout.items():
        for n, w in enumerate(widgets):
            if w.get("id") == "omarchy.clock":
                target, index = section, n
                break
        if target:
            break

    found = target is not None
    if not found:
        target = "center" if "center" in layout else next(iter(layout))
        layout.setdefault(target, [])
        index = len(layout[target])

    widgets = layout[target]
    widgets.insert(index, dict(LEFT))
    widgets.insert(index + 2, dict(RIGHT))

    with open(path, "w") as fh:
        json.dump(cfg, fh, indent=2)
        fh.write("\n")

    if found:
        print("  tengwar placed either side of the clock in bar.layout.%s" % target)
    else:
        print("  no omarchy.clock in the layout; tengwar appended to bar.layout.%s" % target)


if __name__ == "__main__":
    main(sys.argv[1])
