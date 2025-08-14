import os
from datetime import datetime
from pathlib import Path
from glob import glob
from joblib import Parallel, delayed

"""
Dentro da pasta raiz (um tempo de execução fixado) cria um subdiretorio para cada combinação dos parâmetros {decoder}_{date}_
{b}_{eps}_{tipo_penalidade}

Depois de executar os tests -> ir para "verificador.py"
"""

#---------------------[Parâmetros para alteração]---------------------------------
# DECODERS ["coloracao3"]
# PENALIDADES  ["maxzera", "maxrange", "quadzera", "quadrange", "quadrangetotal", "sem_penalidade"]
DECODERS = ["coloracao3"]
B = [2.0]
EPSILON = [0.0]
TIPO_PENALIDADE = ["maxzera", "maxrange", "quadzera", "quadrange", "quadrangetotal", "sem_penalidade"]
SEEDS = ["1602347", "1089661", "1644410"]

DEFAULT_PATH = Path("/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/")
#DEFAULT_PATH = Path("/home/aloc/BRKGA_BMCP/") #PC aloc via ssh
INSTANCES_PATH = DEFAULT_PATH / "10_instancias_teste_final" 
TESTES_PATH = DEFAULT_PATH / "testes_6penalidades_3seeds_2025_08_13_refatoracao_16s" #colocar tempo de execução na última parte
EXT_FILE = ".gr"

MAIN_FILE_PATH = DEFAULT_PATH / "src" / "main_mcp"  
CONFIG_FILE_PATH = DEFAULT_PATH / "src" / "config.conf"

MAX_RUN_TIME = "16"

#---------------------[Função de execução individual]---------------------------------
def run_test(decoder, instance, seed, b, eps, tipo_p, date):
    instance_name = Path(instance).stem
    folder_test = f"{decoder}_{date}_b{b}_eps{eps}_{tipo_p}"
    teste_dir = TESTES_PATH / folder_test
    teste_dir.mkdir(parents=True, exist_ok=True)

    out_file = teste_dir / f"{instance_name}_{seed}.sol"

    comando = f"{MAIN_FILE_PATH} {seed} {CONFIG_FILE_PATH} {MAX_RUN_TIME} {instance} {decoder} {b} {eps} {tipo_p} {out_file}"
    
    #print(f"[EXECUTANDO] {comando}")
    os.system(comando)

#---------------------[Execução em paralelo]---------------------------------
def execute_tests():
    date = datetime.now().strftime("%Y_%m_%d")
    instances = sorted(glob(str(INSTANCES_PATH / f"*{EXT_FILE}")))

    testes = []
    for decoder in DECODERS:
        for instance in instances:
            for seed in SEEDS:
                for b in B:
                    for eps in EPSILON:
                        for tipo_p in TIPO_PENALIDADE:
                            testes.append((decoder, instance, seed, b, eps, tipo_p, date))

    #print(f"Total de testes a executar: {len(testes)}")

    #n_jobs = 5 para pc do aloc, 7 no meu
    Parallel(n_jobs=5)(
        delayed(run_test)(decoder, instance, seed, b, eps, tipo_p, date)
        for decoder, instance, seed, b, eps, tipo_p, date in testes
    )

if __name__ == "__main__":
    execute_tests()
