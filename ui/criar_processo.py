import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from core.email_auto import enviar_email_processo_automatico
import re

DB_PATH = Path("gestor_processos.db")
DOC_FOLDER = Path("docs")
DOC_FOLDER.mkdir(exist_ok=True)

def limpar_nome_ficheiro(nome):
    return re.sub(r'[\\/:"*?<>|]', "_", nome)

def obter_clientes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def guardar_processo(nome, estado, cliente_id, documento_origem, vencimento=None):
    agora = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (cliente_id,))
    resultado = cursor.fetchone()
    cliente_nome = resultado[0] if resultado else "ClienteDesconhecido"

    nome_limpo = limpar_nome_ficheiro(f"{estado} {nome} - {cliente_nome}")
    documento_nome = f"{nome_limpo}.pdf"
    documento_destino = DOC_FOLDER / documento_nome
    documento_destino.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy(documento_origem, documento_destino)

    cursor.execute("""
        INSERT INTO processos (nome, estado, documento_path, cliente_id, created_at, vencimento)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, estado, str(documento_destino), cliente_id, agora, vencimento))

    conn.commit()
    conn.close()
    return documento_destino

def janela_criar_processo(callback_atualizar=None):
    janela = tk.Toplevel()
    janela.title("Criar Novo Processo")
    janela.geometry("400x400")
    janela.grab_set()

    tk.Label(janela, text="Nome do Processo:").pack(pady=5)
    entry_nome = tk.Entry(janela, width=40)
    entry_nome.pack()

    tk.Label(janela, text="Estado Inicial:").pack(pady=5)
    estado_var = tk.StringVar()
    combo_estado = ttk.Combobox(janela, textvariable=estado_var, state="readonly")
    combo_estado["values"] = ["Fatura", "Recibo", "Nota de Crédito", "Fatura Cancelada"]
    combo_estado.pack()
    if combo_estado["values"]:
        estado_var.set(combo_estado["values"][0])

    label_venc = tk.Label(janela, text="Data de Vencimento (DD/MM/AAAA):")
    entry_venc = tk.Entry(janela, width=20)

    def mostrar_ou_ocultar_vencimento(event=None):
        if estado_var.get() == "Fatura":
            label_venc.pack(pady=5)
            entry_venc.pack()
        else:
            label_venc.pack_forget()
            entry_venc.pack_forget()

    combo_estado.bind("<<ComboboxSelected>>", mostrar_ou_ocultar_vencimento)
    mostrar_ou_ocultar_vencimento()

    tk.Label(janela, text="Cliente:").pack(pady=5)
    cliente_var = tk.StringVar()
    combo_clientes = ttk.Combobox(janela, textvariable=cliente_var, state="readonly")
    clientes = obter_clientes()
    valores_clientes = [f"{cid} - {nome}" for cid, nome in clientes]
    combo_clientes["values"] = valores_clientes
    combo_clientes.pack()
    if valores_clientes:
        cliente_var.set(valores_clientes[0])

    documento_path = tk.StringVar()
    def escolher_documento():
        caminho = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if caminho:
            documento_path.set(caminho)
            label_doc.config(text=f"Documento: {Path(caminho).name}")

    tk.Button(janela, text="Selecionar Documento", command=escolher_documento).pack(pady=10)
    label_doc = tk.Label(janela, text="Nenhum documento selecionado")
    label_doc.pack()

    def submeter():
        nome = entry_nome.get().strip()
        estado = estado_var.get().strip()
        cliente = cliente_var.get().strip()
        documento = documento_path.get()

        if not nome or not estado or not cliente or not documento:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return

        vencimento = None
        if estado == "Fatura":
            valor_venc = entry_venc.get().strip()
            if not valor_venc:
                messagebox.showerror("Erro", "A data de vencimento é obrigatória para Faturas.")
                return
            try:
                venc_dt = datetime.strptime(valor_venc, "%d/%m/%Y")
                vencimento = venc_dt.isoformat()
            except ValueError:
                messagebox.showerror("Erro", "Data de vencimento inválida. Use o formato DD/MM/AAAA.")
                return

        cliente_id = int(cliente.split(" - ")[0])
        caminho_documento = guardar_processo(nome, estado, cliente_id, documento, vencimento)

        try:
            enviar_email_processo_automatico(nome, estado, cliente_id, str(caminho_documento))
        except Exception as e:
            messagebox.showwarning(janela, "Aviso", f"Processo criado, mas o email não foi enviado:\n{e}")

        messagebox.showinfo("Sucesso", "Processo criado com sucesso.")
        if callback_atualizar:
            callback_atualizar()
        janela.destroy()

    tk.Button(janela, text="Criar Processo", command=submeter).pack(pady=20)

if __name__ == "__main__":
    janela_criar_processo()
