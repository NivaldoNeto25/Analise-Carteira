def calcular_retorno_mensal(precos):
    """
    Calcula o retorno percentual mensal de uma série de preços.
    Retorno = ((Preço atual - Preço anterior) / Preço anterior) * 100
    """
    if len(precos) < 2:  # É necessário pelo menos 2 preços para calcular retorno
        return []

    retornos = []
    for i in range(1, len(precos)):
        # Calcula o retorno percentual do mês atual em relação ao anterior
        r = ((precos[i] - precos[i-1]) / precos[i-1]) * 100
        retornos.append(round(r, 4))  # Arredonda para 4 casas decimais

    return retornos


def media(lista):
    """
    Calcula a média aritmética de uma lista numérica.
    """
    if len(lista) == 0:
        return 0  # Evita divisão por zero
    return round(sum(lista) / len(lista), 4)


def desvio_padrao(lista):
    """
    Calcula o desvio padrão amostral de uma lista numérica.
    Mede a dispersão dos valores em relação à média.
    """
    if len(lista) < 2:
        return 0  # É necessário pelo menos 2 dados para calcular o desvio padrão

    m = media(lista)
    soma = 0

    # Soma dos quadrados dos desvios em relação à média
    for x in lista:
        soma += (x - m)**2

    # Fórmula do desvio padrão amostral: sqrt(Σ(x - média)² / (n - 1))
    return round((soma / (len(lista)-1))**0.5, 4)


def coef_variacao(lista):
    """
    Calcula o coeficiente de variação (%), que mede o risco relativo.
    Fórmula: (desvio padrão / média) * 100
    """
    m = media(lista)
    if m == 0:
        return None  # Evita divisão por zero se a média for zero
    return round((desvio_padrao(lista) / m) * 100, 4)


def correlacao(lista_x, lista_y):
    """
    Calcula a correlação de Pearson entre duas listas numéricas.
    Mede a relação linear entre dois conjuntos de retornos (entre -1 e 1).
    """
    # As listas devem ter o mesmo tamanho e pelo menos 2 elementos
    if len(lista_x) != len(lista_y) or len(lista_x) < 2:
        return 0

    mx = media(lista_x)
    my = media(lista_y)

    numerador = 0
    denom_x = 0
    denom_y = 0

    # Calcula covariância e desvios padrão de cada lista
    for i in range(len(lista_x)):
        numerador += (lista_x[i] - mx) * (lista_y[i] - my)
        denom_x += (lista_x[i] - mx)**2
        denom_y += (lista_y[i] - my)**2

    # Evita divisão por zero caso um dos desvios seja nulo
    if denom_x == 0 or denom_y == 0:
        return 0

    # Fórmula: cov(X, Y) / (σx * σy)
    return round(numerador / ((denom_x**0.5) * (denom_y**0.5)), 4)


def retorno_medio_carteira(retornos_empresas, pesos):
    """
    Calcula o retorno mensal da carteira com base nos retornos individuais e seus pesos.
    Retorno carteira = Σ (peso_i * retorno_i)
    """
    if not retornos_empresas or len(retornos_empresas[0]) == 0:
        return []

    n = len(retornos_empresas[0])  # Número de períodos
    carteira = []

    # Itera mês a mês, somando os retornos ponderados dos ativos
    for i in range(n):
        r = 0
        for j in range(len(retornos_empresas)):
            r += retornos_empresas[j][i] * pesos[j]
        carteira.append(round(r, 4))

    return carteira


def retorno_total(preco_inicial, preco_final, evento=0):
    """
    Calcula o retorno total percentual entre dois valores.
    Pode incluir um 'evento' adicional (ex: dividendos recebidos).
    Fórmula: ((Final - Inicial + evento) / Inicial) * 100
    """
    if preco_inicial == 0:
        return 0  # Evita divisão por zero

    r = ((preco_final - preco_inicial + evento) / preco_inicial) * 100
    return round(r, 4)


def calcular_capm(rf_mensal_pct, beta, retorno_mercado_mensal_pct):
    """
    Calcula o retorno esperado de um ativo pelo modelo CAPM:
    E(Ri) = Rf + Beta * (Rm - Rf)
    Onde:
      - Rf = retorno livre de risco (%)
      - Beta = risco sistemático da ação
      - Rm = retorno esperado do mercado (%)
    """
    return round(rf_mensal_pct + beta * (retorno_mercado_mensal_pct - rf_mensal_pct), 4)