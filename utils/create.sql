DROP TABLE IF EXISTS task_tests;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS user_repositories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    git_username VARCHAR(100) PRIMARY KEY NOT NULL,
    creation_date timestamp NOT NULL
);

CREATE TABLE user_repositories (
    git_username VARCHAR(100) NOT NULL,
    repository_name VARCHAR(200) NOT NULL,
    PRIMARY KEY(git_username, repository_name),
    FOREIGN KEY(git_username) REFERENCES users(git_username)
);

CREATE TABLE projects (
    project_name VARCHAR(20) PRIMARY KEY NOT NULL,
    corrector_class VARCHAR(100),
    date_from timestamp NOT NULL,
    date_to   timestamp NOT NULL
);

CREATE TABLE tasks (
	task_name VARCHAR(30) NOT NULL,
    project_name VARCHAR(20) NOT NULL,
    corrector_method VARCHAR(100),
    PRIMARY KEY(task_name, project_name),
    FOREIGN KEY(project_name) REFERENCES projects(project_name)
);

CREATE TABLE task_tests (
	task_name VARCHAR(30) NOT NULL,
    project_name VARCHAR(20) NOT NULL,
    release_name VARCHAR(50) NOT NULL,
    git_username VARCHAR(100) NOT NULL,
    repository_name VARCHAR(200) NOT NULL,
    grade NUMERIC(7, 4) NOT NULL,
    date_run timestamp NOT NULL,
    test_status VARCHAR(50) check(test_status = 'PASS' or test_status = 'ERROR' or test_status = 'FAILED'),
    issue_text TEXT,
    PRIMARY KEY(task_name, project_name, release_name, git_username, repository_name),
    FOREIGN KEY(task_name, project_name) REFERENCES tasks(task_name, project_name),
    FOREIGN KEY(git_username, repository_name) REFERENCES user_repositories(git_username, repository_name) 
);
