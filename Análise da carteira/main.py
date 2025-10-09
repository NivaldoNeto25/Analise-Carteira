import yfinance as yf          # Para baixar dados financeiros do Yahoo Finance
import funcoes                 # Módulo personalizado com funções auxiliares

# === Definições iniciais ===
tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]   # Lista de ações da carteira (Petrobras, Vale e Itaú)
weights = [1/3, 1/3, 1/3]                        # Pesos iguais para cada ativo
initial_capital = 100_000                        # Capital inicial da carteira (R$ 100 mil)

# === Taxa livre de risco (CDI/Selic) ===
rf_anual = 13.59                                 # Taxa anual em porcentagem
rf_mensal = (1 + rf_anual/100)**(1/12) - 1       # Converte taxa anual para mensal (capitalização composta)
rf_mensal_pct = rf_mensal * 100                  # Converte para porcentagem mensal

# === Download de preços mensais das ações ===
data = yf.download(
    tickers,
    start="2021-01-02",
    end="2025-01-02",
    interval="1mo",
    progress=False
)["Close"]

# Ajusta os dados para garantir uma observação por mês (último preço do mês)
data = data.resample("ME").last().ffill().bfill()

# === Download do índice IBOVESPA (mercado de referência) ===
ibov = yf.download(
    "^BVSP",
    start="2021-01-02",
    end="2025-01-02",
    interval="1mo",
    progress=False
)["Close"]

# Mesmo ajuste para o IBOV: usa o último preço de cada mês
ibov = ibov.resample("ME").last().ffill().bfill()

# === Cálculo dos retornos do IBOV ===
if ibov.empty:
    print("nenhum dado retornado para o ibov no período definido")
    retornos_ibov = []
else:
    # Calcula o retorno percentual mensal do IBOV usando função auxiliar
    retornos_ibov = funcoes.calcular_retorno_mensal(list(ibov))

# === Exibe os preços mensais das ações ===
print("=== Preços Mensais Ajustados ===")
print(data.round(4))

# === Cálculo dos retornos de cada empresa ===
retornos_empresas = []
for ticker in tickers:
    precos = data[ticker].tolist()                      # Converte os preços para lista
    retornos = funcoes.calcular_retorno_mensal(precos)  # Calcula os retornos mensais
    retornos_empresas.append(retornos)

# === Estatísticas individuais de cada ação ===
for i, ticker in enumerate(tickers):
    r = retornos_empresas[i]
    print(f"\n=== {ticker} ===")
    print("Retorno médio mensal:", funcoes.media(r), "%")
    print("Desvio padrão mensal:", funcoes.desvio_padrao(r), "%")
    print("Coeficiente de variação:", funcoes.coef_variacao(r), "%")

# === Correlação entre os ativos ===
print("\n=== Correlação 2 a 2 ===")
for i in range(len(tickers)):
    for j in range(i+1, len(tickers)):
        # Calcula correlação entre pares de ativos
        c = funcoes.correlacao(retornos_empresas[i], retornos_empresas[j])
        print(f"{tickers[i]} x {tickers[j]}: {c}")

# === Estatísticas da carteira ===
retorno_carteira = funcoes.retorno_medio_carteira(retornos_empresas, weights)
print("\n=== Estatísticas da Carteira ===")
print("Retorno médio mensal da carteira:", funcoes.media(retorno_carteira), "%")
print("Desvio padrão mensal da carteira:", funcoes.desvio_padrao(retorno_carteira), "%")

# === Simulação do valor final da carteira ===
valor_final_carteira = initial_capital
for r in retorno_carteira:
    # Atualiza o valor a cada mês aplicando o retorno percentual
    valor_final_carteira *= (1 + r/100)

print("Valor final da carteira após 48 meses:", round(valor_final_carteira, 2))

# === Cálculo do retorno total em % no período ===
ret_total_carteira = funcoes.retorno_total(initial_capital, valor_final_carteira)
print("Retorno total da carteira após 48 meses:", ret_total_carteira, "%")

# === Cálculo do CAPM para cada ativo ===
print("\n=== CAPM dos Ativos ===")

# Retorno médio mensal do mercado (IBOV)
retorno_medio_mercado = funcoes.media(retornos_ibov)

for ticker in tickers:
    acao = yf.Ticker(ticker)
    beta = acao.info.get("beta")        # Obtém o Beta da ação (risco sistemático)
    if beta is None:                    # Se não existir, define como 0
        beta = 0
    # Aplica fórmula do CAPM: E(Ri) = Rf + Beta * (Rm - Rf)
    capm = funcoes.calcular_capm(rf_mensal_pct, beta, retorno_medio_mercado)
    print(f"{ticker}: Beta = {beta}, CAPM = {capm}%")