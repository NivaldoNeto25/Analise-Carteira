def calcular_retorno_mensal(precos):
    retornos = []
    for i in range(1, len(precos)):
        r = ((precos[i] - precos[i-1]) / precos[i-1]) * 100
        retornos.append(round(r, 4))
    return retornos

def media(lista):
    return round(sum(lista) / len(lista), 4)

def desvio_padrao(lista):
    m = media(lista)
    soma = 0
    for x in lista:
        soma += (x - m)**2
    return round((soma / (len(lista)-1))**0.5, 4)

def coef_variacao(lista):
    m = media(lista)
    if m == 0:
        return None
    return round((desvio_padrao(lista) / m) * 100, 4)

def correlacao(lista_x, lista_y):
    if len(lista_x) != len(lista_y):
        raise ValueError("Listas de tamanhos diferentes")
    mx = media(lista_x)
    my = media(lista_y)
    numerador = 0
    denom_x = 0
    denom_y = 0
    for i in range(len(lista_x)):
        numerador += (lista_x[i]-mx)*(lista_y[i]-my)
        denom_x += (lista_x[i]-mx)**2
        denom_y += (lista_y[i]-my)**2
    return round(numerador / ((denom_x**0.5)*(denom_y**0.5)), 4)

def retorno_medio_carteira(retornos_empresas, pesos):
    n = len(retornos_empresas[0])
    carteira = []
    for i in range(n):
        r = 0
        for j in range(len(retornos_empresas)):
            r += retornos_empresas[j][i] * pesos[j]
        carteira.append(round(r, 4))
    return carteira

def retorno_total(preco_inicial, preco_final, evento=0):
    r = ((preco_final - preco_inicial + evento) / preco_inicial) * 100
    return round(r, 4)