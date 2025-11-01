import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Ler o dataset
df = pd.read_csv('results/dataset_chamadas_com_metricas.csv')

# Preparar os dados
X = df[['duracao_segundos', 'bitrate_mbps', 'jitter_ms']].values
y_true = df['status'].apply(lambda x: 1 if x == 'Chamada_Curta' else 0)  # 1 = Anomalia, 0 = Normal

# Padronizar as métricas antes do t-SNE
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Treinar Isolation Forest com os dados padronizados
modelo = IsolationForest(contamination=0.3, random_state=42)
modelo.fit(X_scaled)

# Prever
y_pred = modelo.predict(X_scaled)
y_pred = np.where(y_pred == -1, 1, 0)

# t-SNE
tsne = TSNE(n_components=2, perplexity=40, learning_rate=100, n_iter=1500, init='pca', random_state=42)
X_embedded = tsne.fit_transform(X_scaled)

# Novo gráfico com agrupamento
plt.figure(figsize=(10, 7))
colors = np.array(['#4A90E2', '#E94E77'])  # Azul e vermelho
labels = np.array(['Normal', 'Anomalia'])

for i in range(2):
    idx = np.where(y_pred == i)
    plt.scatter(X_embedded[idx, 0], X_embedded[idx, 1], 
                c=colors[i], label=labels[i], alpha=0.7, s=50, edgecolors='k')

plt.title('t-SNE: Agrupamento Normal vs Anômalo (Dados Padronizados)', fontsize=14)
plt.xlabel('Dimensão t-SNE 1')
plt.ylabel('Dimensão t-SNE 2')
plt.legend(title="Classificação", fontsize=12)
plt.grid(True)

plt.tight_layout()
plt.savefig('tsne_isolation_forest_padronizado.png', dpi=300)

plt.show()
