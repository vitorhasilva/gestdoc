import sqlite3
from pathlib import Path

# Caminho para a base de dados
DB_PATH = Path("gestor_processos.db")

# Conexão e cursor
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# Tabela de Clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL
)
""")

# Tabela de Processos
cursor.execute("""
CREATE TABLE IF NOT EXISTS processos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('Fatura', 'Recibo', 'Nota de Crédito', 'Fatura Cancelada')),
    documento_path TEXT,
    vencimento TEXT,
    cliente_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    fechado_em TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
)
""")

# Tabela de Modelos de Email
cursor.execute("""
CREATE TABLE IF NOT EXISTS modelos_email (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    mensagem TEXT NOT NULL
)
""")

# Tabela de Histórico de Processos
cursor.execute("""
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processo_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    estado TEXT NOT NULL,
    data TEXT NOT NULL,
    FOREIGN KEY(processo_id) REFERENCES processos(id) ON DELETE CASCADE
);
""")

# Inserir modelos predefinidos se ainda não existirem
cursor.execute("SELECT COUNT(*) FROM modelos_email")
if cursor.fetchone()[0] == 0:
    modelos_iniciais = [
        ("Fatura", "Estimado Cliente [NOME_CLIENTE],\n\nEm anexo encontra o documento, [NOME_DOCUMENTO]"),
        ("Recibo", "Estimado Cliente [NOME_CLIENTE],\n\nEm anexo encontra o documento, [NOME_DOCUMENTO]"),
        ("Nota de Crédito", "Estimado Cliente [NOME_CLIENTE],\n\nEm anexo encontra o documento, [NOME_DOCUMENTO]"),
        ("Fatura Cancelada", "Estimado Cliente [NOME_CLIENTE],\n\nEm anexo encontra o documento, [NOME_DOCUMENTO]")
    ]
    cursor.executemany("INSERT INTO modelos_email (tipo, mensagem) VALUES (?, ?)", modelos_iniciais)

# Confirmar alterações e fechar ligação
conn.commit()
conn.close()
