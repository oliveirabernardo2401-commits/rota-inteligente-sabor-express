import heapq
from collections import deque
from src.grafo import heuristica_euclidiana

def busca_a_estrela(G, inicio, objetivo):
    """Implementação do algoritmo A* retornando caminho, custo total e nós explorados."""
    fila_prioridade = [(0, inicio)]
    veio_de = {inicio: None}
    custo_g = {inicio: 0.0}
    nos_explorados = 0

    while fila_prioridade:
        _, atual = heapq.heappop(fila_prioridade)
        nos_explorados += 1

        if atual == objetivo:
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = veio_de[atual]
            return caminho[::-1], round(custo_g[objetivo], 3), nos_explorados

        for vizinho in G.neighbors(atual):
            peso_aresta = G[atual][vizinho]["weight"]
            novo_g = custo_g[atual] + peso_aresta

            if vizinho not in custo_g or novo_g < custo_g[vizinho]:
                custo_g[vizinho] = novo_g
                prioridade_f = novo_g + heuristica_euclidiana(G, vizinho, objetivo)
                heapq.heappush(fila_prioridade, (prioridade_f, vizinho))
                veio_de[vizinho] = atual

    return [], float("inf"), nos_explorados

def busca_bfs(G, inicio, objetivo):
    """Implementação de Busca em Largura (BFS) para comparação de baseline."""
    fila = deque([inicio])
    veio_de = {inicio: None}
    nos_explorados = 0

    while fila:
        atual = fila.popleft()
        nos_explorados += 1

        if atual == objetivo:
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = veio_de[atual]
            caminho = caminho[::-1]
            custo = sum(G[caminho[i]][caminho[i+1]]["weight"] for i in range(len(caminho)-1))
            return caminho, round(custo, 3), nos_explorados

        for vizinho in G.neighbors(atual):
            if vizinho not in veio_de:
                veio_de[vizinho] = atual
                fila.append(vizinho)

    return [], float("inf"), nos_explorados

def otimizar_sequencia_entregas(G, ponto_partida, destinos, algoritmo="astar"):
    """Ordena entregas pelo vizinho mais próximo (custo A*) e constrói a rota completa."""
    nao_visitados = list(set(destinos))
    atual = ponto_partida
    rota_completa = [ponto_partida]
    custo_total = 0.0
    total_nos_explorados = 0

    func_busca = busca_a_estrela if algoritmo == "astar" else busca_bfs

    while nao_visitados:
        melhor_destino = None
        melhor_trecho = []
        menor_custo = float("inf")
        explorados_passo = 0

        for cand in nao_visitados:
            trecho, custo, exp = func_busca(G, atual, cand)
            explorados_passo += exp
            if custo < menor_custo:
                menor_custo = custo
                melhor_destino = cand
                melhor_trecho = trecho

        rota_completa.extend(melhor_trecho[1:])
        custo_total += menor_custo
        total_nos_explorados += explorados_passo
        atual = melhor_destino
        nao_visitados.remove(melhor_destino)

    return rota_completa, round(custo_total, 2), total_nos_explorados
