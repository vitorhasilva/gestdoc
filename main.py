import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from core import cr_database
from ui.configuracao_smtp import janela_configuracao_smtp
from ui.lista_processos import criar_interface

DB_PATH = Path("gestor_processos.db")
CONFIG_PATH = Path("config_smtp.json")

def verificar_estado(root):

    if not CONFIG_PATH.exists():
        resp = messagebox.askyesno("Configuração Necessária", "Nenhuma configuração de email encontrada.\nDeseja configurar agora?")
        if resp:
            janela = janela_configuracao_smtp(root)
            root.wait_window(janela)

            if not CONFIG_PATH.exists():
                messagebox.showwarning("Aviso", "A configuração de email não foi guardada. A aplicação será encerrada.")
                root.destroy()
                return
        else:
            messagebox.showwarning("Aviso", "A aplicação pode não funcionar corretamente sem configurar o envio de email.")

    criar_interface(root)  # Usa o root como UI principal

def main():
    root = tk.Tk()
    verificar_estado(root)
    root.mainloop()

if __name__ == "__main__":
    main()
