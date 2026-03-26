from datetime import datetime, timedelta


class MockTaskBoard:
    """
    In-memory mock of an ET editorial task board (mock Jira/Notion).
    Singleton — shared across all agents.
    """

    def __init__(self):
        self._tasks: dict[str, dict] = {}

    def create(self, task: dict) -> str:
        tid = task["id"]
        self._tasks[tid] = {**task, "last_updated": datetime.now().isoformat()}
        return tid

    def get(self, task_id: str) -> dict | None:
        return self._tasks.get(task_id)

    def get_all(self) -> list[dict]:
        return list(self._tasks.values())

    def exists(self, title: str) -> bool:
        return any(t["title"] == title for t in self._tasks.values())

    def update_status(self, task_id: str, status: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = status
            self._tasks[task_id]["last_updated"] = datetime.now().isoformat()

    def mark_done(self, task_id: str):
        """NEW: Mark task as completed"""
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "done"
            self._tasks[task_id]["last_updated"] = datetime.now().isoformat()

    def send_nudge(self, task_id: str):
        """Mock Slack nudge — logs that notification was sent."""
        if task_id in self._tasks:
            self._tasks[task_id]["nudge_sent"] = True
            self._tasks[task_id]["last_updated"] = datetime.now().isoformat()

    def simulate_stall(self, task_id: str):
        """
        Demo helper: rewinds last_updated by 49h so the
        tracker sees it as stalled.
        """
        if task_id in self._tasks:
            fake_time = datetime.now() - timedelta(hours=49)
            self._tasks[task_id]["last_updated"] = fake_time.isoformat()
            self._tasks[task_id]["status"] = "pending"

    def clear(self):
        self._tasks = {}


# Singleton
task_board = MockTaskBoard()