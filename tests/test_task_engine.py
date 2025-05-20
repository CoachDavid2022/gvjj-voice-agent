import unittest
import json
from pathlib import Path
import importlib.util

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "ava" / "task_engine.py"
spec = importlib.util.spec_from_file_location("task_engine", MODULE_PATH)
task_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task_engine)
Task = task_engine.Task
TaskEngine = task_engine.TaskEngine


def dummy_true():
    return True


def dummy_false():
    return False


class TestTaskEngine(unittest.TestCase):
    def test_run_all_tasks(self):
        tasks = [Task("t1", dummy_true), Task("t2", dummy_false)]
        engine = TaskEngine(tasks, log_path=Path("/tmp/task_engine_test.log"))
        results = engine.run()
        self.assertEqual(results, {"t1": True, "t2": False})


if __name__ == "__main__":
    unittest.main()
