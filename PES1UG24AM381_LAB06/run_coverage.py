"""Run real coverage commands and retain their output for Lab 6 evidence."""

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["baseline", "code", "branch"])
    args = parser.parse_args()
    os.chdir(Path(__file__).resolve().parent)
    output = Path("reports")
    output.mkdir(exist_ok=True)
    tests = {"baseline": "test_bus_transit.py",
             "code": "CodeCoverageTest_bus_transit_fare.py",
             "branch": "BranchCoverageTest_bus_transit_fare.py"}
    env = dict(os.environ, COVERAGE_FILE=f".coverage.{args.stage}",
               PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    modes = [False, True] if args.stage == "baseline" else [args.stage == "branch"]
    transcript = []
    for branch in modes:
        commands = [["run", *(["--branch"] if branch else []),
                     "--source=bus_transit_fare", "-m", "pytest", tests[args.stage], "-q"],
                    ["report", "-m", *([] if args.stage == "baseline" else ["--fail-under=90"])],
                    ["json", "-o", str(output / f"{args.stage}_{'branch' if branch else 'line'}.json")]]
        for command in commands:
            prompt = "$ python -m coverage " + shlex.join(command)
            print(prompt, flush=True)
            result = subprocess.run([sys.executable, "-m", "coverage", *command],
                                    env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            print(result.stdout, end="", flush=True)
            transcript.extend([prompt, result.stdout.rstrip()])
            if result.returncode:
                raise SystemExit(result.returncode)
    (output / f"{args.stage}_coverage.txt").write_text("\n".join(transcript) + "\n")


if __name__ == "__main__":
    main()
