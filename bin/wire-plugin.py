#!/usr/bin/env python3
"""Enable a cloned plugin in shell.json and disable the stock one it replaces.

    wire-plugin.py <shell.json> <new-id> <replaced-id>

Mirrors what `omarchy plugin clone` records, so `omarchy plugin remove` can put
the stock plugin back later.
"""
import json, sys


def main(path, new_id, replaced):
    with open(path) as fh:
        cfg = json.load(fh)

    plugins = cfg.setdefault("plugins", [])
    if not any(p.get("id") == new_id for p in plugins):
        plugins.append({"id": new_id})

    disabled = cfg.setdefault("disabledPlugins", [])
    if replaced not in disabled:
        disabled.append(replaced)

    restores = cfg.setdefault("cloneSourceRestores", [])
    if new_id not in restores:
        restores.append(new_id)

    with open(path, "w") as fh:
        json.dump(cfg, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
