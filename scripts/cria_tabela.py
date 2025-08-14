'''
  Automatiza a criação de um arquivo csv
  a partir de arquivos de solução (.sol)

  Os arquivos .csv gerados usam '.' como separador decimal (apenas copiam os valores dos campos do .sol sem formatação ou arredondamento)

  A pasta raíz contém os dados de teste para um dado tempo de execução e cada subdiretorio contem os testes para cada combinação de {decoder}_{date}_{b}_{eps}_{tipo_penalidade}. É gerado um .csv para cada subdiretorio
  Depois de executar esse script -> ir para "cria_tabela_media_seeds.py"
'''
import os
from os.path import isfile, join

TESTE_PATH = "/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/testes_6penalidades_3seeds_2025_08_13_refatoracao_16s"
EXTENSION_FILE = ".sol"

def create_table():
    '''
        Cria um arquivo csv para cada pasta de teste
        contendo os dados de cada instância testada 

        .
        ├── testes_6penalidades_3seeds_2025_07_07_1024s
        │   ├── coloracao3_2025_07_07_b2.0_eps0.0_quadrangetotal
        │   │   ├── instance1
        │   │   ├── instance2
        │   │   ├── instancen
        |   |   ├── arquivo .csv gerado
        │   ├── coloracao3_2025_07_07_b2.0_eps0.0_quadzera
        │   │   ├── instance1
        │   │   ├── instance2
        │   │   ├── instancen
        |   |   ├── arquivo .csv gerado
    '''

    # Lista todos os diretórios de testes contidos no diretório <TESTE_PATH>
    testes_names = [
        d
        for d in os.listdir(TESTE_PATH)
        if os.path.isdir(join(TESTE_PATH, d))
    ]

    for teste_name in testes_names:

        alg, year, month, day, b, epsilon, tipo_penalidade = teste_name.split("_", 6)

        # Lista todos os arquivos presentes em /TESTE_PATH/test_name
        sol_files_names = [
            f
            for f in os.listdir(join(TESTE_PATH, teste_name))
            if isfile(join(TESTE_PATH, teste_name, f)) and EXTENSION_FILE in f
        ]

        # Ordena os arquivos em ordem crescente
        sol_files_names.sort()

        decoder_name = alg  # extrai o nome do algoritmo

        print(
            "--" + teste_name + "\n"
            "Algoritmo,Instance,Nodes,Edges,Terminals,Valid Solution,"
            "Best cost,Penalidade,maxV/balanceamentoPerfeito,Last update iteration,"
            "Last update time,Final iteration,Final time,B,Epsilon,Tipo penalidade,seed"
        )

        # Cria e abre o arquivo decoder_name.csv no diretório do teste
        data_file_name = join(TESTE_PATH, teste_name, f"{alg}_{b}_{epsilon}_{tipo_penalidade}.csv")
        data_file = open(data_file_name, "w", encoding="utf-8")

        # Grava a linha de cabeçalho no arquivo
        data_file.write(
            "Algoritmo,Instance,Nodes,Edges,Terminals,Valid Solution,"
            "Best cost,Penalidade,maxV/balanceamentoPerfeito,Last update iteration,"
            "Last update time,Final iteration,Final time,B, Epsilon, Tipo penalidade,seed\n"
        )

        for i in sol_files_names:

            # Remove extensão e separa os campos do nome
            basename = i[:-4]  # remove ".sol"
            parts = basename.split("_")
            seed = parts[-1]
            instance_name = "_".join(parts[:-1])

            path_sol_file_name = join(TESTE_PATH, teste_name, i)
            with open(path_sol_file_name, "r", encoding="utf-8") as file_solution:
                solucao = file_solution.readlines()

            # Cria dicionário com os campos do .sol
            campos = {}
            for line in solucao:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    campos[key.strip()] = value.strip()

            # Monta a linha de saída
            data = [
                alg,
                instance_name,
                campos.get("Nodes", ""),
                campos.get("Edges", ""),
                campos.get("Terminals", ""),
                campos.get("Valid Solution", ""),
                campos.get("Best cost", ""),
                campos.get("Penalidade", ""),  # mantém no mesmo formato do .sol
                campos.get("maxV/balanceamentoPerfeito", ""),
                campos.get("Last update iteration", ""),
                campos.get("Last update time", ""),
                campos.get("Final iteration", ""),
                campos.get("Final time", ""),
                campos.get("B", ""),
                campos.get("Epsilon", ""),
                campos.get("Tipo penalidade",""),
                seed,
            ]

            data_file.write(",".join(data) + "\n")
            print(",".join(data))

        print()
        data_file.close()

if __name__ == "__main__":
    create_table()
