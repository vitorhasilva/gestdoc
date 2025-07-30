import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path

DB_PATH = Path("gestor_processos.db")

# Funções de base de dados para clientes
def obter_clientes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def adicionar_cliente(nome, email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, email) VALUES (?, ?)", (nome, email))
    conn.commit()
    conn.close()

def atualizar_cliente(cliente_id, nome, email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET nome = ?, email = ? WHERE id = ?", (nome, email, cliente_id))
    conn.commit()
    conn.close()

def eliminar_cliente(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()

# Interface de Gestão de Clientes
def janela_gerir_clientes():
    janela = tk.Tk()
    janela.title("Gestão de Clientes")
    janela.geometry("500x400")

    tabela = ttk.Treeview(janela, columns=("ID", "Nome", "Email"), show="headings")
    for col in ("ID", "Nome", "Email"):
        tabela.heading(col, text=col)
        tabela.column(col, width=150)
    tabela.pack(expand=True, fill="both", padx=10, pady=10)

    def atualizar_tabela():
        for item in tabela.get_children():
            tabela.delete(item)
        for cliente in obter_clientes():
            tabela.insert("", "end", values=cliente)

    def adicionar():
        nome = entry_nome.get().strip()
        email = entry_email.get().strip()
        if nome and email:
            adicionar_cliente(nome, email)
            atualizar_tabela()
            entry_nome.delete(0, tk.END)
            entry_email.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Nome e Email são obrigatórios.")

    def editar():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return
        cliente = tabela.item(item)["values"]
        cliente_id = cliente[0]
        nome = entry_nome.get().strip()
        email = entry_email.get().strip()
        if nome and email:
            atualizar_cliente(cliente_id, nome, email)
            atualizar_tabela()
        else:
            messagebox.showerror("Erro", "Nome e Email são obrigatórios.")

    def eliminar():
        item = tabela.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um cliente para eliminar.")
            return
        cliente = tabela.item(item)["values"]
        confirmar = messagebox.askyesno("Confirmar", f"Eliminar cliente '{cliente[1]}'?")
        if confirmar:
            eliminar_cliente(cliente[0])
            atualizar_tabela()

    def preencher_campos(event):
        item = tabela.selection()
        if item:
            cliente = tabela.item(item)["values"]
            entry_nome.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            entry_nome.insert(0, cliente[1])
            entry_email.insert(0, cliente[2])

    # Formulário
    frame_form = ttk.Frame(janela)
    frame_form.pack(pady=10)

    ttk.Label(frame_form, text="Nome:").grid(row=0, column=0, padx=5, sticky="e")
    entry_nome = ttk.Entry(frame_form, width=30)
    entry_nome.grid(row=0, column=1)

    ttk.Label(frame_form, text="Email:").grid(row=1, column=0, padx=5, sticky="e")
    entry_email = ttk.Entry(frame_form, width=30)
    entry_email.grid(row=1, column=1)

    # Botões
    frame_botoes = ttk.Frame(janela)
    frame_botoes.pack(pady=10)

    ttk.Button(frame_botoes, text="Adicionar", command=adicionar).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Atualizar", command=editar).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Eliminar", command=eliminar).pack(side="left", padx=5)

    tabela.bind("<<TreeviewSelect>>", preencher_campos)

    atualizar_tabela()
    # janela.mainloop()

# Para testar localmente:
# janela_gerir_clientes()

