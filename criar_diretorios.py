# -------------------------------------------------------------------------------------
# Criar Diretorios
# Autor: Expert
# Criado: 03/03/2025


import os

# -------------------------------------------------------------------------------------
# Definições Globais
# -------------------------------------------------------------------------------------
debug = True

tabelas = ['atendimentos_documentos']
anos = range(2025, 2027)
meses = range(1, 13)
dias = range(1, 32)

for tabela in tabelas:
    caminho = f'./{tabela}'
    if not os.path.exists(caminho):
        if debug:
            print(caminho)
        else:
            os.mkdir(caminho)
    for ano in anos:
        caminho = f'./{tabela}/{ano}'
        if debug:
            print(caminho)
        else:
            os.mkdir(caminho)
        for mes in meses:
            caminho = f'./{tabela}/{ano}/{mes:02}'
            if debug:
                print(caminho)
            else:
                os.mkdir(caminho)
            for dia in dias:
                caminho = f'./{tabela}/{ano}/{mes:02}/{dia:02}'
                if debug:
                    print(caminho)
                else:
                    os.mkdir(caminho)
