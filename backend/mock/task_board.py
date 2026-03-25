class TaskBoard:
    def __init__(self):
        self.tasks = {}

    def create(self, task):
        self.tasks[task["id"]] = task
        return task["id"]
from datetime import datetime, timedelta

class TaskBoard:
    def __init__(self):
        self.tasks = {}

    def create(self, task):
        task["last_updated"] = datetime.now().isoformat()
        task["status"] = "pending"
        self.tasks[task["id"]] = task
        return task["id"]

    def exists(self, description):
        return any(t["description"] == description for t in self.tasks.values())

    def get_all(self):
        return list(self.tasks.values())

    def update_status(self, task_id, status):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["last_updated"] = datetime.now().isoformat()

    def simulate_stall(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id]["last_updated"] = (
                datetime.now() - timedelta(hours=49)
            ).isoformat()
    def exists(self, description):
        return any(t["description"] == description for t in self.tasks.values())

    def get_all(self):
        return list(self.tasks.values())


task_board = TaskBoard()