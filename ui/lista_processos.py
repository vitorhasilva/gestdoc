import tkinter as tk
from tkinter import ttk
import sqlite3
from pathlib import Path
from datetime import datetime
from ui.criar_processo import janela_criar_processo  
from ui.gerir_clientes import janela_gerir_clientes 
from core.modelos_email import janela_modelos_email 
from ui.configuracao_smtp import janela_configuracao_smtp
from ui.detalhes_processo import janela_detalhes_processo


DB_PATH = Path("gestor_processos.db")

def obter_processos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.nome, c.nome, p.estado, COALESCE(p.updated_at, p.created_at)
        FROM processos p
        JOIN clientes c ON p.cliente_id = c.id
    """)
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def criar_interface(root):
    root.title("Gestor de Processos")
    root.geometry("850x450")
    
    root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy()))

    titulo = ttk.Label(root, text="Lista de Processos", font=("Helvetica", 16))
    titulo.pack(pady=10)

    colunas = ("ID", "Nome do Processo", "Cliente", "Estado", "Última Atualização")
    tabela = ttk.Treeview(root, columns=colunas, show="headings")
    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=160)
    tabela.pack(expand=True, fill="both", padx=10, pady=10)

    def atualizar_tabela():
        for item in tabela.get_children():
            tabela.delete(item)
        for processo in obter_processos():
            data_iso = processo[4]
            data_formatada = datetime.fromisoformat(data_iso).strftime("%d/%m/%Y %H:%M")
            tabela.insert("", "end", values=(*processo[:4], data_formatada))

    atualizar_tabela()
    
    def abrir_detalhes(event):
        item_selecionado = tabela.selection()
        if item_selecionado:
            valores = tabela.item(item_selecionado, "values")
            id_processo = valores[0]  # ID é o primeiro campo
            janela_detalhes_processo(int(id_processo),atualizar_callback=atualizar_tabela)

    frame_botoes = ttk.Frame(root)
    frame_botoes.pack(pady=10)

    ttk.Button(frame_botoes, text="Criar Novo Processo", command=lambda: janela_criar_processo(atualizar_tabela)).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Gerir Clientes", command=lambda: janela_gerir_clientes()).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Modelos de Email", command=lambda: janela_modelos_email()).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Configuração de Email", command=lambda: janela_configuracao_smtp(root)).pack(side="left", padx=5)

    tabela.bind("<Double-1>", abrir_detalhes)
    # root.mainloop()



if __name__ == "__main__":
    criar_interface()
