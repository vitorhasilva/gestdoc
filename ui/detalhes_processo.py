import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import webbrowser
from pathlib import Path
from datetime import datetime
from core.email_handler import enviar_email
from core.utils import limpar_nome_ficheiro

DB_PATH = Path("gestor_processos.db")

ESTADOS_POSSIVEIS = {
    "Fatura": ["Recibo", "Cancelado"],
    "Recibo": ["Nota de Crédito"]
}

def obter_detalhes_processo(processo_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nome, p.estado, p.documento_path, c.nome, c.email, p.created_at, p.updated_at
        FROM processos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = ?
    """, (processo_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def atualizar_estado_processo(processo_id, novo_estado, novo_documento):
    agora = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE processos
        SET estado = ?, documento_path = ?, updated_at = ?
        WHERE id = ?
    """, (novo_estado, novo_documento, agora, processo_id))
    conn.commit()
    conn.close()

def janela_detalhes_processo(processo_id, atualizar_callback=None):
    dados = obter_detalhes_processo(processo_id)
    if not dados:
        messagebox.showerror("Erro", "Processo não encontrado.")
        return

    nome, estado, doc_path, nome_cliente, email_cliente, criado_em, atualizado_em = dados

    janela = tk.Toplevel()
    janela.title(f"Detalhes do Processo #{processo_id}")
    janela.geometry("500x400")
    janela.grab_set()

    def abrir_documento():
        if Path(doc_path).exists():
            webbrowser.open(doc_path)
        else:
            messagebox.showerror("Erro", "Documento não encontrado.")

    def reenviar_email():
        from core.modelos_email import obter_modelo_email
        modelo = obter_modelo_email(estado)
        if not modelo:
            messagebox.showerror("Erro", f"Modelo de email não encontrado para o estado '{estado}'.")
            return
        try:
            enviar_email(
                destinatario=email_cliente,
                assunto=f"Documento do processo: {nome}",
                mensagem_texto=modelo,
                caminho_pdf=doc_path,
                nome_cliente=nome_cliente,
                nome_processo=nome
            )
            messagebox.showinfo("Sucesso", "Email reenviado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro ao enviar email", str(e))

    def atualizar_estado_para(novo_estado):
        caminho = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not caminho:
            return
        nome_ficheiro = limpar_nome_ficheiro(f"{novo_estado} {nome} - {nome_cliente}.pdf")
        destino = Path("documentos") / nome_ficheiro
        destino.write_bytes(Path(caminho).read_bytes())

        atualizar_estado_processo(processo_id, novo_estado, str(destino))
        reenviar_email()
        messagebox.showinfo("Atualizado", f"Estado atualizado para {novo_estado}.")
        janela.destroy()
        if atualizar_callback:
            atualizar_callback()

    # Labels com info
    ttk.Label(janela, text=f"Processo: {nome}", font=("Arial", 12, "bold")).pack(pady=5)
    ttk.Label(janela, text=f"Cliente: {nome_cliente} ({email_cliente})").pack()
    ttk.Label(janela, text=f"Estado atual: {estado}").pack()
    ttk.Label(janela, text=f"Criado em: {datetime.fromisoformat(criado_em).strftime('%d/%m/%Y %H:%M')}").pack()
    if atualizado_em:
        ttk.Label(janela, text=f"Última atualização: {datetime.fromisoformat(atualizado_em).strftime('%d/%m/%Y %H:%M')}").pack()

    ttk.Button(janela, text="Abrir Documento", command=abrir_documento).pack(pady=10)
    ttk.Button(janela, text="Reenviar Email", command=reenviar_email).pack(pady=5)

    # Botões de estado possíveis
    if estado in ESTADOS_POSSIVEIS:
        frame_botoes = ttk.Frame(janela)
        frame_botoes.pack(pady=10)
        for novo_estado in ESTADOS_POSSIVEIS[estado]:
            ttk.Button(frame_botoes, text=f"Atualizar para {novo_estado}", command=lambda s=novo_estado: atualizar_estado_para(s)).pack(side="left", padx=5)

# Exemplo de uso:
# janela_detalhes_processo(3)
