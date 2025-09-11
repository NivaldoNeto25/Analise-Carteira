import yfinance as yf
import funcoes

tickers = ["AAPL", "MSFT", "TSLA"]
weights = [1/3, 1/3, 1/3]
initial_capital = 100_000

data = yf.download(tickers, start="2021-01-02", end="2025-01-02", interval="1mo", progress=False)["Close"]
data = data.resample("M").last()
data = data.ffill().bfill()

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