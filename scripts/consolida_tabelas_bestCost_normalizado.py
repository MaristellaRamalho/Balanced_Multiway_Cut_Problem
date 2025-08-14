"""
  Esse script consolida os resultados das medias das seeds para valid_solution e best_cost (normalizado pelo melhor custo dentro de cada instancia, considerando todas as penalidades e todos os tempos de execução)

  ROOT_DATA_PATH
├── testes_6penalidades_3seeds_2025_06_29_1s
│   ├── coloracao3_2025_06_29_b2.0_eps0.0_zera
│   │   └── media_seeds_coloracao3_2025_06_29_b2.0_eps0.0_zera_1089661_1602347_1644410
│   ├── coloracao3_2025_06_29_b2.0_eps0.0_quadrange
│   │   └── media_seeds_coloracao3_2025_06_29_b2.0_eps0.0_quadrange_1089661_1602347_1644410
│   ├── ...
├── testes_6penalidades_3seeds_2025_06_29_2s
│   ├── coloracao3_2025_06_29_b2.0_eps0.0_zera
│   │   └── media_seeds_coloracao3_2025_06_29_b2.0_eps0.0_zera_1089661_1602347_1644410
│   ├── coloracao3_2025_06_29_b2.0_eps0.0_quadrange
│   │   └── media_seeds_coloracao3_2025_06_29_b2.0_eps0.0_quadrange_1089661_1602347_1644410
│   ├── ...
├── testes_6penalidades_3seeds_2025_06_29_ns
│   ├── coloracao3_2025_06_29_b2.0_eps0.0_zera
│   │   └── media_seeds_coloracao3_2025_06_29_b2.0_eps0.0_zera_1089661_1602347_1644410

A partir do diretorio raiz esse script varre todas as planilhas de média, para cada penalidade em cada tempo de execução e encontra o MELHOR CUSTO POR INSTANCIA.
Depois, gera uma única planilha (.xlsx) que contem uma ABA para cada tempo de execução. Em cada ABA temos as informações das instancias (Algoritmo, Instance,Nodes,Edges,Terminals,B,Epsilon) e os valores de best_cost e valid_solution para cada penalidade naquele tempo de execução. Os valores de best_cost são normalizados pelo melhor custo dentro de cada isntancia (uma instancia por linha)

Para gerar os graficos de custo x tempo -> subir a planilha no drive -> calcular, dentro cada ABA, para cada coluna de penalidade, a media do custo filtrada pelo numero de nós e o desvio padrao do custo filtrado pelo numero de nos -> ir para o script "plotar_grafico_custo_tempo_separados"
"""
import pandas as pd
from pathlib import Path

import pandas as pd
from pathlib import Path

# --- CONFIGURAÇÕES PRINCIPAIS ---
# Caminho para a pasta raiz
ROOT_DATA_PATH = Path("/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/raiz_refatoracao_13_08")

# Tipos de penalidade a serem procurados
PENALTY_TYPES = ['maxzera', 'maxrange', 'quadzera', 'quadrange', 'quadrangetotal', 'sem_penalidade']

# Colunas fixas que serão mantidas na tabela final
FIXED_COLUMNS = ['Algoritmo', 'Instance', 'Nodes', 'Edges', 'Terminals', 'B', 'Epsilon']

# LEITURA E AGREGAÇÃO DE TODOS OS DADOS 

all_dfs = []
# Itera sobre cada pasta de tempo de execução
for time_dir in ROOT_DATA_PATH.iterdir():
    if not time_dir.is_dir():
        continue

    # Extrai o tempo do nome da pasta
    try:
        max_time_str = time_dir.name.split('_')[-1]
    except IndexError:
        continue
    
    # Itera sobre cada subpasta de penalidade
    for penalty_dir in time_dir.iterdir():
        if not penalty_dir.is_dir():
            continue
        try:
            #print(f'dir : {penalty_dir.name}')

            penalty_name = penalty_dir.name.split('_')[-1]
            if penalty_name == "penalidade":
                penalty_name = "sem_penalidade"
            if penalty_name not in PENALTY_TYPES:
                continue
            
            results_file = next(penalty_dir.glob("media_seeds_*.csv"))
            df = pd.read_csv(results_file, sep=';', decimal=',')
            df['Max_Time'] = max_time_str
            df['Penalty'] = penalty_name
            #print(f'tipo_penalidade : {penalty_name}')
            all_dfs.append(df)
        except (StopIteration, Exception) as e:
            print(f"  - [AVISO] Falha ao processar a pasta '{penalty_dir.name}': {e}")

