import random
import subprocess
import time
import requests
import os

class PortHelper:

    @staticmethod
    def get_free_port(start_port=None):
        if start_port is None:
            start_port = random.randint(9000, 15000)
        i = start_port
        while True:
            if subprocess.getstatusoutput(f"nc -zv localhost {i}")[0] != 0:
                return i
            i += 1

class DockerConnectionHelper():

    @staticmethod
    def wait_for_service(port, host='127.0.0.1', timeout=60):
        url = f"http://{host}:{port}"
        deadline = time.time() + timeout
        ok_in_a_row = 0
        backoff = 0.5
        expect_status=200
        expect_text='Get-it'

        with requests.Session() as s:
            while time.time() < deadline:
                try:
                    r = s.get(url, timeout=(2, 2), allow_redirects=False)
                    if r.status_code == expect_status:
                        if expect_text is None or (expect_text in r.text):
                            ok_in_a_row += 1
                            if ok_in_a_row >= 2:  # duas leituras válidas seguidas
                                print("Service is ready")
                                return
                        else:
                            ok_in_a_row = 0
                    else:
                        ok_in_a_row = 0
                except requests.RequestException:
                    ok_in_a_row = 0

                time.sleep(backoff)
                backoff = min(backoff * 1.5, 2.0)

        raise TimeoutError(f"Timed out waiting for service at {url}")
        # start_time = time.time()
        # while True:
        #     try:
        #         response = requests.get(url)
        #         if response.status_code == 200:
        #             print("Service is ready")
        #             break
        #     except requests.exceptions.RequestException:
        #         # Handle connection errors, like service not yet available
        #         pass
            
        #     current_time = time.time()
        #     if current_time - start_time >= timeout:
        #         raise TimeoutError(f"Timed out waiting for service at {url}")
        #     time.sleep(1)

class DockerProject1Runner():

    def allocate(self, git_username, repository_name):
        self.git_username = git_username
        self.repository_name = repository_name
        self.port = PortHelper.get_free_port()
        self.id = random.randint(1000000, 9999999)
        local_path = os.path.abspath(f"../repos/{git_username}/{repository_name}")
        # subprocess.run(["cp", "-a", f"../repos/{git_username}/{repository_name}/.", f"./repo_folder_{self.id}/"])
        # print("docker", "run", "-p", f"{self.port}:8080", "-d", "-v", f"./repo_folder_{self.id}:/usr/src/app/repo_folder","--name", f"container_{self.id}", "project1a")
        subprocess.run(["docker", "run", "-p", f"{self.port}:5000", "-d", "-v", f"{local_path}:/usr/src/app/repo_folder","--name", f"container_{git_username}_{self.id}", "project1"])
        DockerConnectionHelper.wait_for_service(self.port)

    def deallocate(self):
        print(f"Deallocating resources for {self.git_username}/{self.repository_name} on port {self.port}")
        subprocess.run(["docker", "stop", f"container_{self.git_username}_{self.id}"])
        subprocess.run(["docker", "rm", "-f", f"container_{self.git_username}_{self.id}"])
        # subprocess.run(["rm", "-rf", f"repo_folder_{self.id}"])
        subprocess.run(["sudo","rm", "-rf", f"../repos/{self.git_username}/{self.repository_name}"])