'''
  Verifca os resultados obtidos 
  a partir de arquivos de solução

  A pasta raíz contem todos os arquivos .sol para um dado tempo de execução, separados em subdiretorios para cada combinação de {decoder}_{date}_{b}_{eps}_{tipo_penalidade}
  Depois de verificar os testes -> ir para "cria_tabela.py" para gerar planilhas com os dados dos .sol
'''

import os
from os.path import isfile, join
import math
import numpy as np

TESTE_PATH = "/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/testes_6penalidades_3seeds_2025_08_13_refatoracao_16s"
INSTANCIAS_PATH = "/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/10_instancias_teste_final"
EXTENSION_FILE_SOL = ".sol"
EXTENSION_FILE_INSTANCE = ".gr"

DEBUG = 0

#------------------------------------------------------------[PENALIDADES]---------------------------------------------------------------------------
def calc_penalidade_maxzera(components_size, B, epsilon, n, k, debug=False):
    maxV = max(components_size)
    b = B + epsilon

    balanceamentoPerfeito = math.ceil(n / k)
    maxNodeComponent = math.ceil(b * balanceamentoPerfeito)
    gd_max = n - (k - 1) - balanceamentoPerfeito

    gd = 0.0  # grau de desbalanceamento
    if maxV > maxNodeComponent:
        gd = maxV - balanceamentoPerfeito
        is_valid = 0
    else:  
        is_valid = 1

    penalidade = gd / gd_max 
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    if debug:
        print(f"MaxV: {maxV}")
        print(f"Max nos permitido em uma componente: {maxNodeComponent}")
        print(f"Balanceamento Perfeito: {balanceamentoPerfeito}")
        print(f"Grau de desbalanceamento: {gd}")
        print(f"Grau de desbalanceamento max: {gd_max}")
        print(f"Penalidade: {penalidade}")
        print(f"b = B + eps = {b}")

    return penalidade, is_valid, fator_maxV_balPerfeito


def calc_penalidade_maxrange(components_size, B, epsilon, n, k, debug=False):
    maxV = max(components_size)
    b = B + epsilon

    balanceamentoPerfeito = math.ceil(n / k)
    maxNodeComponent = math.ceil(b * balanceamentoPerfeito)
    gd_max = n - (k - 1) - balanceamentoPerfeito

    gd = 0.0  # grau de desbalanceamento
    if maxV > maxNodeComponent:
        gd = maxV - balanceamentoPerfeito
        is_valid = 0
    else:
         gd = (maxV - balanceamentoPerfeito) / b
         is_valid = 1

    penalidade = gd / gd_max 
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    if debug:
        print(f"MaxV: {maxV}")
        print(f"Max nos permitido em uma componente: {maxNodeComponent}")
        print(f"Balanceamento Perfeito: {balanceamentoPerfeito}")
        print(f"Grau de desbalanceamento: {gd}")
        print(f"Grau de desbalanceamento max: {gd_max}")
        print(f"Penalidade: {penalidade}")
        print(f"b = B + eps = {b}")

    return penalidade, is_valid, fator_maxV_balPerfeito

def calc_penalidade_quadzera(components_size, B, epsilon, n, k, debug=False):
    maxV = max(components_size)
    b = B + epsilon

    balanceamentoPerfeito = math.ceil(n / k)
    maxNodeComponent = math.ceil(b * balanceamentoPerfeito)

    gd_max = (n - (k - 1)) - balanceamentoPerfeito
    gd = 0.0
    is_valid = 1

    for i in range(k):
        if components_size[i] > maxNodeComponent:
            diferenca = components_size[i] - balanceamentoPerfeito
            gd += diferenca ** 2
            is_valid = 0

    penalidade = math.sqrt(gd) / gd_max 
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    if debug:
        print(f"MaxV: {maxV}")
        print(f"Max nos permitido em uma componente: {maxNodeComponent}")
        print(f"Balanceamento Perfeito: {balanceamentoPerfeito}")
        print(f"Grau de desbalanceamento: {gd}")
        print(f"Penalidade: {penalidade}")

    return penalidade, is_valid, fator_maxV_balPerfeito

