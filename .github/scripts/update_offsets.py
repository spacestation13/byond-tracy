#!/usr/bin/env python3
"""Fetch new BYOND offsets from sov's extractor and patch the header files and readme."""

import json
import os
import re
import sys
import urllib.request

API   = "https://sovexe.github.io/byond-tracy-offset-extractor/data.json"
ZEROS = ", ".join(["0x00000000"] * 11)


def main():
    with open("offsets/windows.h") as f:
        win = f.read()
    with open("offsets/linux.h") as f:
        nix = f.read()

    cur_max = int(re.search(r"#define BYOND_MAX_BUILD (\d+)", win).group(1))

    with urllib.request.urlopen(API) as r:
        data = json.loads(r.read().decode())

    # {1678: {"version": "516.1678", "windows": [...], "linux": [...]}}
    builds: dict[int, dict] = {}
    for item in data:
        _, build = item["version"].split(".")
        entry = builds.setdefault(int(build), {"version": item["version"]})
        entry[item["platform"]] = item["addresses"]

    new = sorted(b for b in builds if b > cur_max)
    if not new:
        print("Nothing to do.")
        return

    new_max = max(new)

    for build, platforms in sorted((b, builds[b]) for b in new):
        win_addrs = platforms.get("windows")
        nix_addrs = platforms.get("linux")

        if win_addrs:
            line = f"\t[BYOND_VERSION_ADJUSTED({build})] = {{{', '.join(win_addrs)}}},"
            win = win.replace("\n};", f"\n{line}\n}};", 1)

        if nix_addrs:
            line = f"\t[BYOND_VERSION_ADJUSTED({build})] = {{{', '.join(nix_addrs)}}},"
        elif win_addrs:
            ver = builds[build]["version"]
            line = f"\t[BYOND_VERSION_ADJUSTED({build})] = {{{ZEROS}}}, // note: {ver} was a Windows-only build"
        nix = nix.replace("\n};", f"\n{line}\n}};", 1)

    win = re.sub(r"#define BYOND_MAX_BUILD \d+", f"#define BYOND_MAX_BUILD {new_max}", win)
    nix = re.sub(r"#define BYOND_MAX_BUILD \d+", f"#define BYOND_MAX_BUILD {new_max}", nix)

    with open("offsets/windows.h", "w") as f:
        f.write(win)
    with open("offsets/linux.h", "w") as f:
        f.write(nix)

    # Prepend new rows to the readme version table (newest first)
    new_rows = []
    for build in reversed(new):
        ver = builds[build]["version"]
        w = ver if "windows" in builds[build] else "N/A"
        l = ver if "linux"   in builds[build] else "N/A"
        new_rows.append(f"| {w} | {l} |")

    with open("readme.md") as f:
        readme = f.read()

    sep = "| -------- | -------- |"
    readme = readme.replace(sep + "\n", sep + "\n" + "\n".join(new_rows) + "\n", 1)

    with open("readme.md", "w") as f:
        f.write(readme)

    print(f"Added {len(new)} build(s): {new}")

    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a") as f:
            f.write(f"new_max={new_max}\n")
            f.write(f"new_builds={','.join(str(b) for b in new)}\n")


if __name__ == "__main__":
    main()
