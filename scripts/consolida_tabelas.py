"""
  Esse script consolida os resultados das medias das seeds (para cada tempo de execução separadamente)
  A partir de um diretorio raiz (para um tempo de execução especifico), para cada valor de B, serão geradas 3 planilhas (.csv):
  1) compara os custos de cada instancia para cada penalidade . Best Cost é normalizado
     pelo menor custo da linha (melhor resultado para a instancia naquele tempo de execução) -> NÃO USAMOS POR ENQUANTO
  2) compara a validade das soluções -> coluna valid solution para cada penalidade. -> NÃO USAMOS POR ENQUANTO
  3) compara maxv/balanceamento perfeito -> USAMOS ESSA PLANILHA PARA GERAR OS GRAFICOS DE BALANCEAMENTO
  
  O script extrai o tempo máximo de execução do nome da pasta de testes,
  adiciona-o como uma coluna fixa e o inclui no nome dos arquivos de saída.

  Depois de gerar as 3 planilhas e subir no drive -> criar uma pasta com todas as planilhas de comparativo de balanceamento, para cada tempo de execução desejado (comparativo_balanceamento_B2_1s.csv, comparativo_balanceamento_B2_2s.csv, etc) -> Em cada planilha de balanceamento, calcular as médias do balanceamento, para cada coluna de penalidade, filtrada pelo numero de nós da instancia -> ir para o script "plotar_grafico_balanceamento_tempo" .

  Para ter graficos separados para cada numero de nós, plotando tambem o desvio padrão -> calcular nas planilhas de balanceamento tambem o desvio padrao para cada coluna de penalidade, filtrada pelo numero de nós da instancia -> ir para o script "plotar_grafico_balanceamento_tempo_separados"
"""
import pandas as pd
from pathlib import Path

def formatar_decimal(valor, casas):
    """
    Formata um número para uma string com N casas decimais e vírgula como separador
    """
    try:
        valor_arredondado = round(float(valor), casas)
        formato_str = f"{{:.{casas}f}}"
        string_com_ponto = formato_str.format(valor_arredondado)
        return string_com_ponto.replace('.', ',')
    except (ValueError, TypeError):
        return str(valor)

# Caminho para a pasta que contém as subpastas com os arquivos de média
TESTES_PATH = Path("/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/testes_6penalidades_3seeds_2025_08_13_refatoracao_16s")

# Extração do tempo de execução
try:
    # Pega o nome da pasta (ex: '..._6s') e extrai a última parte
    max_time_str = TESTES_PATH.name.split('_')[-1] 
    # Remove o 's' e converte para um número inteiro para usar na coluna
    max_time_num = int(max_time_str.replace('s', ''))
except (IndexError, ValueError):
    print("[ERRO] Não foi possível extrair o tempo numérico do nome da pasta. Verifique o formato do caminho em TESTES_PATH.")
    max_time_str = "TEMPO_DESCONHECIDO"
    max_time_num = 0

PENALTY_TYPES = ['maxzera', 'maxrange', 'quadzera', 'quadrange', 'quadrangetotal', 'sem_penalidade']
B_VALUES = [2.0]

# Colunas fixas que existem nos arquivos de média
BASE_FIXED_COLUMNS = [
    'Algoritmo', 'Instance', 'Nodes', 'Edges', 'Terminals', 'B', 'Epsilon'
]

# Colunas a serem analisadas para as planilhas de consolidação
TARGET_COLUMNS_MAP = {
    'best_cost': 'Best cost',
    'valid_solution': 'Valid Solution',
    'balanceamento': 'maxV/balanceamentoPerfeito'
}


for b_val in B_VALUES:
    print(f"--- Processando arquivos para B = {b_val} ---")
    
    data_per_penalty = {}

    # Carrega os dados de cada tipo de penalidade para o valor de B atual
    for penalty in PENALTY_TYPES:
        try:
            search_pattern = f"*b{b_val}*_{penalty}"
            subfolder = next(TESTES_PATH.glob(search_pattern))
            results_file = next(subfolder.glob("media_seeds_*.csv"))
            df = pd.read_csv(results_file, sep=';', decimal=',')
            data_per_penalty[penalty] = df
        except StopIteration:
            print(f"  [AVISO] Nenhum arquivo/pasta encontrado para B={b_val}, Penalidade='{penalty}'. Pulando.")
            continue
        except Exception as e:
            print(f"  [ERRO] Ocorreu um erro ao processar B={b_val}, Penalidade='{penalty}': {e}")
            continue
    
    if not data_per_penalty:
        print(f"Nenhum dado encontrado para B={b_val}. Pulando.")
        continue

    # Adiciona a coluna Max_Time -
    # Pega um DataFrame de base usando a lista de colunas fixas originais
    base_df = next(iter(data_per_penalty.values()))[BASE_FIXED_COLUMNS].copy()
    base_df = base_df.drop_duplicates(subset=['Instance'])
    base_df['Max_Time'] = max_time_num

    # Gera cada um dos 3 arquivos de comparação
    for target_name, source_column in TARGET_COLUMNS_MAP.items():
        
        comparison_df = base_df.copy()

        # Junta os dados de cada penalidade 
        for penalty, df in data_per_penalty.items():
            new_col_name = f"{target_name}_{penalty}"
            merge_data = df[['Instance', source_column]].rename(columns={source_column: new_col_name})
            comparison_df = pd.merge(comparison_df, merge_data, on='Instance', how='left')

        # Garante que as colunas de dados que acabaram de ser adicionadas são numéricas
        cols_to_process = [col for col in comparison_df.columns if target_name in col]
        for col in cols_to_process:
            comparison_df[col] = pd.to_numeric(comparison_df[col], errors='coerce')
        
        # Normalização para 'best_cost'
        if target_name == 'best_cost':
            cost_cols = [col for col in comparison_df.columns if 'best_cost' in col]
            if cost_cols:
                min_costs_per_row = comparison_df[cost_cols].min(axis=1)
                comparison_df[cost_cols] = comparison_df[cost_cols].div(min_costs_per_row + 1e-9, axis=0)

        # Formata as colunas de dados principais (as que são comparadas)
        if target_name == 'valid_solution':
            cols_to_format = [col for col in comparison_df.columns if target_name in col]
            for col in cols_to_format:
                comparison_df[col] = comparison_df[col].fillna(0).apply(formatar_decimal, casas=2)
        elif target_name == 'best_cost' or target_name == 'balanceamento':
            cols_to_format = [col for col in comparison_df.columns if target_name in col]
            for col in cols_to_format:
                comparison_df[col] = comparison_df[col].fillna(0).apply(formatar_decimal, casas=6)
        
        # Salva o arquivo final como CSV
        output_filename = TESTES_PATH / f"comparativo_{target_name}_B{int(b_val)}_{max_time_str}.csv"
        
        comparison_df.to_csv(output_filename, index=False, sep=';')

print("\n--- Processamento Concluído ---")
