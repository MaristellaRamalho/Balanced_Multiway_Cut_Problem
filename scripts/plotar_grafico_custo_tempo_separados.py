"""
Gera:
- um arquivo PDF contendo TRÊS gráficos de custo x tempo 
um para cada número de nós (160, 320, 640). O custo está normalizado pelo melhor custo dentro de cada isntancia.
- 3 arquivos .pdf separados com o grafico completo (um para cada número de nós)

Cada gráfico mostra a evolução do Custo Médio (com barras de erro 
para o desvio padrão) em função do Tempo de Execução. As diferentes 
linhas dentro de cada gráfico representam as funções de penalidade (6 linhas).

├── ROOT_DATA_PATH
    ├── arquivo_comparativos.xlsx (EXCEL_FILENAME)

A planilha deve ter, dentro de cada ABA , as medias e o desvio padrao do custo para cada coluna de penalidade, filtrado pelo numero de nos da instancia -> calcular direto na planilha

MÉDIA DO CUSTO PLOTADA COMO MÉDIA MENOS 1 -> Escala linear no eixo y (em %)
"""
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import re
import numpy as np

# --- CONFIGURAÇÕES GERAIS ---
# Caminho para a PASTA que contém o arquivo Excel.
ROOT_DATA_PATH = Path("/mnt/c/Users/maris/OneDrive/Documentos/IC_Maristella/BRKGA_BMCP/dados_refatoracao_13_08")

# Nome do arquivo Excel que será lido.
EXCEL_FILENAME = "comparativo_bestCost_normalizado_validSolution_4s.xlsx"

# Nome do arquivo PDF que será gerado.
OUTPUT_PDF_FILENAME = "grafico_custo_por_num_nos_e_tempo_com_devpad_B2_1024s_porcentagem_refatoracao.pdf"

# Exibir os gráficos na tela após gerar? (True/False)
MOSTRAR_GRAFICOS = False

# Nomes e prefixos usados na planilha de CUSTO
PREFIXO_COLUNA_CUSTO = 'best_cost_'
ROTULO_MEDIA = 'Média best_cost'
ROTULO_DESVIO = 'Desvio Padrão'

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
    """Extrai o número de nós de uma string como 'Média best_cost (160 nós)'."""
    match = re.search(r'\((\d+)\s*nós\)', texto)
    if match:
        return int(match.group(1))
    return None

