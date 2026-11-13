"""Re-run the three fuzz properties against the preserved buggy processor.

An exit status of 1 and three failing properties are the expected result.
The current working application is never overwritten.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="se_lab7_before_") as directory:
    directory = Path(directory)
    shutil.copy2(root / "evidence" / "processor_before.py", directory / "processor.py")
    shutil.copy2(root / "test_processor.py", directory / "test_processor.py")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "test_processor.py", "-q", "--tb=no",
        "-k", "no_crash or safe",
    ], cwd=directory)
    raise SystemExit(result.returncode)
