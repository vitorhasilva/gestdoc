import re

def limpar_nome_ficheiro(nome):
    # Substitui todos os caracteres que não sejam letras, números, hífens ou underscores por "_"
    return re.sub(r'[\\/:"*?<>|]', "_", nome)
