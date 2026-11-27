"""Rebuild the master tracker from what actually exists on disk (never from claims).

Outputs: PROJECT_TRACKER/MASTER_SPREADSHEET.csv, MASTER_SPREADSHEET.xlsx, STATUS.md, and the `videos` block of tracker.json.
Run: python3 PROJECT_TRACKER/update_tracker.py   (from studio root or anywhere)
"""
import json, os, glob, csv, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NICHES = [("CAVE_DIVING_20", "Cave diving"), ("SCUBA_DIVING_20", "Scuba diving"), ("MURDER_MYSTERY_20", "Murder & mystery"), ("HAUNTED_20", "Haunted & paranormal")]


def ex(*p):
    return os.path.exists(os.path.join(ROOT, *p))


def stage(id_):
    qc = os.path.join(ROOT, "QUALITY_CONTROL", id_, "QC_REPORT.md")
    qc_pass = os.path.exists(qc) and "VERDICT: PASS" in open(qc).read()
    final = ex("FINAL_VIDEOS", f"{id_}.mp4")
    flags = {
        "script": ex("SCRIPTS", id_, "script.json"),
        "storyboard": ex("STORYBOARDS", id_, "STORYBOARD.md"),
        "packaging": ex("THUMBNAILS", id_, "PACKAGING.md"),
        "factcheck": ex("QUALITY_CONTROL", id_, "FACTCHECK.md"),
        "narration": ex("AUDIO", id_, "narration.wav"),
        "shots_py": ex("BLENDER_PROJECTS", id_, "shots.py"),
        "ready": ex("BLENDER_PROJECTS", id_, "READY"),
        "rendered_shots": len([d for d in glob.glob(os.path.join(ROOT, "RENDERS", id_, "*")) if os.path.isdir(d)]),
        "final_video": final,
        "thumbnail": bool(glob.glob(os.path.join(ROOT, "THUMBNAILS", id_, "*.png"))),
        "qc_pass": qc_pass,
    }
    if qc_pass:
        s = "QC PASSED"
    elif final:
        s = "RENDERED - QC pending"
    elif flags["ready"]:
        s = "ANIMATED - in render queue"
    elif flags["shots_py"]:
        s = "ANIMATING"
    elif flags["script"]:
        s = "SCRIPTED"
    else:
        s = "CONCEPT"
    return s, flags


def main():
    rows = []
    srcs = [(os.path.join(ROOT, "VIDEO_IDEAS", f, "concepts.json"), f, cat) for f, cat in NICHES]
    rcat = {"CAVE": "Cave diving (reserve)", "SCUBA": "Scuba diving (reserve)", "MURDER": "Murder & mystery (reserve)", "HAUNT": "Haunted & paranormal (reserve)"}
    for rp in sorted(glob.glob(os.path.join(ROOT, "VIDEO_IDEAS", "RESERVE_20", "*_reserve.json"))):
        srcs.append((rp, "RESERVE_20", rcat.get(os.path.basename(rp).split("_")[0], "Reserve")))
    for p, folder, cat in srcs:
        if not os.path.exists(p):
            continue
        try:
            data = json.load(open(p))
        except Exception as e:
            print("unreadable", p, e)
            continue
        for c in data:
            s, fl = stage(c["id"])
            sc = c.get("scores", {})
            rows.append({
                "id": c["id"], "category": cat, "rank": c.get("rank", c.get("number")), "working_title": c.get("working_title"),
                "alt_title": c.get("alt_title"), "subject": (c.get("subject") or "")[:300], "duration_s": c.get("duration_s"),
                "demand": sc.get("demand"), "story": sc.get("story"), "packaging": sc.get("packaging"), "retention": sc.get("retention"),
                "feasibility": sc.get("feasibility"), "total": c.get("total"), "difficulty": c.get("difficulty"),
                "verification": c.get("verification_status", ""), "status": s,
                "script": f"SCRIPTS/{c['id']}/" if fl["script"] else "", "storyboard": f"STORYBOARDS/{c['id']}/" if fl["storyboard"] else "",
                "final_video": f"FINAL_VIDEOS/{c['id']}.mp4" if fl["final_video"] else "",
                "thumbnail": f"THUMBNAILS/{c['id']}/" if fl["thumbnail"] else "", "qc": "PASS" if fl["qc_pass"] else "",
                "concept_file": f"VIDEO_IDEAS/{folder}/" + ("RESERVE_CONCEPTS.md" if folder == "RESERVE_20" else "CONCEPTS.md"),
            })
    out = os.path.join(ROOT, "PROJECT_TRACKER")
    keys = list(rows[0].keys()) if rows else []
    with open(os.path.join(out, "MASTER_SPREADSHEET.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(rows)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        wb = Workbook()
        ws = wb.active
        ws.title = "All 100 concepts"
        ws.append(keys)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="1F2937")
        for r in rows:
            ws.append([r[k] for k in keys])
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions
        for col, wd in zip("ABCDEFG", (10, 18, 6, 44, 44, 60, 9)):
            ws.column_dimensions[col].width = wd
        wb.save(os.path.join(out, "MASTER_SPREADSHEET.xlsx"))
    except Exception as e:
        print("xlsx skipped:", e)
    tj_p = os.path.join(out, "tracker.json")
    tj = json.load(open(tj_p)) if os.path.exists(tj_p) else {}
    tj["updated"] = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"
    tj["videos"] = {r["id"]: r["status"] for r in rows if r["status"] != "CONCEPT"}
    json.dump(tj, open(tj_p, "w"), indent=1)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    by_cat = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    lines = ["# STATUS (auto-generated from disk by update_tracker.py)", "", f"Updated: {tj['updated']}", "",
             "## Concept counts", ""] + [f"- {k}: {v}" for k, v in by_cat.items()] + [f"- **Total: {len(rows)}**", "", "## Pipeline status", ""]
    lines += [f"- {k}: {v}" for k, v in sorted(counts.items())]
    lines += ["", "## Videos in production", "", "| ID | Title | Score | Status |", "|---|---|---|---|"]
    for r in rows:
        if r["status"] != "CONCEPT":
            lines.append(f"| {r['id']} | {r['working_title']} | {r['total']} | {r['status']} |")
    open(os.path.join(out, "STATUS.md"), "w").write("\n".join(lines) + "\n")
    print(f"{len(rows)} concepts; " + ", ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()
    try:  # keep the upload kit (subtitles + titles/descriptions for QC-passed Shorts) in step with the tracker
        import subprocess, sys
        subprocess.run([sys.executable, os.path.join(ROOT, "PIPELINE", "upload_kit.py")], check=False)
    except Exception as e:
        print("upload kit skipped:", e)
