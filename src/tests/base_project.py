import db.db_conn as db

class BaseProject:

    def __init__(self, git_username, repository, release, project_name):
        self.git_username = git_username
        self.repository = repository
        self.release = release
        self.project_name = project_name

    def report(self, task_name, issue_text, grade=0.0, test_status="ERROR"):
        db.record_test_result(
            task_name=task_name,
            project_name=self.project_name,
            release_name=self.release,
            git_username=self.git_username,
            repository_name=self.repository,
            grade=grade,
            test_status=test_status,
            issue_text=issue_text
        )