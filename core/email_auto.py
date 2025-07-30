import sqlite3
from core.email_handler import enviar_email
from pathlib import Path

DB_PATH = Path("gestor_processos.db")

def obter_nome_cliente(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Cliente"

def obter_email_cliente(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM clientes WHERE id = ?", (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

def obter_modelo_email_por_estado(estado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT mensagem FROM modelos_email WHERE tipo = ?", (estado,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def enviar_email_processo_automatico(nome_processo, estado, cliente_id, documento_path):
    nome_cliente = obter_nome_cliente(cliente_id)
    email_destinatario = obter_email_cliente(cliente_id)
    modelo = obter_modelo_email_por_estado(estado)

    if not modelo:
        print(f"[Aviso] Modelo de email para o estado '{estado}' não encontrado.")
        return

    assunto = f"{estado} {nome_processo} | {nome_cliente}"

    try:
        enviar_email(
            destinatario=email_destinatario,
            assunto=assunto,
            mensagem_texto=modelo,
            caminho_pdf=documento_path,
            nome_cliente=nome_cliente,
            nome_processo=nome_processo
        )
    except Exception as e:
        print(f"[Erro] Falha ao enviar email: {e}")
