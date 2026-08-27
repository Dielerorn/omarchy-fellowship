#!/usr/bin/env python3
"""Point the Omarchy menu's Screensaver row at the calm Fellowship one.

    wire-menu.py <omarchy-menu.jsonc>

Going idle runs the screensaver through the cloned idle plugin, but the menu
row (Super+Space -> Screensaver) is a separate path: it calls stock
`omarchy-launch-screensaver`, which cycles all 34 ttfx effects at random. Same
inscription, rainbow instead of Rivendell gold.

The file is JSONC with comments the user may well have written, so this is a
text insertion rather than a parse-and-dump: the row is replaced in place if it
is already there, and otherwise added before the closing brace.
"""
import os, re, sys

ROW = ('  "system.screensaver": {"action":'
       '"$HOME/.config/omarchy/bin/fellowship-launch-screensaver force"},')
NOTE = ("  // Launch the calm Fellowship screensaver rather than the stock one,\n"
        "  // which picks a random ttfx effect. Icon and label are inherited.\n")


def main(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write("{\n" + NOTE + ROW + "\n}\n")
        print("  created %s with the screensaver override" % path)
        return

    src = open(path).read()
    if re.search(r'^\s*"system\.screensaver"\s*:', src, re.M):
        src = re.sub(r'^\s*"system\.screensaver"\s*:.*$', ROW, src, count=1, flags=re.M)
        open(path, "w").write(src)
        print("  updated the existing system.screensaver row")
        return

    idx = src.rfind("}")
    if idx == -1:
        print("  %s has no closing brace; left alone" % path, file=sys.stderr)
        return 1
    head = src[:idx].rstrip()
    if head and not head.endswith((",", "{")):
        head += ","
    open(path, "w").write(head + "\n\n" + NOTE + ROW + "\n" + src[idx:])
    print("  added the screensaver override")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]) or 0)
