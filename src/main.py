from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks, Response
import hmac
import hashlib
import os
from dotenv import load_dotenv
load_dotenv()
# svg
import svg_report as sr
import hashlib
import time
# tests
from fetch_release import *
from auto_test import *
import db.db_conn as db

app = FastAPI()

GITHUB_SECRET = os.environ.get("GITHUB_SECRET").encode("utf-8")

def verify_signature(payload: bytes, signature: str):
    if not signature:
        return False
    sha_name, received_sig = signature.split("=")
    if sha_name != "sha256":
        return False
    mac = hmac.new(GITHUB_SECRET, msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), received_sig)


def check_user_repo_exists(git_username, repository_name):
    if not db.get_user_exists(git_username):
        db.insert_user(git_username)
        
    if not db.get_repo_exists(git_username, repository_name):
        db.insert_repository(git_username, repository_name)


@app.post("/progeficaz/{project_name}")
async def github_webhook(
    request: Request,
    project_name: str,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(default=None),    
):
    payload = await request.body()

    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Assinatura inválida")

    data = await request.json()

    if data.get("action") == "published":
        git_username = data.get("repository", {}).get("owner", {}).get("login")
        repository_name = data.get("repository", {}).get("name")
        release = data.get("release", {}).get("name")

        print(f"📦 Repositório: {repository_name}")
        print(f"👑 Dono: {git_username}")
        print(f"📄 Nome da release: {release}")

        check_user_repo_exists(git_username, repository_name)
        try:          
            fetch_release(git_username=git_username, repository=repository_name, release=release)
        except Exception as e:
            print(f"Error cloning repository {git_username}/{repository_name}:" + str(e))
            return {"message": 'no repository access'}
        background_tasks.add_task(auto_test, git_username, repository_name, release, project_name)

        return {"message": "received"}

    return {"status": "ok"}

@app.get("/progeficaz/{project_name}/svg/{git_username}/{repository_name}")
async def root(project_name, git_username, repository_name):
    report = sr.RepoReport(git_username = git_username, repository_name = repository_name, project_name = project_name)
    svg = report.compile()
    resp = Response(content=svg, media_type="image/svg+xml")
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Pragma'] = 'no-cache'

    now = time.strftime("%Y %m %d %H %M")
    txt = '{} {} {}'.format(git_username, repository_name, now).encode('utf-8')
    etag = hashlib.sha1(txt).hexdigest()
    resp.headers['ETag'] = etag
    
    return resp

@app.post("/local/{project_name}/{git_username}/{repository_name}/{release}")
async def root(request: Request, project_name: str, git_username: str, repository_name: str, release: str, background_tasks: BackgroundTasks):
    print(f'running tests for {git_username}')
    check_user_repo_exists(git_username, repository_name)
    try:          
        fetch_release(git_username=git_username, repository=repository_name, release=release)
    except Exception as e:
        print(f"Error cloning repository {git_username}/{repository_name}:" + str(e))
        return {"message": 'no repository access'}
    background_tasks.add_task(auto_test, git_username, repository_name, release, project_name)

    return {"message": "received"}