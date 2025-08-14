'''
  Testes automatizados
    Executa o programa principal especificando o decoder e a instância do grafo.
  
  Inputs
    - Requer uma lista de decoders, uma lista de instâncias e a extensão dos
      arquivos de instâncias utilizados.
    - Você deve adicionar manualmente na variável 'method' os decoders que deseja
      rodar no lote de testes atual e na variável 'extension_file' a extensão dos
      arquivos de instância utilizados.
    - A lista de instâncias é criada automaticamente lendo da pasta 'instances'
      apenas os arquivos de extensão 'extension_file' e armazenando na variável
      'instances_names'.

  Outputs
    Cria na pasta 'testes' uma pasta (se não existir) para cada decoder e
    salva o resultado de cada teste realizado.
  
  Observações
    A convenção de nomenclatura de pasta dos testes usa o nome do decoder e a data
    do momento em que o teste é iniciado. Testar múltiplas vezes um decoder na
    data irá sobrescrever o resultado obtido anterior. 
'''

import os
from datetime import datetime
from pathlib import Path
from glob import glob


#---------------------[Parâmetros para alteração]---------------------------------

# DECODERS ["coloracao3"]
# PENALIDADES  ["maxzera", "maxrange", "quadzera", "quadrange", "quadrangetotal", "sem_penalidade"]
DECODERS =  ["coloracao3"]
B = [1.0, 2.0]
EPSILON = [0.0]
TIPO_PENALIDADE = ["maxzera", "maxrange", "quadzera", "quadrange", "quadrangetotal", "sem_penalidade"]
SEEDS = ["1602347", "1089661", "1644410"]

DEFAULT_PATH = Path("/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/")
INSTANCES_PATH = DEFAULT_PATH / "instancias_pequenas" 
TESTES_PATH = DEFAULT_PATH / "testes_instancias_pequenas"
EXT_FILE = ".gr"

MAIN_FILE_PATH = DEFAULT_PATH / "src" / "main_mcp"  
CONFIG_FILE_PATH = DEFAULT_PATH / "src" / "config.conf"

MAX_RUN_TIME = ""

#---------------------[Execução dos testes automatizados]---------------------------------

def execute_tests():
    '''
    ---
    '''
    date = datetime.now().strftime("%Y_%m_%d")

    instances = glob(str(INSTANCES_PATH / f"*{EXT_FILE}"))
    instances.sort()

    for decoder in DECODERS:
        # Executa programa para cada uma das instâncias
        for instance in instances:
            for seed in SEEDS:
                for b in B:
                    for eps in EPSILON: 
                        for tipo_p in TIPO_PENALIDADE:
                            folder_test = f"{decoder}_{date}_b{b}_eps{eps}_{tipo_p}"

                            teste_dir = TESTES_PATH / folder_test
                            if not teste_dir.exists():
                                print(f"Criando pasta {folder_test}")
                                teste_dir.mkdir(parents=True)

                            out_file = str(teste_dir / f"{Path(instance).stem}_{seed}") + ".sol"
                            script = f"{MAIN_FILE_PATH} {seed} {CONFIG_FILE_PATH} {MAX_RUN_TIME} $instance {decoder} {b} {eps} {tipo_p} $teste"
                            comando = script.replace("$instance", str(INSTANCES_PATH / instance))
                            comando = comando.replace("$teste", str(TESTES_PATH / folder_test / out_file))

                            print(f"Instance: {instance}")
                            print(f"Comando: {comando}")
                            os.system(comando)
                            print("\n")

        print("\n\n")
    print("\n\n\n")


if __name__ == "__main__":
    execute_tests()
