import json
import logging
import subprocess
from pathlib import Path
from typing import Callable, Dict, List


class Task:
    """Represents an executable task."""

    def __init__(self, name: str, action: Callable[[], bool]):
        self.name = name
        self.action = action
        self.success = None
        self.output = ""

    def run(self) -> bool:
        try:
            self.success = self.action()
        except Exception as exc:  # pragma: no cover - for unexpected runtime issues
            self.success = False
            self.output = str(exc)
        return self.success


class TaskEngine:
    """Simple engine to run a sequence of tasks with logging."""

    def __init__(self, tasks: List[Task], log_path: Path | None = None):
        self.tasks = tasks
        self.log_path = log_path or Path("task_engine.log")
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format="%(asctime)s %(message)s",
        )

    def run(self) -> Dict[str, bool]:
        results = {}
        for task in self.tasks:
            ok = task.run()
            results[task.name] = ok
            logging.info("%s: %s", task.name, "SUCCESS" if ok else "FAIL")
            if task.output:
                logging.info(task.output)
        return results


# --- predefined actions -------------------------------------------------

def validate_modules() -> bool:
    """Run validate_modules.py and return True if no issues printed."""
    script = Path(__file__).parent / "validate_modules.py"
    result = subprocess.run([
        "python",
        str(script),
    ], capture_output=True, text=True)
    return "No issues found" in result.stdout


def run_tests() -> bool:
    """Execute the project's unit tests."""
    result = subprocess.run([
        "python",
        "-m",
        "unittest",
        "discover",
        "-v",
    ])
    return result.returncode == 0


def main():  # pragma: no cover - CLI
    tasks = [
        Task("Validate modules", validate_modules),
        Task("Run tests", run_tests),
    ]
    engine = TaskEngine(tasks)
    results = engine.run()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
