class TaskBoard:
    def __init__(self):
        self.tasks = {}

    def create(self, task):
        self.tasks[task["id"]] = task
        return task["id"]

    def exists(self, description):
        return any(t["description"] == description for t in self.tasks.values())

    def get_all(self):
        return list(self.tasks.values())


task_board = TaskBoard()