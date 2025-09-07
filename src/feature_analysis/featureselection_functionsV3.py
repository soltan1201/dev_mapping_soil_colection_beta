#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from collections import defaultdict

from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.ensemble import GradientBoostingClassifier

# --- Configurações e Constantes ---
# Use constantes para facilitar a manutenção
BASE_DATA_PATH = Path("roisSoils/")
RESULTS_PATH = Path("analise_features/")
FEATURES_COLS = [
    'blue', 'bsi', 'evi', 'gv', 'mbi', 'msavi', 'ndbi', 'ndsi', 
    'ndvi', 'nir', 'red', 'shade', 'soil', 'swir1', 'ui', 'vdvi'
]
TARGET_COL = 'class' # ou 'classe', unificar o nome da coluna alvo nos CSVs é uma boa prática
MIN_FEATURES_TO_SELECT = 2
N_JOBS = -1  # Usar -1 para aproveitar todos os cores da CPU

# Configuração do logging para uma saída mais limpa
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_feature_selection(df: pd.DataFrame) -> RFECV:
    """
    Executa o RFECV em um DataFrame para selecionar as melhores features.

    Args:
        df (pd.DataFrame): DataFrame contendo as features e a coluna alvo.

    Returns:
        RFECV: O objeto RFECV treinado.
    """
    X = df[FEATURES_COLS]
    y = df[TARGET_COL]

    logging.info(f"Iniciando RFECV em um dataset com shape {X.shape}.")

    # Validação cruzada que será usada dentro do RFECV
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    # O estimador (modelo) que guiará a eliminação de features
    estimator = GradientBoostingClassifier(n_estimators=50, max_depth=2, random_state=42)

    # Seletor RFECV
    selector = RFECV(
        estimator=estimator,
        step=1,
        cv=cv,
        scoring='accuracy',
        min_features_to_select=MIN_FEATURES_TO_SELECT,
        n_jobs=N_JOBS  # Paraleliza a validação cruzada
    )

    selector.fit(X, y)

    logging.info(f"Seleção concluída. Número ótimo de features: {selector.n_features_}")
    logging.info(f"Ranking das features: {selector.ranking_}")

    return selector

def plot_rfecv_results(selector: RFECV, output_path: Path):
    """
    Gera e salva o gráfico de performance do RFECV.
    """
    n_scores = len(selector.cv_results_["mean_test_score"])
    
    fig, ax = plt.subplots()
    ax.set_xlabel("Número de features selecionadas")
    ax.set_ylabel("Acurácia Média (Validação Cruzada)")
    ax.set_title(f"Performance do RFECV\n{output_path.stem}")
    ax.errorbar(
        range(MIN_FEATURES_TO_SELECT, n_scores + MIN_FEATURES_TO_SELECT),
        selector.cv_results_["mean_test_score"],
        yerr=selector.cv_results_["std_test_score"],
        marker='o',
        capsize=3
    )
    # Adiciona uma linha vertical no número ótimo de features
    ax.axvline(selector.n_features_, linestyle="--", color="r", label=f"Ótimo: {selector.n_features_} features")
    ax.legend()
    plt.tight_layout()
    
    logging.info(f"Salvando gráfico em: {output_path}")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig) # Libera memória da figura

def save_selected_features(selector: RFECV, output_path: Path):
    """
    Salva as features selecionadas em um arquivo de texto.
    """
    selected_features = [feat for feat, support in zip(FEATURES_COLS, selector.support_) if support]
    
    logging.info(f"Features selecionadas: {selected_features}")
    with open(output_path, 'w') as f:
        for feature in selected_features:
            f.write(f"{feature}\n")
    logging.info(f"Lista de features salva em: {output_path}")

def process_by_region(files_by_region: dict):
    """
    Processa os arquivos CSV agrupados por região, concatenando-os antes da análise.
    """
    logging.info(f"Iniciando processamento para {len(files_by_region)} regiões.")
    
    for region, files in files_by_region.items():
        logging.info(f"Processando região: {region} ({len(files)} arquivos)")
        
        try:
            # Concatena todos os dataframes da mesma região
            df_list = [pd.read_csv(f) for f in files]
            # Unificar nome da coluna alvo 'classe' para 'class' se necessário
            for df in df_list:
                if 'classe' in df.columns and TARGET_COL not in df.columns:
                    df.rename(columns={'classe': TARGET_COL}, inplace=True)

            concatenated_df = pd.concat(df_list, ignore_index=True)
            
            # Executa a seleção de features
            selector = run_feature_selection(concatenated_df)
            
            # Define os caminhos de saída
            plot_filename = RESULTS_PATH / f"selecao_features_{region}.png"
            txt_filename = RESULTS_PATH / f"features_importantes_{region}.txt"
            
            # Salva os resultados
            plot_rfecv_results(selector, plot_filename)
            save_selected_features(selector, txt_filename)
            
        except Exception as e:
            logging.error(f"Falha ao processar a região {region}: {e}")

def main():
    """
    Função principal para orquestrar a busca de arquivos e o processamento.
    """
    # Garante que o diretório de resultados exista
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    
    # Encontra todos os arquivos CSV no diretório base
    all_csv_files = list(BASE_DATA_PATH.glob("*.csv"))
    if not all_csv_files:
        logging.warning(f"Nenhum arquivo .csv encontrado em {BASE_DATA_PATH}")
        return

    # Agrupa arquivos por região (ex: 'rois_shp_CERRADO_1992' -> 'CERRADO')
    files_by_region = defaultdict(list)
    for f in all_csv_files:
        try:
            # Extrai o nome da região do nome do arquivo (ajuste conforme seu padrão)
            region_name = f.stem.split('_')[-2]
            files_by_region[region_name].append(f)
        except IndexError:
            logging.warning(f"Não foi possível extrair a região do arquivo: {f.name}. Usando 'desconhecida'.")
            files_by_region['desconhecida'].append(f)
            
    process_by_region(files_by_region)
    
    logging.info("Processo concluído com sucesso!")

if __name__ == '__main__':
    main()