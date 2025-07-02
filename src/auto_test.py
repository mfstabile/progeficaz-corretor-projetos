import db.db_conn as db
# from tests.projeto1a import Projeto1A
from tests.projeto1 import Projeto1
from tests.base_project import BaseProject
from issuer_pusher import *

def auto_test(git_username, repository, release, project_name):
    print("Calling auto_test on background task")
    issue_msg = "# Problemas encontrados nos testes:\n\n"
    try:
        class_name = db.get_project_runner(project_name=project_name)
        print("Running tests for {} using {}".format(project_name, class_name))
    except Exception as e:
        print(f"Error running tests for {project_name}:" + str(e))
        push_issue(git_username=git_username, repository=repository, release=release, text=issue_msg + f"Não foi possível encontrar o projeto '{project_name}'. Verifique se o webhook está configurado corretamente e se o prazo de correção não se encerrou.")
        return


    tasks = db.get_tasks(project_name=project_name)

    if db.check_tag_submitted(git_username=git_username, repository_name=repository, release_name=release):
        push_issue(git_username=git_username, repository=repository, release=release, text=issue_msg + f"Não foi possível testar a tag '{release}'. A tag já foi testada anteriormente.")
        return

    str_runner = f'{class_name}("{git_username}", "{repository}", "{release}")'

    try:
        runner_object = eval(str_runner)
    except TimeoutError as te:
        msg = issue_msg + "Não foi possível inicializar o projeto. Verifique se o projeto pode ser executado pelo comando 'python servidor.py'."
        # msg += '\nGaranta que o valor da variável SERVER_HOST localizada no arquivo servidor.py esteja com o valor "0.0.0.0"'
        # msg += '\nAo testar em seu computador, basta acessar o link http://localhost:8080 ou http://127.0.0.1:8080 que a aplicação deve continuar funcionando.'
        push_issue(git_username=git_username, repository=repository, release=release, text=msg)
        return
    except Exception as e:
        msg = issue_msg + f"Não foi possível inicializar o projeto. O código gerou uma exceção inesperada: {e.__class__.__name__}: {e}"
        push_issue(git_username=git_username, repository=repository, release=release, text=msg)
        return
    
    return_messages = {}

    for task in tasks:
        task_name = task[0]
        method_name = task[1]

        method = getattr(runner_object, method_name)
        print(f"Running task {task_name} for {git_username}/{repository}")
        print('-------------------'*3)

        try:
            result = method(task_name)
            if result is not None:
                return_messages[task_name] = result
        except Exception as e:
            print(f"Error running task {task_name} for {git_username}/{repository}")
            print(e)
            print('-------------------'*3)
            msg = issue_msg + f"Não foi possível testar a tarefa '{task_name}'. O código gerou uma exceção inesperada: {e.__class__.__name__}: {e}"
            runner_object.report(task_name=task_name, issue_text=msg, test_status="FAILED")
            return_messages[task_name] = msg

    for task_name, return_message in return_messages.items():
        issue_msg += f"## {task_name}\n\n"
        issue_msg += f"{return_message}\n\n"
        
    if len(return_messages) != 0:
        push_issue(git_username=git_username, repository=repository, release=release, text=issue_msg)
        
    runner_object.end()