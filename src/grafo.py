import math
import pandas as pd
import networkx as nx

def carregar_grafo(nos_path="data/nos_cidade.csv", arestas_path="data/arestas_ruas.csv"):
    """Constrói o grafo ponderado da cidade a partir dos arquivos CSV."""
    df_nos = pd.read_csv(nos_path)
    df_arestas = pd.read_csv(arestas_path)

    G = nx.Graph()
    for _, row in df_nos.iterrows():
        G.add_node(
            int(row["id"]),
            nome=row["nome"],
            x=float(row["x"]),
            y=float(row["y"]),
            tipo=row["tipo"]
        )

    for _, row in df_arestas.iterrows():
        # Peso efetivo considera distância * fator de tráfego (horário de pico)
        custo_tempo = float(row["distancia_km"]) * float(row["fator_trafego"])
        G.add_edge(
            int(row["origem"]),
            int(row["destino"]),
            distancia_km=float(row["distancia_km"]),
            fator_trafego=float(row["fator_trafego"]),
            weight=round(custo_tempo, 3)
        )
    return G, df_nos, df_arestas

def heuristica_euclidiana(G, no_atual, no_destino):
    """Calcula a distância Euclidiana em linha reta entre dois nós (admissível para A*)."""
    x1, y1 = G.nodes[no_atual]["x"], G.nodes[no_atual]["y"]
    x2, y2 = G.nodes[no_destino]["x"], G.nodes[no_destino]["y"]
    return math.hypot(x2 - x1, y2 - y1)
