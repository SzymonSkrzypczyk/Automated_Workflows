"""Reproduce the Czeladź investigation in a new local workspace."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def run(*args):
    print("\n$", " ".join(args), flush=True)
    subprocess.run([sys.executable, "-m", "eo_processing", *args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default="work/czeladz-reproduction",
                        help="New workspace, relative to the Lab 06 directory")
    args = parser.parse_args()
    workspace = (ROOT / args.workspace).resolve()
    if workspace.exists():
        parser.error(f"Workspace already exists: {workspace}; choose a new one")
    workspace.mkdir(parents=True)
    database = workspace / "catalogue.sqlite"
    run("init", "--database", str(database))
    run("register", "--database", str(database), "--bundle", str(ROOT / "submission/inputs"))

    for source, name in (("personal_batch.json", "batch"), ("personal_threshold010.json", "threshold010_batch")):
        config = json.loads((ROOT / "config" / source).read_text(encoding="utf-8-sig"))
        config["database"] = str(database)
        config["workspace"] = str(workspace)
        for job in config["jobs"]:
            job["plugin"] = str(ROOT / "extensions/ndbi.py")
        local_config = workspace / f"{name}_config.json"
        local_config.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        manifest = workspace / f"{name}.json"
        run("plan", "--config", str(local_config), "--out", str(manifest))
        run("run", "--manifest", str(manifest))
        run("assess", "--manifest", str(manifest), "--minimum-valid-fraction", "0.5")
        run("report", "--manifest", str(manifest), "--out", str(workspace / f"{name}_report"))

    subprocess.run([sys.executable, str(ROOT / "submission/compare_ndbi.py"),
                    str(workspace / "batch_report/report.json")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "submission/check_real_ndbi.py"),
                    str(workspace / "batch_report/report.json")], cwd=ROOT, check=True)
    print(f"\nResults saved in {workspace}")


if __name__ == "__main__":
    main()
