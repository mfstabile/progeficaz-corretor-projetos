from fastapi import FastAPI, Request, Header, HTTPException
import hmac
import hashlib
import os

app = FastAPI()

GITHUB_SECRET = os.getenv("GITHUB_SECRET").encode("utf-8")

def verify_signature(payload: bytes, signature: str):
    if not signature:
        return False
    sha_name, received_sig = signature.split("=")
    if sha_name != "sha256":
        return False
    mac = hmac.new(GITHUB_SECRET, msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), received_sig)

@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=None)
):
    payload = await request.body()

    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Assinatura inválida")

    data = await request.json()

    if data.get("action") == "published":
        dono = data.get("repository", {}).get("owner", {}).get("login")
        repositorio = data.get("repository", {}).get("name")
        nome_release = data.get("release", {}).get("name")
        tag = data.get("release", {}).get("tag_name")

        print(f"📦 Repositório: {repositorio}")
        print(f"👑 Dono: {dono}")
        print(f"🏷️ Tag da release: {tag}")
        print(f"📄 Nome da release: {nome_release}")

    return {"status": "ok"}
