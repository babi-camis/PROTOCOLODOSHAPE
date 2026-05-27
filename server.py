from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Importações do Firebase Cloud Functions e Firestore
from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore

# Inicializa o ecossistema Firebase
initialize_app()
db_client = firestore.client()

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserData(BaseModel):
    name: str
    email: str
    age: int
    weight: float
    height: float
    gender: str
    objective: str

@app.post("/api/save-lead")
async def save_lead(data: UserData):
    try:
        # Grava o lead direto no Firestore de forma definitiva
        email_key = data.email.lower()
        doc_ref = db_client.collection("leads").document(email_key)
        doc_ref.set(data.dict())
        return {"status": "success", "message": "Dados do lead guardados com sucesso no banco Firebase."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco: {str(e)}")

@app.post("/api/infinitepay-webhook")
async def infinitepay_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Payload inválido.")
    
    status = payload.get("status") or payload.get("event")
    
    email_comprador = (
        payload.get("email") 
        or payload.get("customer", {}).get("email") 
        or payload.get("data", {}).get("customer", {}).get("email")
        or payload.get("metadata", {}).get("email")
    )

    if not email_comprador:
        return {"status": "ignored", "reason": "E-mail do comprador não localizado no payload."}

    email_comprador = email_comprador.lower()
    success_statuses = ["paid", "approved", "completed", "payment.approved", "confirmed"]

    if status in success_statuses:
        # Busca o lead guardado no Firestore
        doc_ref = db_client.collection("leads").document(email_comprador)
        doc_snap = doc_ref.get()
        
        if doc_snap.exists:
            user_info = doc_snap.to_dict()
            email_enviado = send_personalized_email(user_info)
            if email_enviado:
                return {"status": "dispatched"}
            else:
                raise HTTPException(status_code=500, detail="Falha no envio do e-mail de entrega.")
        else:
            return {"status": "ignored", "reason": "Lead não localizado no banco Firestore."}
            
    return {"status": "ignored", "reason": f"Estado de pagamento '{status}' não elegível para disparo."}

def send_personalized_email(user_info: dict) -> bool:
    sender_email = "seu-email@gmail.com"  # Altere para o seu e-mail real
    receiver_email = user_info['email']
    password = "fgjpteikolbcleyk" # Altere para sua senha de app real

    message = MIMEMultipart()
    message["From"] = f"Protocolo do Shape <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = f"🔥 O Seu Protocolo Personalizado Chegou, {user_info['name']}!"

    planilha_url = "https://link-da-planilha-padrao.com"
    gender = user_info['gender'].lower()
    objective = user_info['objective'].lower()

    if gender == 'masculino':
        if objective == 'hipertrofia':
            planilha_url = "https://seu-drive.com/planilha-massa-masculina.pdf"
        elif objective == 'emagrecimento':
            planilha_url = "https://seu-drive.com/planilha-cutting-masculino.pdf"
    elif gender == 'feminino':
        if objective == 'hipertrofia':
            planilha_url = "https://seu-drive.com/planilha-massa-feminina.pdf"
        elif objective == 'emagrecimento':
            planilha_url = "https://seu-drive.com/planilha-cutting-feminino.pdf"

    body = f"""Olá {user_info['name']},

O seu pagamento foi confirmado com sucesso pelo sistema da InfinitePay!

Analisámos a sua biometria e o seu objetivo ({user_info['objective']}) para libertar a sua planilha correta:
👉 Aceda ao seu protocolo personalizado aqui: {planilha_url}

Bons treinos, foco no objetivo!
"""
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Erro crítico no envio de e-mail para {receiver_email}: {e}")
        return False

# Expõe o FastAPI dentro do ambiente do Firebase Cloud Functions
@https_fn.on_request()
def api_server(req: https_fn.Request) -> https_fn.Response:
    return https_fn.as_asgi(app)(req)
