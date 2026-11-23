import pandas as pd
from sklearn.cluster import KMeans

def agrupar_pedidos_kmeans(df_pedidos, df_nos, n_entregadores=3, random_state=42):
    """Agrupa pedidos em zonas geográficas usando K-Means."""
    df_merged = df_pedidos.merge(df_nos[["id", "x", "y", "nome"]], left_on="no_destino", right_on="id")
    coordenadas = df_merged[["x", "y"]].values

    kmeans = KMeans(n_clusters=n_entregadores, random_state=random_state, n_init=10)
    df_merged["cluster_entregador"] = kmeans.fit_predict(coordenadas)
    centroides = kmeans.cluster_centers_

    return df_merged, centroides
