import pandas as pd
import numpy as np
import requests
import zipfile
import io
import matplotlib.pyplot as plt
import yfinance as yf


# Configurações: defini os códigos das ações (tickers) e os anos para os quais os dados serão coletados
tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
anos = [2021, 2022, 2023, 2024]


# Função para extrair um valor específico do dataframe da CVM, procurando por um termo e o ano de referência
def extrair_valor_cvm(df, termo_busca, ano_referencia):
    if df.empty:
        return 0.0
    
    # Definição dos nomes das colunas que contêm as datas e valores, com base na estrutura do dataframe
    col_data = "DT_REFER" if "DT_REFER" in df.columns else "DT_FIM_EXERC"
    col_val = "VL_CONTA" if "VL_CONTA" in df.columns else "VALOR"
    col_cd = "CD_CONTA" if "CD_CONTA" in df.columns else None
    col_ds = "DS_CONTA" if "DS_CONTA" in df.columns else None
    
    # Filtra para contas que são fixas (se a coluna existir) e que correspondam ao ano de referência
    mask_fixa = (df["ST_CONTA_FIXA"].astype(str).str.upper() == "S") if "ST_CONTA_FIXA" in df.columns else True
    df_filtrado = df[mask_fixa & df[col_data].astype(str).str.contains(str(ano_referencia))]
    
    # Se o termo buscado contém dígitos, busca na coluna do código da conta. Caso contrário, na descrição da conta.
    if col_cd and any(c.isdigit() for c in termo_busca):
        df_matched = df_filtrado[df_filtrado[col_cd].astype(str).str.startswith(termo_busca)]
    else:
        df_matched = df_filtrado[df_filtrado[col_ds].astype(str).str.contains(termo_busca, case=False, na=False)]
    
    # Se encontrou resultado, converte o valor para float e multiplica por 1000 para ajustar a unidade
    if not df_matched.empty:
        try:
            valor_str = str(df_matched[col_val].iloc[0]).replace(".", "").replace(",", ".")
            valor = float(valor_str) * 1000
            return valor
        except:
            return 0.0
    return 0.0


# Função que baixa os dados financeiros da CVM para um dado nome de empresa e anos especificados
def baixar_dados_cvm(nome_empresa, anos_consulta):
    url_base = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{}.zip"
    bpa_list, bpp_list, dre_list = [], [], []
    for ano in anos_consulta:
        url = url_base.format(ano)
        try:
            response = requests.get(url)
            response.raise_for_status()
            # Descompacta os arquivos zip e separa os dados em BP Ativo (bpa), BP Passivo (bpp) e DRE (dre)
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                for arquivo in z.namelist():
                    arq_lower = arquivo.lower()
                    if "bpa_con" in arq_lower:
                        with z.open(arquivo) as f:
                            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)
                            bpa_list.append(df)
                    elif "bpp_con" in arq_lower:
                        with z.open(arquivo) as f:
                            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)
                            bpp_list.append(df)
                    elif "dre_con" in arq_lower:
                        with z.open(arquivo) as f:
                            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)
                            dre_list.append(df)
        except Exception as e:
            print(f"Erro ao baixar dados do ano {ano}: {e}")

    # Função para concatenar os dataframes de uma lista e filtrar pela empresa desejada
    def concat_filtrar(lista):
        if not lista:
            return pd.DataFrame()
        df_total = pd.concat(lista, ignore_index=True)
        df_total.columns = [c.upper().strip() for c in df_total.columns]
        if 'DENOM_CIA' in df_total.columns:
            return df_total[df_total['DENOM_CIA'].str.contains(nome_empresa, case=False, na=False)]
        return df_total
    
    # Retorna os dataframes filtrados para o ativo, passivo e DRE
    return concat_filtrar(bpa_list), concat_filtrar(bpp_list), concat_filtrar(dre_list)


resultado_final = []