def calc_penalidade_quadrange(components_size, B, epsilon, n, k, debug=False):
    maxV = max(components_size)
    b = B + epsilon

    balanceamentoPerfeito = math.ceil(n / k)
    maxNodeComponent = math.ceil(b * balanceamentoPerfeito)

    gd_max = (n - (k - 1)) - balanceamentoPerfeito
    gd = 0.0
    is_valid = 1

    for i in range(k):
        if components_size[i] > maxNodeComponent:
            diferenca = components_size[i] - balanceamentoPerfeito
            gd += diferenca ** 2
            is_valid = 0
        else:
            diferenca = max(0, components_size[i] - balanceamentoPerfeito)
            gd += (diferenca ** 2) / b

    penalidade = math.sqrt(gd) / gd_max 
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    if debug:
        print(f"MaxV: {maxV}")
        print(f"Max nos permitido em uma componente: {maxNodeComponent}")
        print(f"Balanceamento Perfeito: {balanceamentoPerfeito}")
        print(f"Grau de desbalanceamento: {gd}")
        print(f"Grau de desbalanceamento max: {gd_max}")
        print(f"Penalidade: {penalidade}")

    return penalidade, is_valid, fator_maxV_balPerfeito


def calc_penalidade_quadrangetotal(components_size, B, epsilon, n, k, debug=False):
    maxV = max(components_size)
    b = B + epsilon

    balanceamentoPerfeito = math.ceil(n / k)
    maxNodeComponent = math.ceil(b * balanceamentoPerfeito)

    gd_max = (n - (k - 1)) - balanceamentoPerfeito
    gd = 0.0
    is_valid = 1

    for i in range(k):
        if components_size[i] > maxNodeComponent:
            diferenca = components_size[i] - balanceamentoPerfeito
            gd += diferenca ** 2
            is_valid = 0
        else:
            diferenca = components_size[i] - balanceamentoPerfeito
            gd += (diferenca ** 2) / b

    penalidade = math.sqrt(gd) / gd_max 
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    if debug:
        print(f"MaxV: {maxV}")
        print(f"Max nos permitido em uma componente: {maxNodeComponent}")
        print(f"Balanceamento Perfeito: {balanceamentoPerfeito}")
        print(f"Grau de desbalanceamento: {gd}")
        print(f"Grau de desbalanceamento max: {gd_max}")
        print(f"Penalidade: {penalidade}")

    return penalidade, is_valid, fator_maxV_balPerfeito


def sem_penalidade(components_size, B, epsilon, n, k, debug=False):
    maxV = max(components_size)
    b = B + epsilon

    balanceamentoPerfeito = math.ceil(n / k)
    maxNodeComponent = math.ceil(b * balanceamentoPerfeito)

    gd_max = (n - (k - 1)) - balanceamentoPerfeito
    gd = 0.0
    is_valid = 1
    if maxV > maxNodeComponent:
        is_valid = 0

    # A penalidade é zero
    penalidade = 0.0
    
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    if debug:
        print(f"MaxV: {maxV}")
        print(f"Max nos permitido em uma componente: {maxNodeComponent}")
        print(f"Balanceamento Perfeito: {balanceamentoPerfeito}")
        print(f"Grau de desbalanceamento: {gd}")
        print(f"Grau de desbalanceamento max: {gd_max}")
        print(f"Penalidade: {penalidade}")

    return penalidade, is_valid, fator_maxV_balPerfeito


