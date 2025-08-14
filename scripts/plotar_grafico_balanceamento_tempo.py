import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

'''
        Gera um grafico (.pdf) do fator de balanceamento médio , ao longo do tempo, para cada penalidade e numero de nós da instancia (6 penalidades - 3 linhas por penalidade (160, 320 e 640 nós))

        usar essa estrutura de pastas:
        .
        ├── ROOT_DATA_PATH
        │   ├── dados_Bx
        │   │   ├── comparativo_balanceamento_Bx_1s.xlsx
        │   │   ├── comparativo_balanceamento_Bx_2s.xlsx
        │   │   ├── ...
        │   ├── dados_By
        │   │   ├── comparativo_balanceamento_By_1s.xlsx
        │   │   ├── comparativo_balanceamento_By_2s.xlsx
        │   │   ├── ...


'''


# --- CONFIGURAÇÕES GERAIS ---
# Pasta raiz com as subpastas que contêm as planilhas de comparação -> uma subpasta para cada valor de B
ROOT_DATA_PATH = "/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/dados_refatoracao_13_08"

# Valor(es) de 'B' para analisar.
B_VALUES_TO_ANALYZE = [2] 

# Exibir os gráficos na tela após gerar?
MOSTRAR_GRAFICOS = False

# Colunas usadas
COLUNA_IDENTIFICADORA = 'Algoritmo' #(coluna A - onde estão os rótulos das medias)
COLUNA_NOS = 'Nodes'
PREFIXO_COLUNA_PENALIDADE = 'balanceamento_'

# Mapeamento dos nomes das penalidades para a legenda do gráfico -> dependendo da data dos testes deve-se alterar o nome das penalidades (nomes refatorados em 28/07):
#zera -> maxzera
#range -> maxrange
#sem -> sem_penalidade
MAPEAMENTO_LEGENDA = {
    'maxzera': 'Maxzera',
    'maxrange': 'Maxrange',
    'quadzera': 'Quadzera',
    'quadrange': 'Quadrange',
    'quadrangetotal': 'Quadrangetotal',
    'sem_penalidade': 'Sem penalidade'
}
# --- FIM DAS CONFIGURAÇÕES ---