def gerar_graficos_evolucao(caminho_arquivo_excel, show_plot=False):
    """
    Lê um arquivo excel com múltiplas abas de tempo, lê as médias e desvios pré-calculados e gera um PDF combinado com subplots de evolução do custo e exporta cada subplot (3 graficos) como um pdf separado
"""
    print(f"--- Iniciando análise de: {caminho_arquivo_excel.name} ---")

    try:
        xls = pd.ExcelFile(caminho_arquivo_excel)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo '{caminho_arquivo_excel}' não foi encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao abrir o arquivo Excel: {e}")
        return

    lista_resultados_agregados = []

    for sheet_name in xls.sheet_names:
        match = re.search(r'_(\d+s)$', sheet_name)
        if not match:
            continue
        tempo_str = match.group(1)
        tempo_num = int(tempo_str.replace('s', ''))

        df = pd.read_excel(xls, sheet_name=sheet_name)
        colunas_custo = [col for col in df.columns if str(col).startswith(PREFIXO_COLUNA_CUSTO)]

        df_medias = df[df['Algoritmo'].str.contains(ROTULO_MEDIA, na=False)].copy()
        df_desvios = df[df['Algoritmo'].str.contains(ROTULO_DESVIO, na=False)].copy()

        if df_medias.empty or df_desvios.empty:
            print(f" AVISO: Não foram encontradas as linhas com os rótulos '{ROTULO_MEDIA}' ou '{ROTULO_DESVIO}' na aba '{sheet_name}'. Pulando.")
            continue

        for col in colunas_custo:
            df_medias[col] = pd.to_numeric(df_medias[col], errors='coerce')
            df_desvios[col] = pd.to_numeric(df_desvios[col], errors='coerce')

        df_medias['Nodes'] = df_medias['Algoritmo'].apply(extrair_nos)
        df_desvios['Nodes'] = df_desvios['Algoritmo'].apply(extrair_nos)

        df_medias_long = df_medias.melt(id_vars=['Nodes'], value_vars=colunas_custo, var_name='Penalidade', value_name='Custo_Medio')
        df_desvios_long = df_desvios.melt(id_vars=['Nodes'], value_vars=colunas_custo, var_name='Penalidade', value_name='Desvio_Padrao')

        df_merged = pd.merge(df_medias_long, df_desvios_long, on=['Nodes', 'Penalidade'])
        df_merged['Tempo'] = tempo_num

        lista_resultados_agregados.append(df_merged)

    if not lista_resultados_agregados:
        print("\nERRO CRÍTICO: Nenhum dado foi agregado. Verifique os nomes das abas, colunas e os rótulos de média/desvio no arquivo Excel.")
        return

    df_final = pd.concat(lista_resultados_agregados, ignore_index=True)
    df_final['Penalidade'] = df_final['Penalidade'].str.replace(PREFIXO_COLUNA_CUSTO, '').map(MAPEAMENTO_LEGENDA)
    df_final.dropna(inplace=True)

    plt.style.use('seaborn-v0_8-whitegrid')
    nodes_unicos = sorted(df_final['Nodes'].unique())

    #Ordem da legenda
    ordem_penalidades = ['Sem Penalidade', 'Maxzera', 'Maxrange', 'Quadzera', 'Quadrange', 'QuadrangeTotal']
    #Cores de cada penalidade
    color_map = {
        'Maxzera':        '#1e76b3',
        'Maxrange':       '#ff7e0d',
        'Quadzera':       '#2b9f2b',
        'Quadrange':      '#da4243',
        'Quadrangetotal': '#9366bc',
        'Sem penalidade': '#8b564a'
    }

    fig, axes = plt.subplots(
        nrows=len(nodes_unicos), ncols=1,
        figsize=(16, 8 * len(nodes_unicos)),
        sharex=True
    )
    if len(nodes_unicos) == 1:
        axes = [axes]

    for i, nodes in enumerate(nodes_unicos):
        ax_combined = axes[i]
        df_subplot = df_final[df_final['Nodes'] == nodes]
        
        #Grafico individual
        fig_ind, ax_ind = plt.subplots(figsize=(14, 9))

        for penalty in ordem_penalidades:
            df_line = df_subplot[df_subplot['Penalidade'] == penalty].sort_values('Tempo')
            if not df_line.empty:
                cor_especifica = color_map.get(penalty)
                
                #Eixo y em %
                ax_combined.errorbar(
                    x=df_line['Tempo'], y=(df_line['Custo_Medio'] - 1) * 100,
                    yerr=df_line['Desvio_Padrao'] * 100, label=penalty,
                    fmt='-o', capsize=4, ms=6, lw=1.5, color=cor_especifica
                )
                
                ax_ind.errorbar(
                    x=df_line['Tempo'], y=(df_line['Custo_Medio'] - 1) * 100,
                    yerr=df_line['Desvio_Padrao'] * 100, label=penalty,
                    fmt='-o', capsize=4, ms=6, lw=1.5, color=cor_especifica
                )

        for ax in [ax_combined, ax_ind]:
            ax.set_xscale('log', base=2)
            ax.grid(which='both', linestyle='--', linewidth='0.5')
            ax.tick_params(axis='both', which='major', labelsize=12)
            tempos_unicos = sorted(df_final['Tempo'].unique())
            ax.set_xticks(tempos_unicos)
            ax.get_xaxis().set_major_formatter(ScalarFormatter())

        ax_combined.set_title(f'Evolução do Custo Médio Normalizado para Instâncias com {nodes} Nós', fontsize=18, pad=15)
        ax_combined.set_ylabel('diferença ao menor custo normalizado (%)', fontsize=14)
        
        ax_ind.set_title(f'Evolução do Custo Médio Normalizado para Instâncias com {nodes} Nós (B=2)', fontsize=18, pad=15)
        ax_ind.set_ylabel('diferença ao menor custo normalizado (%)', fontsize=14)
        ax_ind.set_xlabel('Tempo de Execução (segundos)', fontsize=14, labelpad=15)
        
        loc_map = {160: 'upper right', 320: 'upper right', 640: 'upper right'}
        ax_ind.legend(loc=loc_map.get(nodes, 'best'), title='Função de Penalidade', fontsize=12, title_fontsize=14)

        fig_ind.tight_layout()
        output_path_ind = ROOT_DATA_PATH / f"grafico_custo_{nodes}_nos.pdf"
        fig_ind.savefig(output_path_ind, bbox_inches='tight')
        plt.close(fig_ind)
    
    axes[-1].set_xlabel('Tempo de Execução (segundos)', fontsize=16, labelpad=15)
    
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles=handles, labels=labels, title='Função de Penalidade',
        bbox_to_anchor=(1.01, 0.5), loc='center left', fontsize=12, title_fontsize=14
    )
    
    fig.suptitle('Custo por Tamanho da Instância e Tempo (B = 2)', fontsize=22, y=1.0)
    fig.tight_layout(rect=[0, 0, 0.90, 0.98])

    output_path_comb = ROOT_DATA_PATH / OUTPUT_PDF_FILENAME
    plt.savefig(output_path_comb, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close(fig)

if __name__ == '__main__':
    caminho_completo = ROOT_DATA_PATH / EXCEL_FILENAME
    gerar_graficos_evolucao(caminho_completo, show_plot=MOSTRAR_GRAFICOS)
    print("\n--- Processo concluído ---")
