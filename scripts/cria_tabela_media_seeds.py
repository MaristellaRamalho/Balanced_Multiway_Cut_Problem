'''
  Calcula as médias a partir dos resultados de várias seeds,
  adiciona desvio padrão e formata os dados.
  best_cost , valid_solution : 2 casas decimais
  desvio padrao/media para best_cost e maxv/balanceamentoPerfeito: % com duas casas decimais
  Demais campos numéricos com 6 casas decimais

  Os arquivos csv gerados usam ',' como separador decimal 

    
Cria um arquivo csv para cada pasta de teste
contendo as medias das seeds para cada intancia. 

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
    

  Depois de executar esse script, ir para:
  1)"consolida_tabelas.py" para ter as planilhas que serão usadas para plotar os graficos de balanceamento
  2)"consolida_tabelas_bestCost_normalizado.py para ter as planilhas que serão usadas para plotar os graficos de custo
'''
import pandas as pd
from pathlib import Path

def formatar_decimal(valor, casas):
    """
    Formata um número para uma string com N casas decimais e vírgula como separador
    """
    try:
        valor_arredondado = round(float(valor), casas)
        # Cria a string de formato para garantir o número de casas
        formato_str = f"{{:.{casas}f}}"
        # Formata, garantindo que o resultado use '.' como decimal
        string_com_ponto = formato_str.format(valor_arredondado)
        # Substitui o ponto pela vírgula para o formato brasileiro
        return string_com_ponto.replace('.', ',')
    except (ValueError, TypeError):
        return str(valor)

TESTES_PATH = Path("/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/testes_6penalidades_3seeds_2025_08_13_refatoracao_16s")

STATIC_FIELDS = [
    "Algoritmo", "Instance", "Nodes", "Edges", "Terminals", "B", "Epsilon", "Tipo penalidade"
]
MEAN_FIELDS = [
    "Valid Solution", "Best cost", "Penalidade", "maxV/balanceamentoPerfeito",
    "Last update iteration", "Last update time", "Final iteration", "Final time"
]
ADDED_MEAN_FIELDS = [
    "Desvio Padrão Best_Cost", "Desvio Padrão/Media Best_Cost",
    "Desvio Padrão maxV/balanceamentoPerfeito", "Desvio Padrão/Media maxV/balanceamentoPerfeito"
]
NUM_SEEDS = 3

# Itera sobre todas as subpastas de testes
for subfolder in TESTES_PATH.iterdir():
    if not subfolder.is_dir():
        continue

    arquivos_csv = list(subfolder.glob("*.csv"))
    if not arquivos_csv:
        continue
    
    arquivo_csv = arquivos_csv[0]

    print(f"Processando pasta: {subfolder.name}")
    resultados_subpasta = []
    seeds_usadas = set()

    df = pd.read_csv(arquivo_csv)
    df.columns = df.columns.str.strip()

    for field in MEAN_FIELDS:
        df[field] = pd.to_numeric(df[field], errors='coerce')

    for i in range(0, len(df), NUM_SEEDS):
        grupo = df.iloc[i:i+NUM_SEEDS]
        if len(grupo) < NUM_SEEDS:
            continue
        
        seeds_usadas.update(grupo["seed"].astype(str).tolist())
        static_vals = grupo.iloc[0][STATIC_FIELDS].to_dict()
        
        medias = grupo[MEAN_FIELDS].mean().to_dict()
        dp_best_cost = grupo['Best cost'].std()
        dp_maxv_bal_perfeito = grupo['maxV/balanceamentoPerfeito'].std()
        
        mean_best_cost = medias.get('Best cost', 0)
        cv_best_cost = (dp_best_cost / mean_best_cost) if mean_best_cost != 0 else 0.0
        
        mean_maxv_bal_perfeito = medias.get('maxV/balanceamentoPerfeito', 0)
        cv_maxv_bal_perfeito = (dp_maxv_bal_perfeito / mean_maxv_bal_perfeito) if mean_maxv_bal_perfeito != 0 else 0.0

        linha_resultado = {**static_vals, **medias}
        linha_resultado[ADDED_MEAN_FIELDS[0]] = dp_best_cost
        linha_resultado[ADDED_MEAN_FIELDS[1]] = cv_best_cost
        linha_resultado[ADDED_MEAN_FIELDS[2]] = dp_maxv_bal_perfeito
        linha_resultado[ADDED_MEAN_FIELDS[3]] = cv_maxv_bal_perfeito
        resultados_subpasta.append(linha_resultado)

    if resultados_subpasta:
        df_sub = pd.DataFrame(resultados_subpasta)
        
        mean_fields_sem_extras = [f for f in MEAN_FIELDS if f not in ['Best cost', 'maxV/balanceamentoPerfeito']]
        final_columns_order = (
            STATIC_FIELDS +
            ['Best cost', 'Desvio Padrão Best_Cost', 'Desvio Padrão/Media Best_Cost'] +
            ['maxV/balanceamentoPerfeito', 'Desvio Padrão maxV/balanceamentoPerfeito', 'Desvio Padrão/Media maxV/balanceamentoPerfeito'] +
            mean_fields_sem_extras
        )
        final_columns_order_existentes = [col for col in final_columns_order if col in df_sub.columns]
        df_sub = df_sub[final_columns_order_existentes]
        

        # Formatação para 2 casas decimais
        cols_2_decimals = ['Valid Solution', 'Best cost']
        for col in cols_2_decimals:
            if col in df_sub.columns:
                df_sub[col] = df_sub[col].fillna(0).apply(formatar_decimal, casas=2)

        # Formatação para 6 casas decimais
        cols_6_decimals = [
            'Penalidade', 'maxV/balanceamentoPerfeito', 'Last update time', 'Final time',
            'Desvio Padrão Best_Cost', 'Desvio Padrão maxV/balanceamentoPerfeito',
            'Last update iteration', 'Final iteration'
        ]
        for col in cols_6_decimals:
            if col in df_sub.columns:
                df_sub[col] = df_sub[col].fillna(0).apply(formatar_decimal, casas=6)

        # Formatação para porcentagem com 2 casas decimais
        cols_percent = [
            'Desvio Padrão/Media Best_Cost', 'Desvio Padrão/Media maxV/balanceamentoPerfeito'
        ]
        for col in cols_percent:
            if col in df_sub.columns:
                # Multiplica por 100 e depois formata como um decimal de 2 casas
                df_sub[col] = (df_sub[col].fillna(0) * 100).apply(formatar_decimal, casas=2) + '%'

        seeds_nome = "_".join(sorted(seeds_usadas))
        output_path = subfolder / f"media_seeds_{subfolder.name}_{seeds_nome}.csv"

        df_sub.to_csv(output_path, sep=';', index=False)
        
print("\nProcessamento concluído.")
