from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
import smtplib
import mimetypes
import json

CONFIG_PATH = Path("config_smtp.json")
ASSINATURA_PATH = Path("assets/assinatura.jpg")
CID = "assinatura@vitor"


def carregar_config_smtp():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def processar_mensagem(modelo, nome_cliente, nome_processo, nome_documento):
    return (
        modelo.replace("[NOME_CLIENTE]", nome_cliente)
              .replace("[NOME_PROCESSO]", nome_processo)
              .replace("[NOME_DOCUMENTO]", nome_documento)
    )


def gerar_assinatura_html(cid):
    return f"""
    <p>Com os melhores cumprimentos.</p>
    <p style="font-size:9.5pt;font-family:Cantarell">
      <br>
      Vitor Manuel Ribeiro Silva<br>
      <span style="font-size:10pt;color:gray">
        (Gerente da Carpintaria Vitor Silva)
      </span>
    </p>
    <div>
      <hr style="border:1px solid #ccc; width:100%">
    </div>
    <p>
      <img src="cid:{cid}" width="260" height="130" style="width:260px;height:130px;"><br>
    </p>
    <p style="font-size:9.5pt;font-family:'Aptos', sans-serif; color:#833C0B;">
      R. Francisco Costa Matos nº80<br>
      4760-520 - Vila Nova de Famalicão<br>
      Braga, Portugal
    </p>
    """


def enviar_email(destinatario, assunto, mensagem_texto, caminho_pdf, nome_cliente, nome_processo):
    config = carregar_config_smtp()
    if not config:
        raise ValueError("Configuração SMTP não encontrada.")

    nome_documento = Path(caminho_pdf).name

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = formataddr((config["nome"], config["email"]))
    msg["To"] = destinatario
    msg["Bcc"] = config["email"]
    
    msg["Disposition-Notification-To"] = config["email"]
    msg["Return-Receipt-To"] = config["email"]

    # Processar corpo e assinatura
    corpo_processado = processar_mensagem(mensagem_texto, nome_cliente, nome_processo, nome_documento)
    corpo_html = corpo_processado.replace('\n', '<br>')
    assinatura_html = gerar_assinatura_html(CID)

    mensagem_html = (
        "<html><body>"
        f"<p>{corpo_html}</p>"
        f"{assinatura_html}"
        "</body></html>"
    )

    msg.set_content(corpo_processado)
    msg.add_alternative(mensagem_html, subtype="html")

    # Anexar documento PDF
    with open(caminho_pdf, "rb") as f:
        file_data = f.read()
        file_name = Path(caminho_pdf).name
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    # Adicionar imagem da assinatura embebida
    if ASSINATURA_PATH.exists():
        with open(ASSINATURA_PATH, "rb") as img:
            img_data = img.read()
            tipo = mimetypes.guess_type(ASSINATURA_PATH)[0]
            if tipo:
                maintype, subtype = tipo.split("/")
                msg.get_payload()[1].add_related(
                    img_data,
                    maintype=maintype,
                    subtype=subtype,
                    cid=f"<{CID}>"
                )

    # Envio do email
    porta = int(config["porta"])
    servidor = config["servidor"]
    email = config["email"]
    senha = config["senha"]
    seguranca = config.get("seguranca", "SSL").upper()

    if seguranca == "STARTTLS":
        with smtplib.SMTP(servidor, porta) as smtp:
            smtp.starttls()
            smtp.login(email, senha)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP_SSL(servidor, porta) as smtp:
            smtp.login(email, senha)
            smtp.send_message(msg)

    return True
