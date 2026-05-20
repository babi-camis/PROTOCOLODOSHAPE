from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import uvicorn
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Configuração de CORS para permitir que o frontend comunique com o backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua pelo domínio do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento temporário em memória (substituir por base de dados em produção)
db_leads: Dict[str, dict] = {}

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
    # Registo dos dados do lead utilizando o e-mail como identificador único
    db_leads[data.email.lower()] = data.dict()
    return {"status": "success", "message": "Dados do lead guardados com sucesso."}

@app.post("/api/infinitepay-webhook")
async def infinitepay_webhook(request: Request):
    # Recebimento do payload enviado pela plataforma de pagamento InfinitePay
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Payload inválido.")
    
    # InfinitePay pode enviar o status no campo 'status' ou 'event'
    # E os dados do comprador sob chaves como 'customer', 'buyer' ou 'metadata'
    status = payload.get("status") or payload.get("event")
    
    # Tentativa de obter o e-mail em diferentes estruturas possíveis de payload da InfinitePay
    email_comprador = (
        payload.get("email") 
        or payload.get("customer", {}).get("email") 
        or payload.get("data", {}).get("customer", {}).get("email")
        or payload.get("metadata", {}).get("email")
    )

    if not email_comprador:
        return {"status": "ignored", "reason": "E-mail do comprador não localizado no payload."}

    email_comprador = email_comprador.lower()

    # Mapeamento de status de sucesso da InfinitePay (ex: "approved", "paid", "payment.approved")
    success_statuses = ["paid", "approved", "completed", "payment.approved", "confirmed"]

    if status in success_statuses:
        user_info = db_leads.get(email_comprador)
        
        if user_info:
            # Disparo do e-mail com a planilha personalizada associada à biometria
            email_enviado = send_personalized_email(user_info)
            if email_enviado:
                return {"status": "dispatched"}
            else:
                raise HTTPException(status_code=500, detail="Falha no envio do e-mail de entrega.")
        else:
            return {"status": "ignored", "reason": "Lead não localizado no banco de dados temporário."}
            
    return {"status": "ignored", "reason": f"Estado de pagamento '{status}' não elegível para disparo."}

def send_personalized_email(user_info: dict) -> bool:
    # Insira aqui o seu endereço de e-mail do Gmail associado à senha de aplicação
    sender_email = "seu-email@gmail.com" 
    receiver_email = user_info['email']
    
    # Senha de aplicação do Gmail configurada no Google Accounts
    password = "fgjpteikolbcleyk" 

    message = MIMEMultipart()
    message["From"] = f"Protocolo do Shape <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = f"🔥 O Seu Protocolo Personalizado Chegou, {user_info['name']}!"

    # Mapeamento do link da planilha com base nas respostas da calculadora
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

    # Corpo de texto do e-mail de entrega
    body = f"""Olá {user_info['name']},

O seu pagamento foi confirmado com sucesso pelo sistema da InfinitePay!

Analisámos a sua biometria e o seu objetivo ({user_info['objective']}) para libertar a sua planilha correta:
👉 Aceda ao seu protocolo personalizado aqui: {planilha_url}

Bons treinos, foco no objetivo!
"""
    
    message.attach(MIMEText(body, "plain"))

    try:
        # Conexão segura SMTP utilizando os servidores do Gmail na porta 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Erro crítico no envio de e-mail para {receiver_email}: {e}")
        return False

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
