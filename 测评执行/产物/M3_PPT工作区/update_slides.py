#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐页整页覆盖更新飞书幻灯片，打印每页结果。"""
import argparse, json, subprocess, sys

IDS = ["pYY", "pYt", "pYi", "pYV", "pYF", "pYW", "pYc", "pYr", "pYl", "pYv"]
PID = "KdygsBjq4lu3d5dZdfVcx6ClnBe"

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True, help="源 XML 目录，如 v4")
ap.add_argument("--pages", default="1-10", help="页码范围，如 1-10 或 9,10")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

def parse_range(s):
    pages = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            pages.extend(range(int(a), int(b) + 1))
        elif part:
            pages.append(int(part))
    return pages

pages = parse_range(args.pages)
fail = 0
for p in pages:
    sid = IDS[p - 1]
    xml = f"{args.src}/slide-{p:02d}.xml"
    cmd = ["lark-cli", "slides", "+update-slide",
           "--presentation", PID, "--slide-id", sid, "--content", f"@{xml}"]
    if args.dry_run:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        ok = d.get("ok")
        err = d.get("error") or d.get("msg") or ""
    except Exception:
        ok = False
        err = (r.stdout or r.stderr)[:200]
    print(f"page {p:02d} ({sid}) <- {xml}: ok={ok} {err}", flush=True)
    if ok is not True:
        fail += 1
print(f"DONE total={len(pages)} fail={fail}")
sys.exit(1 if fail else 0)