# Loop para processar cada ticker especificado
for ticker in tickers:
    print(f"\nProcessando {ticker}...")

    # Identificação manual do nome da companhia para corresponder aos dados da CVM
    if "PETR" in ticker:
        nome_cia = "PETROBRAS"
    elif "VALE" in ticker:
        nome_cia = "VALE"
    elif "ITUB" in ticker:
        nome_cia = "ITAÚ"
    else:
        nome_cia = ticker.split('.')[0]

    # Busca os dados financeiros do Yahoo Finance: balanço patrimonial (balance_sheet) e demonstração de resultado (financials)
    yf_ticker = yf.Ticker(ticker)
    balanco = yf_ticker.balance_sheet
    dre = yf_ticker.financials
    
    # Transforma os dados para formato com os anos no índice
    if not balanco.empty:
        balanco = balanco.T
        balanco.index = balanco.index.year
    if not dre.empty:
        dre = dre.T
        dre.index = dre.index.year

    # Baixa os dados da CVM para os anos configurados
    df_bpa, df_bpp, df_dre = baixar_dados_cvm(nome_cia, anos)

    # Para cada ano, extrai os valores necessários e calcula os indicadores
    for ano in anos:
        ativo_circ = passivo_circ = estoques = fornecedores = ativo_total = receita_liquida = cpv = np.nan

        # Tenta buscar os valores no Yahoo Finance
        if not balanco.empty and ano in balanco.index:
            ativo_circ = balanco.loc[ano].get("Total Current Assets", np.nan)
            passivo_circ = balanco.loc[ano].get("Total Current Liabilities", np.nan)
            estoques = balanco.loc[ano].get("Inventory", np.nan)
            fornecedores = balanco.loc[ano].get("Accounts Payable", np.nan)
            ativo_total = balanco.loc[ano].get("Total Assets", np.nan)
        if not dre.empty and ano in dre.index:
            receita_liquida = dre.loc[ano].get("Total Revenue", np.nan)
            cpv = dre.loc[ano].get("Cost Of Revenue", np.nan)

        # Caso os valores estejam ausentes ou zerados, tenta extrair da base da CVM
        if np.isnan(ativo_circ) or ativo_circ == 0:
            ativo_circ = extrair_valor_cvm(df_bpa, "1.01", ano) or extrair_valor_cvm(df_bpa, "ATIVO CIRCULANTE", ano)
        if np.isnan(passivo_circ) or passivo_circ == 0:
            passivo_circ = extrair_valor_cvm(df_bpp, "2.01", ano) or extrair_valor_cvm(df_bpp, "PASSIVO CIRCULANTE", ano)
        if np.isnan(estoques) or estoques == 0:
            estoques = extrair_valor_cvm(df_bpa, "1.02.04", ano) or extrair_valor_cvm(df_bpa, "ESTOQUES", ano)
        if np.isnan(fornecedores) or fornecedores == 0:
            fornecedores = extrair_valor_cvm(df_bpp, "2.01.02", ano) or extrair_valor_cvm(df_bpp, "FORNECEDORES", ano)
        if np.isnan(ativo_total) or ativo_total == 0:
            ativo_total = extrair_valor_cvm(df_bpa, "1", ano) or extrair_valor_cvm(df_bpa, "ATIVO TOTAL", ano)
        if np.isnan(receita_liquida) or receita_liquida == 0:
            receita_liquida = extrair_valor_cvm(df_dre, "3.01", ano) or extrair_valor_cvm(df_dre, "RECEITA", ano)
        if np.isnan(cpv) or cpv == 0:
            cpv = extrair_valor_cvm(df_dre, "3.02", ano) or extrair_valor_cvm(df_dre, "CUSTO", ano)

        # Cálculo dos indicadores financeiros principais
        if passivo_circ and passivo_circ > 0:
            liquidez_corrente = ativo_circ / passivo_circ
            liquidez_seca = (ativo_circ - estoques) / passivo_circ
        else:
            liquidez_corrente = liquidez_seca = np.nan

        giro_ativo = receita_liquida / ativo_total if ativo_total and ativo_total > 0 else np.nan

        prazo_medio_pagamento = (fornecedores / cpv) * 360 if cpv and cpv > 0 else np.nan

        # Armazena resultados formatados em lista
        resultado_final.append({
            "Empresa": ticker,
            "Ano": ano,
            "Liquidez Corrente": round(liquidez_corrente, 2) if not np.isnan(liquidez_corrente) else "N/D",
            "Liquidez Seca": round(liquidez_seca, 2) if not np.isnan(liquidez_seca) else "N/D",
            "Giro do Ativo": round(giro_ativo, 2) if not np.isnan(giro_ativo) else "N/D",
            "Prazo Médio de Pagamento (dias)": round(prazo_medio_pagamento, 2) if not np.isnan(prazo_medio_pagamento) else "N/D"
        })


# Converte a lista final em DataFrame, ordena e reinicia índice
df_resultados = pd.DataFrame(resultado_final).sort_values(by=["Empresa", "Ano"]).reset_index(drop=True)
print("\nÍndices Financeiros por Empresa e Ano:\n")
print(df_resultados)


# Exporta os resultados para um arquivo Excel
df_resultados.to_excel("indices_financeiros_tickers.xlsx", index=False)
print("\n✅ Resultados exportados para 'indices_financeiros_tickers.xlsx'.")


# Bloco para gerar gráficos dos indicadores extraídos, para cada empresa e indicador relevante
try:
    for indicador in ["Liquidez Corrente", "Giro do Ativo", "Prazo Médio de Pagamento (dias)"]:
        plt.figure(figsize=(8, 5))
        df_plot = df_resultados[df_resultados[indicador] != "N/D"].copy()
        df_plot.loc[:, indicador] = df_plot[indicador].astype(float)
        for empresa in df_plot["Empresa"].unique():
            dados_emp = df_plot[df_plot["Empresa"] == empresa]
            plt.plot(dados_emp["Ano"], dados_emp[indicador], marker='o', label=empresa)
        plt.title(f"{indicador} (2021-2024)")
        plt.xlabel("Ano")
        plt.ylabel(indicador)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()
except Exception:
    print("Erro ao gerar gráficos (verifique se o matplotlib está instalado).")