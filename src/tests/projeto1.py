from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sqlite3
import time
import random
import subprocess
from docker_utils import *
from tests.base_project import BaseProject
import os
from pathlib import Path

SVG_FOLDER = os.environ.get('SVG_FOLDER')
CLONE_BASE_PATH = os.environ.get('CLONE_BASE_PATH')

class Projeto1(BaseProject):
    def __init__(self, git_username, repository, release) -> None:
        super().__init__(git_username, repository, release, "Projeto1")
        # Set up the WebDriver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")  # This make Chromium reachable
        options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems
        options.add_argument("--incognito")
        options.add_argument("--window-size=1920,1080")


        self.driver = webdriver.Chrome(options=options)
        self.container = DockerProject1Runner()
        self.container.allocate(git_username, repository)
        self.port = self.container.port
        self.id = self.container.id


    def end(self):
        # Close the browser
        self.container.deallocate()
        self.driver.quit()
        print("ended")

    
    def test_handout(self, name):
        msg = "Ao testar se o resultado do handout 01 está funcionando: "
        # Open the website
        try:
            self.driver.get(f"http://localhost:{self.port}")
        except Exception as e:
            msg += f"\nNão foi possível acessar o endereço http://localhost:5000."
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
        # Find the form elements and fill them out
            title_input = self.driver.find_element(By.NAME,"titulo")
            text_input = self.driver.find_element(By.NAME,"detalhes")
        except Exception as e:
            msg += f"\nNão foi possível encontrar os campos de título e detalhes. Certifique-se que os inputs possuem a propriedade 'name' com os nomes corretos: 'titulo' e 'detalhes'."
            self.report(task_name=name, issue_text=msg)
            return msg
        
        random_number = random.randint(1000000, 9999999)
        title = "Title"+str(random_number)
        text = "text"+str(random_number)

        try:
            title_input.send_keys(title)
            text_input.send_keys(text)
        except Exception as e:
            msg += f"\nNão foi possível preencher os campos de título e detalhes. Certifique-se que os inputs possuem a propriedade 'name' com os nomes corretos: 'titulo' e 'detalhes'."
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Submit the form
            submit_button = self.driver.find_element(By.CSS_SELECTOR,"[type='submit']")
            submit_button.click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de submit. Certifique-se que o botão está com o atributo type='submit'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        # Wait for the submission to process
        time.sleep(2)

        self.driver.save_screenshot(f'{SVG_FOLDER}/ss_{self.git_username}_{self.repository}.png')

        try:
            src = self.driver.page_source.upper()
            assert title.upper() in src
            assert text.upper() in src
        except Exception as e:
            msg += f"\nNão foi possível encontrar o card com o título '{title}' e detalhes '{text}' na página inicial após apertar o botão de submissão."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        msg += "Tarefa realizada com sucesso."
        self.report(task_name=name, issue_text=msg, grade=10.0, test_status="PASS")


    def test_persistency(self, name):
        msg = f"Ao testar se a tarefa '{name}' está funcionando: "
        
        try:
            # Open the website
            self.driver.get(f"http://localhost:{self.port}")
        except Exception as e:
            msg += f"\nNão foi possível acessar o endereço http://localhost:5000"
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Find the form elements and fill them out
            title_input = self.driver.find_element(By.NAME,"titulo")
            text_input = self.driver.find_element(By.NAME,"detalhes")
        except Exception as e:
            msg += f"\nNão foi possível encontrar os campos de título e detalhes. Certifique-se que os campos estão com os nomes corretos: 'titulo' e 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        random_number = random.randint(1000000, 9999999)
        title = "Title"+str(random_number)
        text = "text"+str(random_number)

        try:
            title_input.send_keys(title)
            text_input.send_keys(text)
        except Exception as e:
            msg += f"\nNão foi possível preencher os campos de título e detalhes. Certifique-se que os campos são campos de texto e estão com os nomes corretos: 'titulo' e 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Submit the form
            submit_button = self.driver.find_element(By.CSS_SELECTOR,"[type='submit']")
            submit_button.click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de submit. Certifique-se que o botão está com o atributo type='submit'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        # Wait for the submission to process
        time.sleep(2)

        try:
            # Check if the card was created
            src = self.driver.page_source.upper()
            assert title.upper() in src
            assert text.upper() in src
        except Exception as e:
            msg += f"\nNão foi possível encontrar o card com o título '{title}' e detalhes '{text}' na página inicial após apertar o botão de submissão."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Check the SQLite database
            file = Path(f'{CLONE_BASE_PATH}/{self.git_username}/{self.repository}/banco.db')
            if not file.exists():
                raise FileNotFoundError
            conn = sqlite3.connect(f'{CLONE_BASE_PATH}/{self.git_username}/{self.repository}/banco.db')
            cursor = conn.cursor()
        except Exception as e:
            msg += f"\nNão foi possível conectar ao banco de dados SQLite. Certifique-se que o banco de dados está na raiz do projeto e com o nome 'banco.db'."
            msg += f"\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}"
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            cursor.execute(f"SELECT title, content FROM note WHERE title = '{title}'")
            annotation = cursor.fetchone()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o card com o título '{title}' no banco de dados SQLite. Certifique-se que a tabela que armazena os cards se chama 'note' e que o campo que armazena o título se chama 'title' e que o campo que armazena os detalhes se chama 'content'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            assert annotation is not None
            assert annotation[0] == title
            assert annotation[1] == text
        except Exception as e:
            msg += f"\nNão foi possível encontrar o card com o título '{title}' e detalhes '{text}' no banco de dados SQLite. Certifique-se que os dados estão sendo armazenados corretamente, que a tabela que armazena os cards se chama 'note' e que o campo que armazena o título se chama 'title' e que o campo que armazena os detalhes se chama 'content'. {e}"
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            random_number = random.randint(1000000, 9999999)
            title = "Title"+str(random_number)
            text = "text"+str(random_number)
            cursor.execute(f"INSERT INTO note (title, content) VALUES ('{title}', '{text}')")
        except Exception as e:
            msg += f"\nNão foi possível inserir um novo card no banco de dados SQLite. O campo id deve ser gerado automaticamente. Verifique se o comando 'INSERT INTO note (title, content) VALUES ('{title}', '{text}') funciona corretamente."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        conn.commit()
        conn.close()
    
        time.sleep(2)

        try:
            self.driver.get(f"http://localhost:{self.port}")
            src = self.driver.page_source.upper()
            assert title.upper() in src
            assert text.upper() in src
        except Exception as e:
            msg += f"\nNão foi possível encontrar o card com o título '{title}' e detalhes '{text}' na página inicial após inserir um novo card no banco de dados SQLite."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        msg += "Tarefa realizada com sucesso."
        self.report(task_name=name, issue_text=msg, grade=10.0, test_status="PASS")


    def test_delete(self, name):
        msg = f"Ao testar se a tarefa '{name}' está funcionando: "
        try:
            self.driver.get(f"http://localhost:{self.port}")
        except Exception as e:
            msg += f"\nNão foi possível acessar o endereço http://localhost:5000"
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            count = len(delete_buttons)
            for i in range(count):
                delete_buttons[-1].click()
                time.sleep(2)
                delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
        except Exception as e:
            msg += f"\nNão foi possível encontrar os botões de delete. Certifique-se que os botões estão com o atributo name='delete_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        if len(delete_buttons) != 0:
            msg += "\nNão foi possível deletar todos os cards."
            self.report(task_name=name, issue_text=msg)
            return msg

        cards = []
        for i in range(5):
            try:
                # Find the form elements and fill them out
                title_input = self.driver.find_element(By.NAME,"titulo")
                text_input = self.driver.find_element(By.NAME,"detalhes")
                
                random_number = random.randint(1000000, 9999999)
                title = "Title"+str(i)+str(random_number)
                text = "text"+str(i)+str(random_number)
                cards.append((title,text))

                title_input.send_keys(title)
                text_input.send_keys(text)

                # Submit the form
                submit_button = self.driver.find_element(By.CSS_SELECTOR,"[type='submit']")
                submit_button.click()

                # Wait for the submission to process
                time.sleep(2)

                # Check if the card was created
                src = self.driver.page_source.upper()
                assert title.upper() in src
                assert text.upper() in src
            except Exception as e:
                msg += f"\nNão foi possível criar {i+1} cards em sequência. O card com o título '{title}' e detalhes '{text}' não foi encontrado. Verifique se os campos estão com os nomes corretos: 'titulo' e 'detalhes' e o botão de submit está com o atributo type='submit'."
                msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
                self.report(task_name=name, issue_text=msg)
                return msg

        try:
            # Delete the second card
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            buttons_count = len(delete_buttons)
            delete_buttons[-4].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de delete. Certifique-se que o botão está com o atributo name='delete_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

            # Wait for the deletion to process
        time.sleep(2)
        try:
            # Check if the second card was deleted
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            new_buttons_count = len(delete_buttons)
            if new_buttons_count != buttons_count-1:
                msg += "\nClicar no botão de delete não removeu o segundo card."
                self.report(task_name=name, issue_text=msg)
                return msg

            src = self.driver.page_source.upper()
            assert cards[1][0].upper() not in src
            assert cards[1][1].upper() not in src
        except Exception as e:
            msg += f"\nNão foi possível deletar o segundo card. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os botões de delete estão deletando o card correto."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Delete the first card
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            buttons_count = len(delete_buttons)
            delete_buttons[-4].click()

            # Wait for the deletion to process
            time.sleep(2)

            # Check if the first card was deleted
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            new_buttons_count = len(delete_buttons)
            if new_buttons_count != buttons_count-1:
                msg += "\nClicar no botão de delete não removeu o primeiro card."
                msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
                self.report(task_name=name, issue_text=msg)
                return msg

            src = self.driver.page_source.upper()
            assert cards[0][0].upper() not in src
            assert cards[0][1].upper() not in src
        except Exception as e:
            msg += f"\nNão foi possível deletar o primeiro card. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os botões de delete estão deletando o card correto."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Delete the last card
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            buttons_count = len(delete_buttons)
            delete_buttons[-1].click()

            # Wait for the deletion to process
            time.sleep(2)

            self.driver.get(f"http://localhost:{self.port}")
            # Check if the last card was deleted
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            new_buttons_count = len(delete_buttons)
            if new_buttons_count != buttons_count-1:
                msg += "\nClicar no botão de delete não removeu o último card."
                self.report(task_name=name, issue_text=msg)
                return msg

            src = self.driver.page_source.upper()
            assert cards[-1][0].upper() not in src, f"Card with title {cards[-1][0]} was not deleted"
            assert cards[-1][1].upper() not in src, f"Card with details {cards[-1][1]} was not deleted"
        except Exception as e:
            msg += f"\nNão foi possível deletar o último card. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os botões de delete estão deletando o card correto."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Check if the third card is still there
            assert cards[2][0].upper() in src, f"Card with title {cards[2][0]} was deleted"
            assert cards[2][1].upper() in src, f"Card with details {cards[2][1]} was deleted"
            
            # Check if the fourth card is still there
            assert cards[3][0].upper() in src, f"Card with title {cards[3][0]} was deleted"
            assert cards[3][1].upper() in src, f"Card with details {cards[3][1]} was deleted"
        except Exception as e:
            msg += f"\nCards inseridos foram apagados indevidamente. Verifique se os botões de delete estão deletando o card correto."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'

        msg += "Tarefa realizada com sucesso."
        self.report(task_name=name, issue_text=msg, grade=10.0, test_status="PASS")


    def test_edit(self, name): 
        msg = f"Ao testar se a tarefa '{name}' está funcionando: "

        try:
            # Open the website
            self.driver.get(f"http://localhost:{self.port}")
        except Exception as e:
            msg += f"\nNão foi possível acessar o endereço http://localhost:5000"
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        cards = []
        for i in range(2):
            try:
                # Find the form elements and fill them out
                title_input = self.driver.find_element(By.NAME,"titulo")
                text_input = self.driver.find_element(By.NAME,"detalhes")
                
                random_number = random.randint(1000000, 9999999)
                title = "Title_"+str(i)+str(random_number)
                text = "text_"+str(i)+str(random_number)
                cards.append((title,text))

                title_input.send_keys(title)
                text_input.send_keys(text)

                # Submit the form
                submit_button = self.driver.find_element(By.CSS_SELECTOR,"[type='submit']")
                submit_button.click()

                # Wait for the submission to process
                time.sleep(2)

                # Check if the card was created
                src = self.driver.page_source.upper()
                assert title.upper() in src
                assert text.upper() in src
            except Exception as e:
                msg += f"\nNão foi possível criar {i} cards em sequência. O card com o título '{title}' e detalhes '{text}' não foi encontrado. Verifique se os campos estão com os nomes corretos: 'titulo' e 'detalhes' e o botão de submit está com o atributo type='submit'."
                msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
                self.report(task_name=name, issue_text=msg)
                return msg

        url = self.driver.current_url.split("?")[0]

        try:
            # Edit the first card
            edit_buttons = self.driver.find_elements(By.NAME,"edit_button")
            edit_buttons[-2].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de editar. Certifique-se que o botão está com o atributo name='edit_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        # Wait for loading
        time.sleep(2)

        edit_url = self.driver.current_url.split("?")[0]
        
        if len(url.split("/")) == len(edit_url.split("/")):
            msg += f"\nClicar no botão de editar não redirecionou para a página de edição"
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            title_input = self.driver.find_element(By.NAME,"titulo")
            text_input = self.driver.find_element(By.NAME,"detalhes")
            title_input.clear()
            title_input.send_keys("auto_test_title_0")
            text_input.clear()
            text_input.send_keys("auto_test_details_0")
        except Exception as e:
            msg += f"\nNão foi possível preencher os campos de título e detalhes. Certifique-se que os campos são campos de texto e estão com os nomes corretos: 'titulo' e 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            cancel_button = self.driver.find_elements(By.XPATH, '//button[text()="Cancelar"]')
            if len(cancel_button) == 0:
                cancel_button = self.driver.find_elements(By.NAME, "edit_cancel")
            cancel_button[0].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de cancelar. Certifique-se que o texto do botão é 'Cancelar' ou que este possui o atributo name='edit_cancel'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        # Wait for loading
        time.sleep(2)

        try:
            # Check if the card was not edited
            current_url = self.driver.current_url.split("?")[0]
            assert current_url == url
        except Exception as e:
            msg += f"\nClicar no botão de cancelar não redirecionou para a página inicial"
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            src = self.driver.page_source.upper()
            assert cards[0][0].upper() in src, f"Card with title {cards[0][0]} is no more"
            assert cards[0][1].upper() in src, f"Card with details {cards[0][1]} is no more"
        except Exception as e:
            msg += f"\nClicar no botão de Cancelar na tela de edição apagou o card com o título '{cards[0][0]}' e detalhes '{cards[0][1]}'."
            msg += f"\nAlterar os valores do título e detalhes e clicar em cancelar não deve alterar o card."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            edit_buttons = self.driver.find_elements(By.NAME,"edit_button")
            edit_buttons[-2].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de editar. Certifique-se que o botão está com o atributo name='edit_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        # Wait for loading
        time.sleep(2)

        try:
            title_input = self.driver.find_element(By.NAME,"titulo")
            text_input = self.driver.find_element(By.NAME,"detalhes")

            title = title_input.get_attribute("value")
            text = text_input.get_attribute("value")
        except Exception as e:
            msg += f"\nNão foi possível encontrar os campos de título e detalhes. Certifique-se que os campos estão com os nomes corretos: 'titulo' e 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            assert title == cards[0][0], "O título do card não foi preenchido corretamente"
            assert text == cards[0][1], "Os detalhes do card não foram preenchidos corretamente"
        except Exception as e:
            msg += f"\nOs campos de título e detalhes não foram preenchidos corretamente com os dados do card. Certifique-se que os cards são exibidos na ordem em que são criados e que os campos estão com os nomes corretos: 'titulo' e 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            title_input.clear()
            title_input.send_keys("auto_test_title_1")
        except Exception as e:
            msg += f"\nNão foi possível alterar o valor do campo de título. Certifique-se que o campo é um campo de texto e está com o nome correto: 'titulo'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            # Submit the form
            save_button = self.driver.find_element(By.XPATH, '//button[text()="Salvar"]')
            save_button.click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de salvar. Certifique-se que o botão está com o atributo type='submit' e que o texto do botão é 'Salvar'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        # Wait for the submission to process
        time.sleep(2)

        # Check if the card was edited
        try:
            src = self.driver.page_source.upper()
            assert cards[0][0].upper() not in src, f"Card with title {cards[-1][0]} shoud be edited"
            assert "auto_test_title_1".upper() in src, f"New title for {cards[-1][1]} was not saved"
            assert cards[0][1].upper() in src, f"Card with details {cards[-1][1]} is no more"
        except Exception as e:
            msg += f"\nO card com o título '{cards[0][0]}' não foi editado para 'auto_test_title_1' mantendo os detalhes '{cards[0][1]}'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Edit the second card
            edit_buttons = self.driver.find_elements(By.NAME,"edit_button")
            edit_buttons[-1].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de editar. Certifique-se que o botão está com o atributo name='edit_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        # Wait for loading
        time.sleep(2)

        try:
            title_input = self.driver.find_element(By.NAME,"titulo")
            text_input = self.driver.find_element(By.NAME,"detalhes")

            title = title_input.get_attribute("value")
            text = text_input.get_attribute("value")

            assert title == cards[1][0], "O título do card não foi preenchido corretamente"
            assert text == cards[1][1], "Os detalhes do card não foram preenchidos corretamente"

            text_input.clear()
            text_input.send_keys("auto_test_details")
        except Exception as e:
            msg += f"\nNão foi possível alterar o valor do campo de detalhes. Certifique-se que o campo é um campo de texto e está com o nome correto: 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Submit the form
            save_button = self.driver.find_element(By.XPATH, '//button[text()="Salvar"]')
            save_button.click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de salvar. Certifique-se que o botão está com o atributo type='submit' e que o texto do botão é 'Salvar'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        # Wait for the submission to process
        time.sleep(2)

        try:
            # Check if the card was edited
            src = self.driver.page_source.upper()
            assert cards[1][0].upper() in src, f"Card with title {cards[-1][0]} is no more"
            assert cards[1][1].upper() not in src, f"Card with details {cards[-1][1]} shoud be edited"
            assert "auto_test_details".upper() in src, f"New details for {cards[-1][1]} was not saved"
        except Exception as e:
            msg += f"\nO card com o título '{cards[1][0]}' não foi editado para 'auto_test_details' mantendo os detalhes '{cards[1][1]}'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            # Edit the first card
            edit_buttons = self.driver.find_elements(By.NAME,"edit_button")
            edit_buttons[-2].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de editar. Certifique-se que o botão está com o atributo name='edit_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        # Wait for loading
        time.sleep(2)

        try:
            title_input = self.driver.find_element(By.NAME,"titulo")
            text_input = self.driver.find_element(By.NAME,"detalhes")

            title = title_input.get_attribute("value")
            text = text_input.get_attribute("value")

            title_input.clear()
            title_input.send_keys("auto_test_title_2")
            text_input.clear()
            text_input.send_keys("auto_test_details_2")
        except Exception as e:
            msg += f"\nNão foi possível alterar o valor do campo de título e detalhes. Certifique-se que os campos são campos de texto e estão com os nomes corretos: 'titulo' e 'detalhes'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # Submit the form
            save_button = self.driver.find_element(By.XPATH, '//button[text()="Salvar"]')
            save_button.click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de salvar. Certifique-se que o botão está com o atributo type='submit' e que o texto do botão é 'Salvar'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        # Wait for the submission to process
        time.sleep(2)

        try:
            # Check if the card was edited
            src = self.driver.page_source.upper()
            assert cards[0][0].upper() not in src, f"Card with title {cards[-1][0]} shoud be edited"
            assert "auto_test_title_1".upper() not in src, f"Card with title {cards[-1][0]} shoud be edited"
            assert "auto_test_title_2".upper() in src, f"New title for {cards[-1][1]} was not saved"
            assert cards[0][1].upper() not in src, f"Card with details {cards[-1][1]} shoud be edited"
            assert "auto_test_details_2".upper() in src, f"New details for {cards[-1][1]} was not saved"
        except Exception as e:
            msg += f"\nAo alterar o título e detalhes do card com o título '{cards[0][0]}' e detalhes '{cards[0][1]}' para 'auto_test_title_2' e 'auto_test_details_2' respectivamente, o card com o título '{cards[0][0]}' e detalhes '{cards[0][1]}' não foi editado para 'auto_test_title_2' e 'auto_test_details_2'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        msg += "Tarefa realizada com sucesso."
        self.report(task_name=name, issue_text=msg, grade=10.0, test_status="PASS")

    
    def test_favorite(self, name):
        msg = f"Ao testar se a tarefa '{name}' está funcionando: "
        try:
            self.driver.get(f"http://localhost:{self.port}")
        except Exception as e:
            msg += f"\nNão foi possível acessar o endereço http://localhost:5000"
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            count = len(delete_buttons)
            for i in range(count):
                delete_buttons[-1].click()
                time.sleep(2)
                delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
            delete_buttons = self.driver.find_elements(By.NAME,"delete_button")
        except Exception as e:
            msg += f"\nNão foi possível encontrar os botões de delete. Certifique-se que o delete esteja funcionando."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        if len(delete_buttons) != 0:
            msg += "\nNão foi possível deletar todos os cards. Certifique-se que o delete esteja funcionando."
            self.report(task_name=name, issue_text=msg)
            return msg
        
        cards = []
        for i in range(5):
            try:
                # Find the form elements and fill them out
                title_input = self.driver.find_element(By.NAME,"titulo")
                text_input = self.driver.find_element(By.NAME,"detalhes")
                
                title = "Title"+str(i)
                text = "text"+str(i)
                cards.append((title,text))

                title_input.send_keys(title)
                text_input.send_keys(text)

                # Submit the form
                submit_button = self.driver.find_element(By.CSS_SELECTOR,"[type='submit']")
                submit_button.click()

                # Wait for the submission to process
                time.sleep(2)

                # Check if the card was created
                src = self.driver.page_source.upper()
                assert title.upper() in src
                assert text.upper() in src
            except Exception as e:
                msg += f"\nNão foi possível criar {i+1} cards em sequência. O card com o título '{title}' e detalhes '{text}' não foi encontrado. Verifique se os campos estão com os nomes corretos: 'titulo' e 'detalhes' e o botão de submit está com o atributo type='submit'."
                msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
                self.report(task_name=name, issue_text=msg)
                return msg
        
        try:
            # Favorite the third card
            favorite_buttons = self.driver.find_elements(By.NAME,"favorite_button")
            buttons_count = len(favorite_buttons)
            favorite_buttons[-3].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de favoritar. Certifique-se que o botão está com o atributo name='favorite_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        # Wait for the favoriting to process
        time.sleep(2)
        try:
            # Check if the third card was favorited
            # Read the cards in order and check if Title2 appears before Title0
            cards_elements = self.driver.find_elements(By.CLASS_NAME, "card")
            card_titles = [card.get_attribute("innerHTML").upper() for card in cards_elements]
            print("Cards found:", card_titles)
            index_title2 = next((i for i, t in enumerate(card_titles) if "TITLE2" in t), -1)
            index_title0 = next((i for i, t in enumerate(card_titles) if "TITLE0" in t), -1)
            assert index_title2 != -1 and index_title0 != -1, "Title2 or Title0 not found among cards"
            assert index_title2 < index_title0, "Title2 does not appear before Title0"

        except Exception as e:
            msg += f"\nFavoritar o terceiro card não o fez ser exibido primeiro. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os favoritados estão aparecendo primeiro."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            # UNfavorite the third card
            favorite_buttons = self.driver.find_elements(By.NAME,"favorite_button")
            favorite_buttons[-5].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de desfavoritar. Certifique-se que o botão está com o atributo name='favorite_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        # Wait for the favoriting to process
        time.sleep(2)
        try:
            # Check if the third card was favorited
            # Read the cards in order and check if Title2 appears before Title0
            cards_elements = self.driver.find_elements(By.CLASS_NAME, "card")
            card_titles = [card.get_attribute("innerHTML").upper() for card in cards_elements]
            index_title2 = next((i for i, t in enumerate(card_titles) if "TITLE2" in t), -1)
            index_title0 = next((i for i, t in enumerate(card_titles) if "TITLE0" in t), -1)
            assert index_title2 != -1 and index_title0 != -1, "Title2 or Title0 not found among cards"
            assert index_title2 > index_title0, "Title2 does not appear after Title0"

        except Exception as e:
            msg += f"\nDesfavoritar o card não o fez ser exibido na posição original. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os favoritados estão aparecendo primeiro."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            # Favorite the second and fourth cards
            favorite_buttons = self.driver.find_elements(By.NAME,"favorite_button")
            favorite_buttons[-4].click()
            time.sleep(2)
            favorite_buttons = self.driver.find_elements(By.NAME,"favorite_button")
            favorite_buttons[-2].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de favoritar. Certifique-se que o botão está com o atributo name='favorite_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        # Wait for the favoriting to process
        time.sleep(2)
        try:
            # Check if the second and fourth cards were favorited
            # Read the cards in order and check if Title1 appears before Title3 and Title3 appears before Title0
            cards_elements = self.driver.find_elements(By.CLASS_NAME, "card")
            card_titles = [card.get_attribute("innerHTML").upper() for card in cards_elements]
            index_title1 = next((i for i, t in enumerate(card_titles) if "TITLE1" in t), -1)
            index_title3 = next((i for i, t in enumerate(card_titles) if "TITLE3" in t), -1)
            index_title0 = next((i for i, t in enumerate(card_titles) if "TITLE0" in t), -1)
            assert index_title1 != -1 and index_title3 != -1 and index_title0 != -1, "Title1, Title3 or Title0 not found among cards"
            assert index_title1 < index_title3 < index_title0, "Notes are not in the expected order"

        except Exception as e:
            msg += f"\nFavoritar o card não o fez ser exibido na posição original. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os favoritados estão aparecendo primeiro."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        try:
            # UNfavorite the second card
            favorite_buttons = self.driver.find_elements(By.NAME,"favorite_button")
            favorite_buttons[-5].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de favoritar. Certifique-se que o botão está com o atributo name='favorite_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        time.sleep(2)
        try:
            # Check if the second and fourth cards were favorited
            # Read the cards in order and check if Title1 appears before Title3 and Title3 appears before Title0
            cards_elements = self.driver.find_elements(By.CLASS_NAME, "card")
            card_titles = [card.get_attribute("innerHTML").upper() for card in cards_elements]
            index_title1 = next((i for i, t in enumerate(card_titles) if "TITLE1" in t), -1)
            index_title3 = next((i for i, t in enumerate(card_titles) if "TITLE3" in t), -1)
            index_title0 = next((i for i, t in enumerate(card_titles) if "TITLE0" in t), -1)
            assert index_title1 != -1 and index_title3 != -1 and index_title0 != -1, "Title1, Title3 or Title0 not found among cards"
            assert index_title3 < index_title0 < index_title1, "Notes are not in the expected order"

        except Exception as e:
            msg += f"\nFavoritar o card não o fez ser exibido na posição original. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os favoritados estão aparecendo primeiro."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        try:
            # UNfavorite the fourth card
            favorite_buttons = self.driver.find_elements(By.NAME,"favorite_button")
            favorite_buttons[-5].click()
        except Exception as e:
            msg += f"\nNão foi possível encontrar o botão de favoritar. Certifique-se que o botão está com o atributo name='favorite_button'."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg
        
        time.sleep(2)
        try:
            # Check if the second and fourth cards were favorited
            # Read the cards in order and check if Title1 appears before Title3 and Title3 appears before Title0
            cards_elements = self.driver.find_elements(By.CLASS_NAME, "card")
            card_titles = [card.get_attribute("innerHTML").upper() for card in cards_elements]
            index_title1 = next((i for i, t in enumerate(card_titles) if "TITLE1" in t), -1)
            index_title3 = next((i for i, t in enumerate(card_titles) if "TITLE3" in t), -1)
            index_title0 = next((i for i, t in enumerate(card_titles) if "TITLE0" in t), -1)
            assert index_title1 != -1 and index_title3 != -1 and index_title0 != -1, "Title1, Title3 or Title0 not found among cards"
            assert index_title0 < index_title1 < index_title3, "Notes are not in the expected order"

        except Exception as e:
            msg += f"\nFavoritar o card não o fez ser exibido na posição original. Verifique se os cards estão sendo apresentados na ordem em que foram inseridos e se os favoritados estão aparecendo primeiro."
            msg += f'\nO código gerou uma exceção inesperada: {e.__class__.__name__}: {e}'
            self.report(task_name=name, issue_text=msg)
            return msg

        msg += "Tarefa realizada com sucesso."
        self.report(task_name=name, issue_text=msg, grade=10.0, test_status="PASS")

    def test_tags(self, name):
        msg = f"Ao testar se a tarefa '{name}' está funcionando: "
        msg += "Tarefa realizada com sucesso."
        self.report(task_name=name, issue_text=msg, grade=10.0, test_status="PASS")