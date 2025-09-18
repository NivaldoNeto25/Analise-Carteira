import yfinance as yf
import funcoes

tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
weights = [1/3, 1/3, 1/3]
initial_capital = 100_000
rf_anual = 13.59
rf_mensal = (1+rf_anual/100)**(1/12)-1
rf_mensal_pct = rf_mensal * 100

data = yf.download(tickers, start="2021-01-02", end="2025-01-02", interval="1mo", progress=False)["Close"]
data = data.resample("ME").last().ffill().bfill()

ibov = yf.download("^BVSP", start="2021-01-02", end="2025-01-02", interval="1mo", progress=False)["Close"]
ibov = ibov.resample("ME").last().ffill().bfill()

if ibov.empty:
    print("nenhum dado retornado para o ibov no período definido")
    retornos_ibov = []
else:
    retornos_ibov = funcoes.calcular_retorno_mensal(list(ibov))

print("=== Preços Mensais Ajustados ===")
print(data.round(4))

retornos_empresas = []
for ticker in tickers:
    precos = data[ticker].tolist()
    retornos = funcoes.calcular_retorno_mensal(precos)
    retornos_empresas.append(retornos)

for i, ticker in enumerate(tickers):
    r = retornos_empresas[i]
    print(f"\n=== {ticker} ===")
    print("Retorno médio mensal:", funcoes.media(r), "%")
    print("Desvio padrão mensal:", funcoes.desvio_padrao(r), "%")
    print("Coeficiente de variação:", funcoes.coef_variacao(r), "%")

print("\n=== Correlação 2 a 2 ===")
for i in range(len(tickers)):
    for j in range(i+1, len(tickers)):
        c = funcoes.correlacao(retornos_empresas[i], retornos_empresas[j])
        print(f"{tickers[i]} x {tickers[j]}: {c}")

retorno_carteira = funcoes.retorno_medio_carteira(retornos_empresas, weights)
print("\n=== Estatísticas da Carteira ===")
print("Retorno médio mensal da carteira:", funcoes.media(retorno_carteira), "%")
print("Desvio padrão mensal da carteira:", funcoes.desvio_padrao(retorno_carteira), "%")

valor_final_carteira = initial_capital
for r in retorno_carteira:
    valor_final_carteira *= (1 + r/100)

print("Valor final da carteira após 48 meses:", round(valor_final_carteira, 2))

ret_total_carteira = funcoes.retorno_total(initial_capital, valor_final_carteira)
print("Retorno total da carteira após 48 meses:", ret_total_carteira, "%")

print("\n=== CAPM dos Ativos ===")

retorno_medio_mercado = funcoes.media(retornos_ibov)

for ticker in tickers:
    acao = yf.Ticker(ticker)
    beta = acao.info.get("beta")
    if beta is None:
        beta = 0
    capm = funcoes.calcular_capm(rf_mensal_pct, beta, retorno_medio_mercado)
    print(f"{ticker}: Beta = {beta}, CAPM = {capm}%")