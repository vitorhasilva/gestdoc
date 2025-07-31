import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import webbrowser
from pathlib import Path
from datetime import datetime
from core.email_handler import enviar_email
from core.utils import limpar_nome_ficheiro
from core.email_auto import obter_modelo_email_por_estado

DB_PATH = Path("gestor_processos.db")

ESTADOS_POSSIVEIS = {
    "Fatura": ["Recibo", "Cancelado"],
    "Recibo": ["Nota de Crédito"],
    "Nota de Crédito": [],
    "Cancelado": []
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

def atualizar_estado_processo(processo_id, novo_estado, novo_documento, novo_nome):
    agora = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, estado FROM processos WHERE id = ?", (processo_id,))
    nome_antigo, estado_antigo = cursor.fetchone()

    cursor.execute("""
        UPDATE processos
        SET estado = ?, documento_path = ?, nome = ?, updated_at = ?
        WHERE id = ?
    """, (novo_estado, novo_documento, novo_nome, agora, processo_id))

    cursor.execute("""
        INSERT INTO historico (processo_id, nome, estado, data)
        VALUES (?, ?, ?, ?)
    """, (processo_id, nome_antigo, estado_antigo, agora))

    conn.commit()
    conn.close()

def obter_historico_processo(processo_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT estado, nome, data FROM historico
        WHERE processo_id = ?
        ORDER BY data DESC
    """, (processo_id,))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def janela_detalhes_processo(processo_id, atualizar_callback=None):
    dados = obter_detalhes_processo(processo_id)
    if not dados:
        messagebox.showerror("Erro", "Processo não encontrado.")
        return

    nome, estado, doc_path, nome_cliente, email_cliente, criado_em, atualizado_em = dados

    janela = tk.Toplevel()
    janela.title(f"Detalhes de {estado} {nome} - {nome_cliente}")
    janela.geometry("500x400")
    janela.grab_set()

    def abrir_documento():
        if Path(doc_path).exists():
            webbrowser.open(doc_path)
        else:
            messagebox.showerror("Erro", "Documento não encontrado.")

    def reenviar_email():
        modelo = obter_modelo_email_por_estado(estado)
        if not modelo:
            messagebox.showerror("Erro", f"Modelo de email não encontrado para o estado '{estado}'.")
            return
        try:
            enviar_email(
                destinatario=email_cliente,
                assunto=f"{estado} {nome} | {nome_cliente}",
                mensagem_texto=modelo,
                caminho_pdf=doc_path,
                nome_cliente=nome_cliente,
                nome_processo=nome
            )
            messagebox.showinfo("Sucesso", "Email reenviado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro ao enviar email", str(e))

    def lembrar_cliente():
        modelo = obter_modelo_email_por_estado("Atraso")
        if not modelo:
            messagebox.showerror("Erro", "Modelo de email 'Atraso' não encontrado.")
            return
        try:
            enviar_email(
                destinatario=email_cliente,
                assunto=f"Lembrete: Fatura {nome} | {nome_cliente}",
                mensagem_texto=modelo,
                caminho_pdf=doc_path,
                nome_cliente=nome_cliente,
                nome_processo=nome
            )
            agora = datetime.now().isoformat()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historico (processo_id, nome, estado, data)
                VALUES (?, ?, ?, ?)
            """, (processo_id, nome, "Lembrete", agora))
            conn.commit()
            conn.close()
            messagebox.showinfo("Lembrete enviado", "O cliente foi notificado com sucesso.")
            if atualizar_callback:
                atualizar_callback()
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao enviar email", str(e))

    def atualizar_estado_para(novo_estado):
        novo_nome = tk.simpledialog.askstring(
            "Novo Nome", f"Introduz o novo nome para o processo ({novo_estado}):",
            initialvalue=f"{nome}"
        )
        if not novo_nome:
            return

        caminho = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not caminho:
            return
        nome_ficheiro = limpar_nome_ficheiro(f"{novo_estado} {novo_nome} - {nome_cliente}.pdf")
        try:
            antigo = Path(doc_path)
            if antigo.exists():
                antigo.unlink()
        except Exception as e:
            print(f"Erro ao apagar documento antigo: {e}")

        destino = Path("docs") / nome_ficheiro
        destino.write_bytes(Path(caminho).read_bytes())

        atualizar_estado_processo(processo_id, novo_estado, str(destino), novo_nome)
        modelo = obter_modelo_email_por_estado(novo_estado)
        if not modelo:
            messagebox.showerror("Erro", f"Modelo de email não encontrado para o estado '{novo_estado}'.")
            return
        try:
            enviar_email(
                destinatario=email_cliente,
                assunto=f"{novo_estado} {novo_nome} | {nome_cliente}",
                mensagem_texto=modelo,
                caminho_pdf=str(destino),
                nome_cliente=nome_cliente,
                nome_processo=novo_nome
            )
            messagebox.showinfo("Atualizado", f"Estado atualizado para {novo_estado} e email enviado.")
        except Exception as e:
            messagebox.showerror("Erro ao enviar email", str(e))

        janela.destroy()
        if atualizar_callback:
            atualizar_callback()

    ttk.Label(janela, text=f"{estado} {nome}", font=("Arial", 12, "bold")).pack(pady=5)
    ttk.Label(janela, text=f"Cliente: {nome_cliente} ({email_cliente})").pack()
    ttk.Label(janela, text=f"Estado atual: {estado}").pack()
    ttk.Label(janela, text=f"Criado em: {datetime.fromisoformat(criado_em).strftime('%d/%m/%Y %H:%M')}").pack()
    if atualizado_em:
        ttk.Label(janela, text=f"Última atualização: {datetime.fromisoformat(atualizado_em).strftime('%d/%m/%Y %H:%M')}").pack()

    ttk.Button(janela, text="Abrir Documento", command=abrir_documento).pack(pady=10)

    if estado == "Fatura":
        frame_acoes = ttk.Frame(janela)
        frame_acoes.pack(pady=5)
        ttk.Button(frame_acoes, text="Reenviar Email", command=reenviar_email).pack(side="left", padx=5)
        ttk.Button(frame_acoes, text="Lembrar Cliente", command=lembrar_cliente).pack(side="left", padx=5)
    else:
        ttk.Button(janela, text="Reenviar Email", command=reenviar_email).pack(pady=5)

    ttk.Label(janela, text="Histórico de alterações:", font=("Arial", 10, "bold")).pack(pady=(10, 2))
    historico_frame = ttk.Frame(janela)
    historico_frame.pack(fill="both", expand=True, padx=10)

    colunas = ("Estado", "Nome", "Data")
    tabela_historico = ttk.Treeview(historico_frame, columns=colunas, show="headings", height=5)
    for col in colunas:
        tabela_historico.heading(col, text=col)
        tabela_historico.column(col, width=200 if col == "Nome" else 150)
    tabela_historico.pack(fill="both", expand=True)

    for estado_antigo, nome_antigo, data in obter_historico_processo(processo_id):
        data_formatada = datetime.fromisoformat(data).strftime('%d/%m/%Y %H:%M')
        tabela_historico.insert("", "end", values=(estado_antigo, nome_antigo, data_formatada))

    if estado in ESTADOS_POSSIVEIS:
        frame_botoes = ttk.Frame(janela)
        frame_botoes.pack(pady=10)
        for novo_estado in ESTADOS_POSSIVEIS[estado]:
            ttk.Button(frame_botoes, text=f"Atualizar para {novo_estado}", command=lambda s=novo_estado: atualizar_estado_para(s)).pack(side="left", padx=5)
    else:
        ttk.Label(janela, text="").pack(pady=10)

# Exemplo de uso:
# janela_detalhes_processo(3)
