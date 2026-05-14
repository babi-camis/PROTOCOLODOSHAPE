from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Em produção, use um banco de dados real (SQLite, PostgreSQL, etc)
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
    # Salvamos os dados usando o e-mail como chave única
    db_leads[data.email.lower()] = data.dict()
    return {"status": "success", "message": "Dados salvos. Prossiga para o checkout."}

@app.post("/api/cakto-webhook")
async def cakto_webhook(request: Request):
    # A Cakto envia os dados da venda aqui
    payload = await request.json()
    
    # Verificamos se o pagamento foi aprovado (depende do payload da Cakto)
    status = payload.get("status") # Ex: "approved" ou "paid"
    email_comprador = payload.get("email").lower()

    if status == "paid" or status == "approved":
        # Buscamos a biometria salva anteriormente
        user_info = db_leads.get(email_comprador)
        
        if user_info:
            send_personalized_email(user_info)
            return {"status": "dispatched"}
            
    return {"status": "ignored"}

def send_personalized_email(user_info):
    sender_email = "seu-email@gmail.com"
    receiver_email = user_info['email']
    password = "SUA_SENHA_DE_APP_GMAIL" # Use 'Senhas de App' do Google

    message = MIMEMultipart()
    message["From"] = f"Protocolo do Shape <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = f"🔥 Seu Protocolo Personalizado chegou, {user_info['name']}!"

    # Lógica de seleção da planilha
    planilha_url = "https://link-da-planilha-padrao.com"
    if user_info['gender'] == 'masculino' and user_info['objective'] == 'hipertrofia':
        planilha_url = "https://seu-drive.com/planilha-massa-masculina.pdf"
    
    body = f"""
    Olá {user_info['name']}, seu pagamento foi confirmado!
    
    Com base no seu objetivo de {user_info['objective']}, preparamos seu material:
    Acesse seu protocolo aqui: {planilha_url}
    
    Bora buscar o shape!
    """
    
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"E-mail enviado para {receiver_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
