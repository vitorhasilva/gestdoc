import tkinter as tk
from tkinter import ttk, messagebox
import json
import smtplib
from pathlib import Path

CONFIG_PATH = Path("config_smtp.json")

def guardar_config_smtp(dados):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

def carregar_config_smtp():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def janela_configuracao_smtp(master):
    janela = tk.Toplevel(master)
    janela.title("Configuração de Email (SMTP)")
    janela.geometry("340x250")
    janela.grab_set()

    config = carregar_config_smtp()

    campos = {
        "email": "Email Remetente",
        "nome": "Nome Remetente",
        "servidor": "Servidor SMTP",
        "porta": "Porta",
        "senha": "Palavra-passe da App"
    }

    entradas = {}

    for i, (chave, texto) in enumerate(campos.items()):
        ttk.Label(janela, text=texto + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
        ent = ttk.Entry(janela, width=30, show="*" if chave == "senha" else "")
        ent.grid(row=i, column=1, pady=5)
        ent.insert(0, config.get(chave, ""))
        entradas[chave] = ent

    # Campo de segurança
    ttk.Label(janela, text="Segurança:").grid(row=len(campos), column=0, sticky="e", padx=5, pady=5)
    seguranca_var = tk.StringVar()
    combo_seg = ttk.Combobox(janela, textvariable=seguranca_var, state="readonly", width=27)
    combo_seg["values"] = ["SSL", "STARTTLS"]
    combo_seg.grid(row=len(campos), column=1, pady=5)
    combo_seg.set(config.get("seguranca", "SSL"))

    def guardar():
        dados = {chave: ent.get().strip() for chave, ent in entradas.items()}
        dados["seguranca"] = seguranca_var.get()
        if not all(dados.values()):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return
        guardar_config_smtp(dados)
        messagebox.showinfo("Sucesso", "Configuração guardada com sucesso.")
        janela.destroy()

    def testar():
        dados = {chave: ent.get().strip() for chave, ent in entradas.items()}
        dados["seguranca"] = seguranca_var.get()
        try:
            if dados["seguranca"].upper() == "STARTTLS":
                with smtplib.SMTP(dados["servidor"], int(dados["porta"]), timeout=10) as smtp:
                    smtp.starttls()
                    smtp.login(dados["email"], dados["senha"])
            else:
                with smtplib.SMTP_SSL(dados["servidor"], int(dados["porta"]), timeout=10) as smtp:
                    smtp.login(dados["email"], dados["senha"])
            messagebox.showinfo("Teste de Envio", "Ligação SMTP bem-sucedida!")
        except Exception as e:
            messagebox.showerror("Erro no Teste", f"Erro ao testar envio:\n{e}")

    ttk.Button(janela, text="Guardar Configuração", command=guardar).grid(row=7, column=0, pady=20, padx=5)
    ttk.Button(janela, text="Testar Envio", command=testar).grid(row=7, column=1, pady=20, padx=5)
    
    return janela