def verifica_instancias():
    # Lista todos os diretórios de testes contidos no diretório <TESTE_PATH>
    print("Pasta raiz:" + TESTE_PATH)

    testes_names = [
        d
        for d in os.listdir(TESTE_PATH)
        if os.path.isdir(join(TESTE_PATH, d))
    ]

    for teste_name in testes_names:

        # Lista todos os arquivos presentes em /TESTE_PATH/test_name
        sol_files_names = [
            f
            for f in os.listdir(join(TESTE_PATH, teste_name))
            if isfile(join(TESTE_PATH, teste_name, f)) and EXTENSION_FILE_SOL in f
        ]

        # Ordena os arquivos em ordem crescente
        sol_files_names.sort()

        print("Diretório:" + teste_name)

        qtd_instancias_corretas_dir_corrente = 0
        instancias_erradas = []
        for sol in sol_files_names:
            if DEBUG: 
                print(".sol: " + sol)
            path_sol_file_name = join(TESTE_PATH, teste_name, sol)

            #Lendo informações da solução (.sol)
            with open(path_sol_file_name, "r", encoding="utf-8") as file_solution:
                solucao = file_solution.readlines() 

            campos = {} # Cria dicionário para os campos do .sol
            componentes = {} #armazena as componentes formadas
            components_size = []
            nos = [] #armazena todos os nós lidos das componentes -> verificar se nenhum nó aparece em mais de uma parte

            for line in solucao:
                line = line.strip()

                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    #conversão para os tipos apropriados
                    try:
                        if "." in value:
                            campos[key] = float(value)
                        else:
                            campos[key] = int(value)
                    except ValueError:
                        campos[key] = value  # mantém como string se não for número

                elif "=" in line:
                    terminal, nodes_str = line.split("=", 1)
                    terminal = int(terminal.strip())

                    #armazena os nós na componente do terminal
                    nodes_str = nodes_str.strip().lstrip("{").rstrip("}")
                    nodes = [int(n) for n in nodes_str.split() if n.strip().isdigit()]
                    componentes[terminal] = nodes
                    components_size.append(len(nodes))

                    for n in nodes:
                        if n in nos:
                            print(f"{n} aparece em mais de uma componente")
                        nos.append(n) 
                            

            #Lendo informações da instância (.gr)
            nome_instancia_com_seed = sol.split(".", 1)[0] #N640_M8N_K80_2_1644410
            nome_instancia = nome_instancia_com_seed.rsplit("_", 1)[0] 
            nome_instancia += EXTENSION_FILE_INSTANCE #coloca .gr

            path_instance_file_name = join(INSTANCIAS_PATH, nome_instancia)
            with open(path_instance_file_name, "r", encoding="utf-8") as instance_file:
                instancia = instance_file.readlines()[1:]  #ignora primeira linha (DIMACS2)

            grafo = {}
            lista_terminais = []

            for line in instancia:
                line = line.strip()
                line = line.split(" ")

                if line[0] != "p" and line[0] != "e":
                    k = int(line[0])
                    lista_terminais = [int(t) for t in line[1:]]
                if line[0] == "p":
                    n = int(line[2])
                    num_edges = int(line[3])
                if line[0] == "e":
                    u = int(line[1])
                    v = int(line[2])
                    cost = float(line[3])
                    
                    #Adicona na lista de adjacencia (grafo não direcionado)
                    if u not in grafo:
                        grafo[u] = []
                    grafo[u].append((v, cost))

                    if v not in grafo: 
                        grafo[v] = []
                    grafo[v].append((u, cost)) 
                
            custo_corte = 0.0
            qtd_terminais_componente = 0
            for indice_terminal, componente in componentes.items():
                no_terminal = lista_terminais[indice_terminal] 
                
                #verificando se a componente possui o terminal esperado
                if no_terminal not in componente:
                    print(f"componente {componente} não possui o terminal esperado ({no_terminal})")
                    instancia_esta_correta = 0

                #calculando custo do corte
                for u in componente:
                    if DEBUG > 1:
                        print(f"lista de adj de {u} :{grafo[u]} ")
                    lista_adjacencia_u = grafo[u]
                    for v, custo in lista_adjacencia_u:
                        if v not in componente:
                            custo_corte += custo
                            
                    #verificando se cada parte tem exatamente um terminal
                    if u in lista_terminais:
                        qtd_terminais_componente += 1
                    
                if qtd_terminais_componente > 1:
                    print(f"componente {componente} possui mais de um terminal")
                    instancia_esta_correta = 0
                qtd_terminais_componente = 0

            
            custo_corte = custo_corte/2

            #VERIFICAR QUANDO LER A INSTANCIA SE CADA PARTE TEM EXATAMENTE UM TERMINAL (ok)*
            #VERIFICAR NUMERO DE ARESTAS  (ok)
            #Verificações para o .sol corrente
            B = campos["B"]
            epsilon = campos["Epsilon"]
            tipo_penalidade = campos["Tipo penalidade"]

            if tipo_penalidade == "maxzera":
                penalidade, is_valid, fator_maxV_balPerfeito = calc_penalidade_maxzera(components_size, B, epsilon, n, k)
            elif tipo_penalidade == "maxrange":
                penalidade, is_valid, fator_maxV_balPerfeito = calc_penalidade_maxrange(components_size, B, epsilon, n, k)
            elif tipo_penalidade == "quadzera":
                penalidade, is_valid, fator_maxV_balPerfeito = calc_penalidade_quadzera(components_size, B, epsilon, n, k)
            elif tipo_penalidade == "quadrange":
                penalidade, is_valid, fator_maxV_balPerfeito = calc_penalidade_quadrange(components_size, B, epsilon, n, k)
            elif tipo_penalidade == "quadrangetotal":
                penalidade, is_valid, fator_maxV_balPerfeito = calc_penalidade_quadrangetotal(components_size, B, epsilon, n, k)
            elif tipo_penalidade == "sem_penalidade":
                penalidade, is_valid, fator_maxV_balPerfeito = sem_penalidade(components_size, B, epsilon, n, k)

            instancia_esta_correta = 1

            if campos["Valid Solution"] != is_valid:
                print("Incosistência na validação")
                instancia_esta_correta = 0
            if not math.isclose(campos["Penalidade"], penalidade, abs_tol=1e-2):
                print("Penalidade incorreta")
                instancia_esta_correta = 0
            if  not math.isclose(campos["maxV/balanceamentoPerfeito"], fator_maxV_balPerfeito, abs_tol=1e-2):
                print("fração maxV/balanceamentoPerfeito incorreta")
                instancia_esta_correta = 0
            if len(nos) != n:
                print("algum(ns) nó duplicado ou ausente")
                instancia_esta_correta = 0
            if campos["Nodes"] != n:
                print("Número de nós reportado incorretamente")
                instancia_esta_correta = 0
            if campos["Terminals"] != k:
                print("Número de terminais reportado incorretamente")
                instancia_esta_correta = 0
            if campos["Edges"] != num_edges:
                print("Número de arestas reportado incorretamente")
                instancia_esta_correta = 0
            if campos["Best cost"] != custo_corte:
                print("Best cost incorreto")
                instancia_esta_correta = 0


            qtd_instancias_corretas_dir_corrente += instancia_esta_correta
            if not instancia_esta_correta:
                instancias_erradas.append(sol)


            if DEBUG > 1:
                print(f"Valid Solution .sol: {campos["Valid Solution"]} | Valid Solution verificador: {is_valid}")

                print(f"Penalidade .sol: {campos["Penalidade"]} | Penalidade verificador: {penalidade}")

                print(f"MaxV/balanceamentoPerfeito .sol: {campos["maxV/balanceamentoPerfeito"]} | maxV/balanceamentoPerfeito verificador: {fator_maxV_balPerfeito}")

                print(f"número de nós distintos: {len(nos)}")

            # Impressão dos campos e componentes 
            if DEBUG > 1:
                print("\n--- Campos armazenados ---")
                for key, value in campos.items():
                    print(f"{key}:{value}")

                print("\n--- Componentes armazenadas ---")
                for comp_id, nodes in componentes.items():
                    print(f"Componente {comp_id}: {nodes}")
                
                print("\n\n") 
            

        print(f"Total de instâncias verificadas no diretório corrente: {len(sol_files_names)}")
        print(f"Total de instâncias corretas no diretório corrente: {qtd_instancias_corretas_dir_corrente}")

        if len(instancias_erradas) > 0:
            print("Instâncias erradas  no diretório corrente: ")
            print(instancias_erradas)
        print("\n")



if __name__ == "__main__":
    verifica_instancias()
