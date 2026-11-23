import os
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from src.grafo import carregar_grafo
from src.clustering import agrupar_pedidos_kmeans
from src.busca_rotas import otimizar_sequencia_entregas

def gerar_visualizacoes(G, df_pedidos_cluster, centroides, rotas_por_cluster):
    os.makedirs("docs", exist_ok=True)
    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}

    # 1. Diagrama do Grafo da Cidade
    plt.figure(figsize=(10, 7))
    nx.draw_networkx_edges(G, pos, edge_color="#CBD5E1", width=1.5)
    
    cores_nos = ["#EF4444" if G.nodes[n]["tipo"] == "restaurante" else "#3B82F6" for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=cores_nos, node_size=320)
    labels = {n: f"{n}" for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_color="white", font_size=8, font_weight="bold")

    edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, font_color="#475569")

    plt.title("Grafo da Região Central - Sabor Express (Pesos = Tempo/Distância Ajustada)", fontsize=12, fontweight="bold")
    plt.xlabel("Coordenada X (km)")
    plt.ylabel("Coordenada Y (km)")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig("docs/diagrama_grafo.png", dpi=200)
    plt.close()

    # 2. Mapa de Clusters (K-Means) e Rotas Otimizadas (A*)
    plt.figure(figsize=(11, 8))
    nx.draw_networkx_edges(G, pos, edge_color="#E2E8F0", width=1.0)
    nx.draw_networkx_nodes(G, pos, node_color="#94A3B8", node_size=120, alpha=0.5)

    paleta = ["#10B981", "#F59E0B", "#8B5CF6"]
    
    # Plotar pedidos agrupados por cluster
    for cluster_id in sorted(df_pedidos_cluster["cluster_entregador"].unique()):
        sub = df_pedidos_cluster[df_pedidos_cluster["cluster_entregador"] == cluster_id]
        cor = paleta[cluster_id % len(paleta)]
        plt.scatter(sub["x"], sub["y"], c=cor, s=180, label=f"Zona Entregador {cluster_id + 1} ({len(sub)} pedidos)", zorder=4, edgecolors="black")

        # Desenhar rota A* do cluster
        rota = rotas_por_cluster[cluster_id]["rota"]
        arestas_rota = [(rota[i], rota[i+1]) for i in range(len(rota)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=arestas_rota, edge_color=cor, width=3.0, alpha=0.85)

    # Plotar centroides
    plt.scatter(centroides[:, 0], centroides[:, 1], c="black", marker="X", s=160, label="Centroides (K-Means)", zorder=5)

    # Destacar Restaurante (Nó 0)
    rx, ry = pos[0]
    plt.scatter([rx], [ry], c="#EF4444", marker="s", s=260, label="Sabor Express (Origem)", zorder=6, edgecolors="black")

    for n in G.nodes:
        plt.text(pos[n][0] + 0.08, pos[n][1] + 0.08, str(n), fontsize=7, color="#334155")

    plt.title("Otimização de Entregas: Agrupamento K-Means + Roteamento A*", fontsize=13, fontweight="bold")
    plt.xlabel("Coordenada X (km)")
    plt.ylabel("Coordenada Y (km)")
    plt.legend(loc="upper left", frameon=True)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig("docs/clusters_rotas.png", dpi=200)
    plt.close()

def executar_pipeline():
    print("=== INICIANDO PIPELINE ROTA INTELIGENTE - SABOR EXPRESS ===\n")
    G, df_nos, _ = carregar_grafo()
    df_pedidos = pd.read_csv("data/pedidos_pico.csv")

    n_entregadores = 3
    df_clusterizado, centroides = agrupar_pedidos_kmeans(df_pedidos, df_nos, n_entregadores=n_entregadores)

    rotas_astar = {}
    custo_total_astar = 0.0
    nos_exp_astar = 0

    custo_total_bfs = 0.0
    nos_exp_bfs = 0

    for cid in range(n_entregadores):
        destinos = df_clusterizado[df_clusterizado["cluster_entregador"] == cid]["no_destino"].tolist()
        rota_a, custo_a, exp_a = otimizar_sequencia_entregas(G, ponto_partida=0, destinos=destinos, algoritmo="astar")
        rota_b, custo_b, exp_b = otimizar_sequencia_entregas(G, ponto_partida=0, destinos=destinos, algoritmo="bfs")

        rotas_astar[cid] = {"rota": rota_a, "custo": custo_a, "destinos": destinos}
        custo_total_astar += custo_a
        nos_exp_astar += exp_a

        custo_total_bfs += custo_b
        nos_exp_bfs += exp_b

        print(f"[Entregador {cid + 1}] Pedidos nos nós: {destinos}")
        print(f"   -> Rota A*: {' -> '.join(map(str, rota_a))}")
        print(f"   -> Custo Ponderado (Tempo/Dist): {custo_a} | Nós explorados (A*): {exp_a}\n")

    print("=== COMPARATIVO DE DESEMPENHO (BENCHMARK) ===")
    print(f"A* + K-Means  -> Custo Total: {custo_total_astar:.2f} | Total de Nós Explorados: {nos_exp_astar}")
    print(f"BFS + K-Means -> Custo Total: {custo_total_bfs:.2f} | Total de Nós Explorados: {nos_exp_bfs}")
    economia_nos = ((nos_exp_bfs - nos_exp_astar) / nos_exp_bfs) * 100
    economia_custo = ((custo_total_bfs - custo_total_astar) / custo_total_bfs) * 100
    print(f"Ganho Computacional (menos nós explorados): {economia_nos:.1f}%")
    print(f"Redução de Custo de Rota (peso tráfego/distância): {economia_custo:.1f}%")

    gerar_visualizacoes(G, df_clusterizado, centroides, rotas_astar)
    print("\nGráficos salvos em: docs/diagrama_grafo.png e docs/clusters_rotas.png")

if __name__ == "__main__":
    executar_pipeline()
