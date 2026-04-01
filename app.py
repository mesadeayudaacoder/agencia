from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Permitir que el Frontend (Vite) se comunique con Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Credenciales institucionales que me enviaste
GMAIL_USER = "mesadeayudaacoder@gmail.com"
GMAIL_APP_PASSWORD = "wogfnljqgxgqleuu"

@app.post("/finalizar-mantenimiento")
async def finalizar_mantenimiento(
    tecnico: str = Form(...),
    usuario: str = Form(...),
    equipo: str = Form(...),
    observaciones: str = Form(...)
):
    # 1. Generar el PDF en la carpeta 'reports'
    report_name = f"reports/mantenimiento_{usuario.replace(' ', '_')}.pdf"
    c = canvas.Canvas(report_name, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Agencia de Comercialización - Informe Técnico")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Técnico Asignado: {tecnico}")
    c.drawString(100, 700, f"Usuario Responsable: {usuario}")
    c.drawString(100, 680, f"Equipo: {equipo}")
    c.drawString(100, 650, "Observaciones:")
    c.drawString(100, 630, observaciones)
    c.save()

    # 2. Enviar Correo de Notificación
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER # Se envía a la mesa de ayuda
        msg['Subject'] = f"Nuevo Mantenimiento: {equipo} - {usuario}"
        
        body = f"Se ha registrado un mantenimiento para el usuario {usuario} realizado por {tecnico}."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return {"status": "success", "message": "Reporte generado y correo enviado."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)