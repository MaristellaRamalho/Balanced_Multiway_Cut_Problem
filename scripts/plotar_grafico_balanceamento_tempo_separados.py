import os
import re
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.ticker import ScalarFormatter
import seaborn as sns 

'''
    Gera:
    - um arquivo PDF contendo TRÊS gráficos de balanceamento x tempo 
    um para cada número de nós (160, 320, 640).
    - 3 arquivos .pdf separados com o grafico completo (um para cada número de nós)

    Cada gráfico mostra a evolução do Balanceamento Médio (com barras de erro 
    para o desvio padrão) em função do Tempo de Execução. As diferentes 
    linhas dentro de cada gráfico representam as funções de penalidade (6 linhas).

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
# Pasta raiz com as subpastas que contêm as planilhas de comparação
ROOT_DATA_PATH = "/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/dados_refatoracao_13_08"

# Valor(es) de 'B' para analisar.
B_VALUES_TO_ANALYZE = [2]

# Exibir os gráficos na tela após gerar (?)
MOSTRAR_GRAFICOS = False

# Colunas e prefixos usados na planilha
COLUNA_IDENTIFICADORA = 'Algoritmo'
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

def extrair_nos(texto):
    """Extrai o número de nós de uma string como 'Média Bal (160 nós)'."""
    match = re.search(r'\((\d+)\s*nós\)', texto)
    if match:
        return int(match.group(1))
    return None

# Usada para plotar o eixo y com valores decimais
def generate_log_ticks(ymin, ymax):
    """Gera uma lista de ticks para uma escala log (1,2,3..10,20,30..)."""
    ticks = []
    # Encontra a primeira potência de 10 abaixo do limite mínimo
    power = np.floor(np.log10(ymin))
    val = 10**power
    
    # Itera através das potências de 10
    while val <= ymax * 10: # Multiplica por 10 para garantir que todos os múltiplos sejam considerados
        # Adiciona os múltiplos (1, 2, 3, ... 9) para cada potência de 10
        for i in range(1, 10):
            tick = val * i
            if tick > ymax:
                break # Para se o tick exceder o limite máximo do gráfico
            if tick >= ymin and tick not in ticks:
                ticks.append(tick)
        val *= 10
    return ticks

def processar_e_plotar_graficos_com_devpad(base_path, b_val, show_plot=False):
    """
    Agrega dados, gera um PDF com 3 subplots e também exporta cada subplot
    como um PDF individual, garantindo consistência de cores.
    """
    pasta_dados = os.path.join(base_path, f'dados_B{b_val}')
    print(f"--- Iniciando análise para B = {b_val} ---")

    if not os.path.isdir(pasta_dados):
        print(f"AVISO: A pasta '{pasta_dados}' não foi encontrada. Pulando.")
        return
    arquivos_excel = sorted([f for f in os.listdir(pasta_dados) if f.endswith('.xlsx')])
    if not arquivos_excel:
        print(f"Nenhum arquivo .xlsx encontrado na pasta '{pasta_dados}'.")
        return
    lista_dados_completos = []
    for nome_arquivo in arquivos_excel:
        match = re.search(r'(\d+)s\.xlsx$', nome_arquivo)
        if not match: continue
        tempo = int(match.group(1))
        caminho_completo = os.path.join(pasta_dados, nome_arquivo)
        try:
            df = pd.read_excel(caminho_completo, engine='openpyxl')
            colunas_penalidade = [col for col in df.columns if str(col).startswith(PREFIXO_COLUNA_PENALIDADE)]
            df_medias = df[df[COLUNA_IDENTIFICADORA].str.contains('Média Bal', na=False)].copy()
            df_desvios = df[df[COLUNA_IDENTIFICADORA].str.contains('Desvio Padrão', na=False)].copy()
            if df_medias.empty or df_desvios.empty: continue
            df_medias['Nodes'] = df_medias[COLUNA_IDENTIFICADORA].apply(extrair_nos)
            df_desvios['Nodes'] = df_desvios[COLUNA_IDENTIFICADORA].apply(extrair_nos)
            for col in colunas_penalidade:
                df_medias[col] = pd.to_numeric(df_medias[col], errors='coerce')
                df_desvios[col] = pd.to_numeric(df_desvios[col], errors='coerce')
            df_medias_long = df_medias.melt(id_vars=['Nodes'], value_vars=colunas_penalidade, var_name='Funcao_Penalidade', value_name='Balanceamento_Medio')
            df_desvios_long = df_desvios.melt(id_vars=['Nodes'], value_vars=colunas_penalidade, var_name='Funcao_Penalidade', value_name='Desvio_Padrao')
            df_merged = pd.merge(df_medias_long, df_desvios_long, on=['Nodes', 'Funcao_Penalidade'])
            df_merged['Tempo'] = tempo
            lista_dados_completos.append(df_merged)
        except Exception as e:
            print(f"ERRO ao processar o arquivo '{nome_arquivo}': {e}")
    if not lista_dados_completos:
        print("\nNenhum dado válido foi agregado. O gráfico não será gerado.")
        return
    df_final = pd.concat(lista_dados_completos, ignore_index=True)
    df_final.dropna(inplace=True)
    nomes_base = df_final['Funcao_Penalidade'].str.replace(PREFIXO_COLUNA_PENALIDADE, '')
    df_final['Funcao_Penalidade'] = nomes_base.map(MAPEAMENTO_LEGENDA).fillna(nomes_base.str.capitalize())

  
    plt.style.use('seaborn-v0_8-whitegrid')
    nodes_a_plotar = sorted(df_final['Nodes'].unique())
    
    ordem_penalidades = ['Sem penalidade', 'Maxzera', 'Maxrange', 'Quadzera', 'Quadrange', 'Quadrangetotal']

    # Cria um mapa de cores fixo para garantir consistência
    color_map = {
    'Maxzera':        '#1e76b3',  # Azul 
    'Maxrange':       '#ff7e0d',  # Laranja 
    'Quadzera':       '#2b9f2b',  # Verde 
    'Quadrange':      '#da4243',  # Vermelho 
    'Quadrangetotal': '#9366bc',  # Roxo
    'Sem penalidade': '#8b564a'   # Marrom 
}

    # --- GRÁFICO COMBINADO (3 subplots) ---
    fig, axes = plt.subplots(
        nrows=len(nodes_a_plotar), ncols=1,
        figsize=(16, 8 * len(nodes_a_plotar)),
        sharex=True, sharey=False
    )
    if len(nodes_a_plotar) == 1:
        axes = [axes]

    for i, nodes in enumerate(nodes_a_plotar):
        ax_combined = axes[i]
        df_subplot = df_final[df_final['Nodes'] == nodes]
        
        #Grafico individual
        fig_ind, ax_ind = plt.subplots(figsize=(14, 9))
        
        for penalidade in ordem_penalidades:
            df_line = df_subplot[df_subplot['Funcao_Penalidade'] == penalidade].sort_values('Tempo')
            if not df_line.empty:
                # Buscar a cor específica do mapa de cores
                cor_especifica = color_map.get(penalidade)

                # Plota no gráfico combinado usando a cor fixa
                ax_combined.errorbar(
                    x=df_line['Tempo'], y=df_line['Balanceamento_Medio'],
                    yerr=df_line['Desvio_Padrao'], label=penalidade,
                    fmt='-o', ms=6, capsize=4, color=cor_especifica
                )
                # Plota no gráfico individual usando a MESMA cor fixa
                ax_ind.errorbar(
                    x=df_line['Tempo'], y=df_line['Balanceamento_Medio'],
                    yerr=df_line['Desvio_Padrao'], label=penalidade,
                    fmt='-o', ms=6, capsize=4, color=cor_especifica
                )

        # --- Customização do gráfico COMBINADO  ---
        ax_combined.set_xscale('log')
        ax_combined.set_yscale('log')
        ymin_c, ymax_c = ax_combined.get_ylim()
        y_ticks_c = generate_log_ticks(ymin_c, ymax_c)
        ax_combined.set_yticks(y_ticks_c)
        ax_combined.yaxis.set_major_formatter(ScalarFormatter())
        ax_combined.set_ylim(ymin_c, ymax_c)
        all_times = sorted(df_final['Tempo'].unique())
        ticks_potencia_de_dois = [t for t in all_times if t > 0 and (t & (t - 1) == 0)]
        ax_combined.set_xticks(ticks_potencia_de_dois)
        ax_combined.xaxis.set_major_formatter(ScalarFormatter())
        ax_combined.grid(which='both', linestyle='-', linewidth='0.5', alpha=0.5)
        ax_combined.set_title(f'Evolução do Balanceamento para Instâncias com {nodes} Nós', fontsize=18, pad=15)
        ax_combined.set_ylabel('Balanceamento Médio (Escala Log)', fontsize=14)
        ax_combined.tick_params(axis='both', labelsize=12)

        # --- Customização do gráfico INDIVIDUAL (um para cada numero de nos)---
        ax_ind.set_xscale('log')
        ax_ind.set_yscale('log')
        ymin_i, ymax_i = ax_ind.get_ylim()
        y_ticks_i = generate_log_ticks(ymin_i, ymax_i)
        ax_ind.set_yticks(y_ticks_i)
        ax_ind.yaxis.set_major_formatter(ScalarFormatter())
        ax_ind.set_ylim(ymin_i, ymax_i)
        ax_ind.set_xticks(ticks_potencia_de_dois)
        ax_ind.xaxis.set_major_formatter(ScalarFormatter())
        ax_ind.grid(which='both', linestyle='-', linewidth='0.5', alpha=0.5)
        ax_ind.set_title(f'Evolução do Balanceamento para Instâncias com {nodes} Nós (B={b_val})', fontsize=18, pad=15)
        ax_ind.set_ylabel('Balanceamento Médio (Escala Log)', fontsize=14)
        ax_ind.set_xlabel('Tempo de Execução (segundos)', fontsize=14, labelpad=15)
        ax_ind.tick_params(axis='both', labelsize=12)
        
        loc_map = {160: 'upper right', 320: 'upper right', 640: 'lower left'}
        legend_loc = loc_map.get(nodes, 'best')
        ax_ind.legend(loc=legend_loc, title='Função Penalidade', fontsize=12, title_fontsize=14)
        
        fig_ind.tight_layout()
        nome_grafico_ind = f'grafico_balanceamento_{nodes}_nos_B{b_val}_1024s.pdf'
        caminho_salvar_ind = os.path.join(base_path, nome_grafico_ind)
        fig_ind.savefig(caminho_salvar_ind, bbox_inches='tight')
        if show_plot:
            plt.show()
        plt.close(fig_ind)

    axes[-1].set_xlabel('Tempo de Execução (segundos)', fontsize=16, labelpad=15)
    
    handles, labels = axes[0].get_legend_handles_labels()

    fig.legend(
        handles=handles, labels=labels, title='Função Penalidade',
        bbox_to_anchor=(1.01, 0.5), loc='center left', fontsize=12, title_fontsize=14
    )
    fig.suptitle(f'Balanceamento por Tamanho da Instância e Tempo (B = {b_val})', fontsize=22, y=1.0)
    plt.tight_layout(rect=[0, 0, 0.90, 0.98])
    
    nome_grafico_comb = f'grafico_balanceamento_por_num_nos_e_tempo_com_devpad_B{b_val}_1024s_relatorio.pdf'
    caminho_salvar_comb = os.path.join(base_path, nome_grafico_comb)
    plt.savefig(caminho_salvar_comb, bbox_inches='tight')
    if show_plot:
        plt.show()
    plt.close(fig)

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    print("--- INICIANDO GERAÇÃO DE GRÁFICOS DE EVOLUÇÃO ---")
    if not os.path.isdir(ROOT_DATA_PATH):
        print(f"ERRO CRÍTICO: O caminho raiz '{ROOT_DATA_PATH}' não foi encontrado.")
    else:
        for b_valor in B_VALUES_TO_ANALYZE:
            processar_e_plotar_graficos_com_devpad(ROOT_DATA_PATH, b_valor, show_plot=MOSTRAR_GRAFICOS)
            print("-" * 60)
    print("--- GERAÇÃO DE GRÁFICOS CONCLUÍDA ---")
