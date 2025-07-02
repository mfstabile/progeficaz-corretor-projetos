import mysql.connector
from mysql.connector import Error
import os
import time

class ConnectionHelper:
    conn = None
        
    @staticmethod
    def get_connection():
        if __class__.conn is None or __class__.conn.is_connected() == False:
            host_name = os.environ.get("DB_HOST")
            port = os.environ.get("DB_PORT")
            db_name = os.environ.get("DB_DATABASE")
            user_name = os.environ.get("DB_USERNAME")
            user_password = os.environ.get("DB_PASSWORD")

            __class__.conn = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name,
                port=port
            )
        return __class__.conn
    
    @staticmethod
    def close_connection():
        if __class__.conn is not None:
            __class__.conn.close()
            __class__.conn = None

def get_results(query, params=None):
    conn = ConnectionHelper.get_connection()

    cursor = conn.cursor()
    cursor.execute(query, params)
    regs = cursor.fetchall()

    return regs

def execute_commit_query(query, params=None):
    conn = ConnectionHelper.get_connection()

    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

def get_user_exists(git_username):
    query = """SELECT count(1)
                 FROM users u
                WHERE u.git_username = %(git_username)s"""

    params = {"git_username": git_username}
    res = get_results(query=query, params=params)
    return int(res[0][0]) > 0

def get_repo_exists(git_username, repository_name):
    query = """SELECT count(1)
            FROM user_repositories u
           WHERE u.git_username = %(git_username)s
             AND u.repository_name = %(repository_name)s"""
    
    params = {"git_username": git_username, "repository_name": repository_name}
    res = get_results(query=query, params=params)
    
    return int(res[0][0]) > 0

def insert_user(git_username):
    query =  "INSERT INTO users (git_username, creation_date) " + \
        "VALUES(%(git_username)s, NOW());"
    
    params = {"git_username": git_username}
    execute_commit_query(query, params)

def insert_repository(git_username, repository_name):
    query =  "INSERT INTO user_repositories (git_username, repository_name) " + \
        "VALUES(%(git_username)s, %(repository_name)s);"
    
    params = {"git_username": git_username, "repository_name": repository_name}
    execute_commit_query(query, params)

def get_project_runner(project_name):
    query = """SELECT p.corrector_class,
                      p.date_from,
                      p.date_to
                 FROM projects p
                WHERE p.project_name = %(project_name)s
                  AND p.date_from <= NOW()
                  AND p.date_to >= NOW()"""

    params = {
        "project_name": project_name,
    }
    res = get_results(query=query, params=params)
    print(res)
    print("*"*10)
    print(res[0])
    return res[0][0]

def get_tasks(project_name):
    query = """SELECT t.task_name,
                      t.corrector_method
                 FROM tasks t
                WHERE t.project_name = %(project_name)s"""

    params = {
        "project_name": project_name,
    }
    res = get_results(query=query, params=params)
    return res


def check_tag_submitted(git_username, repository_name, release_name):
    query = """SELECT count(1)
                 FROM task_tests t
                WHERE t.git_username = %(git_username)s
                  AND t.repository_name = %(repository_name)s
                  AND t.release_name = %(release_name)s"""

    params = {
        "git_username": git_username,
        "repository_name": repository_name,
        "release_name": release_name
    }
    res = get_results(query=query, params=params)
    return int(res[0][0]) > 0


def record_test_result(
    task_name,
    project_name,
    release_name,
    git_username,
    repository_name,
    grade,
    test_status,
    issue_text
):
    query = """
        INSERT INTO task_tests
            (
                task_name,
                project_name,
                release_name,
                git_username,
                repository_name,
                grade,
                date_run,
                test_status,
                issue_text
            )
        VALUES
            (
                %(task_name)s,
                %(project_name)s,
                %(release_name)s,
                %(git_username)s,
                %(repository_name)s,
                %(grade)s,
                NOW(),
                %(test_status)s,
                %(issue_text)s
            )"""

    params = {
        "task_name": task_name,
        "project_name": project_name,
        "release_name": release_name,
        "git_username": git_username,
        "repository_name": repository_name,
        "grade": grade,
        "test_status": test_status,
        "issue_text": issue_text
    }
    execute_commit_query(query=query, params=params)

def get_repo_release_status(git_username, repository_name, project_name):
    params = {
        "project_name": project_name,
        "git_username": git_username,
        "repository_name": repository_name
    }

    query = """SELECT t.task_name,
                    t.test_status
                FROM (
                    SELECT task_name, MAX(date_run) as max_date_run
                    FROM task_tests
                    WHERE project_name = %(project_name)s
                    AND git_username = %(git_username)s
                    AND repository_name = %(repository_name)s
                    GROUP BY task_name
                ) as latest_runs
                INNER JOIN task_tests t ON latest_runs.task_name = t.task_name
                                        AND latest_runs.max_date_run = t.date_run
                WHERE t.project_name = %(project_name)s
                AND t.git_username = %(git_username)s
                AND t.repository_name = %(repository_name)s
                ORDER BY t.date_run DESC"""
    res = get_results(query=query, params=params)
    return res