# Concatena todos os dados em um único DataFrame gigante
full_df = pd.concat(all_dfs, ignore_index=True)


# ENCONTRAR O MELHOR CUSTO PARA CADA INSTÂNCIA 

# Agrupa por instância e encontra o valor mínimo de 'Best cost'
best_costs_per_instance = full_df.groupby('Instance')['Best cost'].min().reset_index()
best_costs_per_instance = best_costs_per_instance.rename(columns={'Best cost': 'min_cost_for_instance'})



# GERAÇÃO DO FICHEIRO EXCEL COM ABAS E NORMALIZAÇÃO POR INSTÂNCIA 
unique_times = sorted(list(full_df['Max_Time'].unique()))
output_filename = "comparativo_bestCost_normalizado_validSolution_4s.xlsx"
output_path = ROOT_DATA_PATH / output_filename

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    # Itera sobre cada tempo de execução para criar uma aba
    for time_value in unique_times:
        print(f"\n--- Processando aba para o tempo: {time_value} ---")

        # Filtra os dados para o tempo atual
        time_df = full_df[full_df['Max_Time'] == time_value].copy()

        # Cria a tabela consolidada usando pivot_table para maior robustez
        pivot_df = time_df.pivot_table(
            index=FIXED_COLUMNS + ['Max_Time'],
            columns='Penalty',
            values=['Best cost', 'Valid Solution']
        )
        
        # Achata os nomes das colunas (ex: ('Best cost', 'zera') -> 'best_cost_zera')
        pivot_df.columns = [f"{val.lower().replace(' ', '_')}_{col}" for val, col in pivot_df.columns]
        consolidated_df = pivot_df.reset_index()

        # Junta os melhores custos conhecidos à tabela consolidada
        consolidated_df = pd.merge(consolidated_df, best_costs_per_instance, on='Instance', how='left')

        # Normaliza cada coluna de custo pelo melhor custo da sua instância
        cost_cols = [col for col in consolidated_df.columns if 'best_cost' in col]
        consolidated_df[cost_cols] = consolidated_df[cost_cols].div(consolidated_df['min_cost_for_instance'], axis=0)
        
        # Remove a coluna auxiliar de normalização
        consolidated_df = consolidated_df.drop(columns=['min_cost_for_instance'])
        
        # SALVANDO E FORMATANDO A ABA 
        sheet_name = f'comparativo_{time_value}'
        consolidated_df.to_excel(writer, sheet_name=sheet_name, index=False)

        workbook  = writer.book
        worksheet = writer.sheets[sheet_name]

        # Cria os formatos de célula
        format_arial = workbook.add_format({'font_name': 'Arial'})
        format_2_decimals = workbook.add_format({'num_format': '0.00', 'font_name': 'Arial'})
        format_6_decimals = workbook.add_format({'num_format': '0.000000', 'font_name': 'Arial'})

        # Aplica os formatos às colunas
        for idx, col_name in enumerate(consolidated_df.columns):
            width = 18 if 'best_cost' in col_name or 'valid_solution' in col_name else 15
            
            if 'best_cost' in col_name:
                cell_format = format_6_decimals
            elif 'valid_solution' in col_name:
                cell_format = format_2_decimals
            else:
                cell_format = format_arial
            
            worksheet.set_column(idx, idx, width, cell_format)
        

print(f"\n--- Processamento Finalizado! ---")
