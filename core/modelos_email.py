import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path

DB_PATH = Path("gestor_processos.db")

# Funções base de dados para modelos de email
def obter_modelos_email():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo, mensagem FROM modelos_email")
    modelos = cursor.fetchall()
    conn.close()
    return modelos

def atualizar_modelo_email(modelo_id, nova_mensagem):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE modelos_email SET mensagem = ? WHERE id = ?", (nova_mensagem, modelo_id))
    conn.commit()
    conn.close()

def janela_modelos_email():
    janela = tk.Toplevel()
    janela.title("Modelos de Email")
    janela.geometry("600x400")
    janela.grab_set()

    modelos = obter_modelos_email()

    modelo_var = tk.StringVar()
    modelos_dict = {f"{tipo} (ID {mid})": (mid, msg) for mid, tipo, msg in modelos}
    modelo_nomes = list(modelos_dict.keys())

    tk.Label(janela, text="Selecionar Modelo:").pack(pady=5)
    combo = ttk.Combobox(janela, values=modelo_nomes, textvariable=modelo_var, state="readonly", width=50)
    combo.pack()

    caixa_texto = tk.Text(janela, wrap="word", height=15)
    caixa_texto.pack(padx=10, pady=10, expand=True, fill="both")

    def carregar_modelo(event=None):
        selecao = modelo_var.get()
        if selecao and selecao in modelos_dict:
            _, msg = modelos_dict[selecao]
            caixa_texto.delete("1.0", tk.END)
            caixa_texto.insert(tk.END, msg)

    def guardar_alteracoes():
        selecao = modelo_var.get()
        if not selecao or selecao not in modelos_dict:
            messagebox.showerror("Erro", "Selecione um modelo.")
            return
        modelo_id, _ = modelos_dict[selecao]
        nova_msg = caixa_texto.get("1.0", tk.END).strip()
        atualizar_modelo_email(modelo_id, nova_msg)
        messagebox.showinfo("Sucesso", "Modelo atualizado com sucesso.")

    combo.bind("<<ComboboxSelected>>", carregar_modelo)

    ttk.Button(janela, text="Guardar Alterações", command=guardar_alteracoes).pack(pady=10)

# Para testar localmente:
# janela_modelos_email()