def processar_e_plotar_novo(base_path, b_val, show_plot=True):
    """
    Lê as médias pré-calculadas da planilha de balanceamento e gera um gráfico em PDF (exportável para Latex)
    """
    pasta_dados = os.path.join(base_path, f'dados_B{b_val}')
    print(f"--- Iniciando nova análise para B = {b_val} (lendo médias) ---")
    
    lista_de_medias_por_tempo = []

    if not os.path.isdir(pasta_dados):
        print(f"\nAVISO: A pasta '{pasta_dados}' não foi encontrada. Pulando.")
        return

    arquivos_excel = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.xlsx')])
    if not arquivos_excel:
        print(f"Nenhum arquivo .xlsx encontrado na pasta '{pasta_dados}'. Pulando.")
        return

    #print(f"Arquivos encontrados: {arquivos_excel}\n")

    for nome_arquivo in arquivos_excel:
        match = re.search(r'(\d+)s\.xlsx', nome_arquivo)
        if not match:
            print(f"AVISO: Não foi possível extrair tempo de '{nome_arquivo}'. Pulando.")
            continue
        
        tempo = int(match.group(1))
        caminho_completo_arquivo = os.path.join(pasta_dados, nome_arquivo)

        try:
            df = pd.read_excel(caminho_completo_arquivo, engine='openpyxl')
            
            # Definir os rótulos exatos das linhas de média
            labels_de_interesse = [
                'Média Bal (160 nós)', 
                'Média Bal (320 nós)', 
                'Média Bal (640 nós)'
            ]
            
            # Filtrar o DataFrame para conter apenas as linhas de média
            df_medias = df[df[COLUNA_IDENTIFICADORA].isin(labels_de_interesse)].copy()
            
            if df_medias.empty:
                print(f"AVISO: Nenhuma linha de média encontrada no arquivo '{nome_arquivo}'. Pulando.")
                continue

            # Extrair o número de nós do rótulo para criar a coluna 'Nodes'
            df_medias[COLUNA_NOS] = df_medias[COLUNA_IDENTIFICADORA].str.extract(r'(\d+)').astype(int)

            # Converter colunas de balanceamento para numérico
            colunas_penalidade = [col for col in df.columns if col.startswith(PREFIXO_COLUNA_PENALIDADE)]
            for col in colunas_penalidade:
                 df_medias[col] = pd.to_numeric(
                    df_medias[col].astype(str).str.replace(',', '.'), 
                    errors='coerce'
                )

            # Transformar os dados para o formato "longo"
            df_melted = df_medias.melt(
                id_vars=[COLUNA_NOS],
                value_vars=colunas_penalidade,
                var_name='Funcao_Penalidade',
                value_name='Balanceamento_Medio'
            )
            df_melted.dropna(subset=['Balanceamento_Medio'], inplace=True)
            df_melted['Tempo'] = tempo
            lista_de_medias_por_tempo.append(df_melted)

        except Exception as e:
            print(f"ERRO ao processar o arquivo '{nome_arquivo}': {e}")

    if not lista_de_medias_por_tempo:
        print("\nNenhum dado válido foi processado. O gráfico não será gerado.")
        return

    df_final = pd.concat(lista_de_medias_por_tempo, ignore_index=True)

    nomes_base = df_final['Funcao_Penalidade'].str.replace(PREFIXO_COLUNA_PENALIDADE, '')
    df_final['Funcao_Penalidade'] = nomes_base.map(MAPEAMENTO_LEGENDA).fillna(nomes_base.str.capitalize())
    
    # --- PLOTAGEM DO GRÁFICO ---
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(16, 10)) #(largura x altura em polegadas)

    sns.lineplot(
        data=df_final,
        x='Tempo', y='Balanceamento_Medio',
        hue='Funcao_Penalidade', #cada penalidade terá um cor unica
        style=COLUNA_NOS, #cada #nodes terá um estilo diferente
        markers=True,
        lw=1.8, ms=8, #tamanho dos marcadores
        ax=ax
    )

    ax.set_xscale('log') #escala log no eixo x
    ax.set_yscale('log') 
    #força os valores no eixo y a aparecerem no formato decimal
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(ScalarFormatter())


    ax.grid(which='both', linestyle='-', linewidth='0.5', alpha=0.5)
    ax.set_title(f'Balanceamento por Tamanho da Instância e Tempo (B = {b_val})', fontsize=20, pad=20)
    ax.set_xlabel('Tempo de Execução (segundos)', fontsize=16)
    ax.set_ylabel('Balanceamento Médio (Escala Log)', fontsize=16)

    #Ordenar legenda (sem_penalidade primeiro)
    handles, labels = ax.get_legend_handles_labels()

    # Dicionário para mapear cada texto ao seu item gráfico -> cada penalidade tem uma cor
    legend_dict = dict(zip(labels, handles))

    # Listas com a ordem dos itens da legenda
    ordem_penalidades = ['Sem penalidade', 'Maxzera', 'Maxrange', 'Quadzera', 'Quadrange', 'Quadrangetotal']
    ordem_nodes = ['160', '320', '640'] 

    # Montar as listas finais de handles e labels na ordem correta
    final_handles = []
    final_labels = []

    # Adicionar o título e os itens da Penalidade
    if 'Funcao_Penalidade' in legend_dict:
        final_labels.append('Funcao_Penalidade')
        final_handles.append(legend_dict['Funcao_Penalidade'])
        for label in ordem_penalidades:
            if label in legend_dict:
                final_labels.append(label)
                final_handles.append(legend_dict[label])

    # Adicionar o título e os itens dos Nós
    if 'Nodes' in legend_dict:
        final_labels.append('Nodes')
        final_handles.append(legend_dict['Nodes'])
        for label in ordem_nodes:
            if label in legend_dict:
                final_labels.append(label)
                final_handles.append(legend_dict[label])

    # Criar a legenda com os itens reordenados e aplicar estilo
    legend = ax.legend(handles=final_handles, labels=final_labels, loc='upper right')
    plt.setp(legend.get_texts(), fontsize='12')
    

    ax.tick_params(axis='x', labelsize=12) # Define o tamanho para o eixo X
    ax.tick_params(axis='y', labelsize=12) # Define o tamanho para o eixo Y


    #Mostrar apenas potencias de 2 no eixo x 

    # Pega todos os tempos únicos que existem nos dados
    all_times = sorted(df_final['Tempo'].unique())

    # Filtra a lista para manter apenas os números que são potência de 2 
    ticks_potencia_de_dois = [t for t in all_times if t > 0 and (t & (t - 1) == 0)]

    # Define os ticks do eixo x para serem apenas esses valores filtrados
    ax.set_xticks(ticks_potencia_de_dois)

    #Valores aparecem no formato decimal
    ax.xaxis.set_major_formatter(ScalarFormatter())


    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    nome_grafico = f'grafico_balanceamento_por_num_nos_e_tempo_B{b_val}_1024s_relatorio.pdf'
    caminho_salvar_grafico = os.path.join(base_path, nome_grafico)
    plt.savefig(caminho_salvar_grafico, bbox_inches='tight')
        
    if show_plot:
        plt.show()
    else:
        plt.close(fig)

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    print("--- INICIANDO ANÁLISE EM LOTE ---")
    if not os.path.isdir(ROOT_DATA_PATH):
        print(f"ERRO CRÍTICO: O caminho raiz '{ROOT_DATA_PATH}' não foi encontrado.")
    else:
        for b_valor in B_VALUES_TO_ANALYZE:
            processar_e_plotar_novo(ROOT_DATA_PATH, b_valor, show_plot=MOSTRAR_GRAFICOS)
            print("-" * 50)
    print("--- ANÁLISE EM LOTE CONCLUÍDA ---")