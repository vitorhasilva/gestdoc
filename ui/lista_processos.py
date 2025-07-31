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
        SELECT p.id, p.nome, c.nome, p.estado, COALESCE(p.updated_at, p.created_at), p.vencimento
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

    colunas = ("ID", "Nome do Processo", "Cliente", "Estado", "Última Atualização", "Vencimento")
    tabela = ttk.Treeview(root, columns=colunas, show="headings")

    larguras = {
        "ID": [50, "w"],
        "Nome do Processo": [120, "center"],
        "Cliente": [200, "w"],
        "Estado": [100, "center"],
        "Última Atualização": [130, "center"],
        "Vencimento": [120, "center"],
    }

    for col in colunas:
        tabela.heading(col, text=col)
        tabela.column(col, width=larguras.get(col, [100, "w"])[0], anchor=larguras.get(col, [100, "w"])[1])
    tabela.pack(expand=True, fill="both", padx=10, pady=10)
    tabela.tag_configure("vencido", foreground="red")
    tabela.tag_configure("breve", foreground="orange")

    def atualizar_tabela():
        for item in tabela.get_children():
            tabela.delete(item)
        for processo in obter_processos():
            id_, nome_proc, nome_cli, estado, data_iso, vencimento = processo
            data_formatada = datetime.fromisoformat(data_iso).strftime("%d/%m/%Y %H:%M")
            venc_formatada = datetime.fromisoformat(vencimento).strftime("%d/%m/%Y") if vencimento else ""

            tag = ""
            if estado == "Fatura" and vencimento:
                try:
                    venc_data = datetime.fromisoformat(vencimento)
                    dias_restantes = (venc_data - datetime.now()).days
                    if dias_restantes < 0:
                        tag = "vencido"
                    elif dias_restantes <= 2:
                        tag = "breve"
                except Exception:
                    pass

            tabela.insert("", "end", values=(id_, nome_proc, nome_cli, estado, venc_formatada, data_formatada), tags=(tag,))



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
