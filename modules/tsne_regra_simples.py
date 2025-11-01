import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Ler o dataset
df = pd.read_csv('dataset_chamadas_com_metricas.csv')

# Aplicar a regra simples
def regra_simples(row):
    if row['duracao_segundos'] < 8 or row['jitter_ms'] > 80:
        return 1  # Anomalia
    else:
        return 0  # Normal

df['pred_regra'] = df.apply(regra_simples, axis=1)

X = df[['duracao_segundos', 'bitrate_mbps', 'jitter_ms']].values
y_pred = df['pred_regra']

# t-SNE
tsne = TSNE(n_components=2, random_state=42)
X_embedded = tsne.fit_transform(X)

# Plotar
plt.figure(figsize=(8, 6))
scatter = plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=y_pred, cmap='coolwarm', alpha=0.6)
plt.title('t-SNE: Classificação pela Regra Simples (3500 chamadas)')
plt.xlabel('Dimensão 1')
plt.ylabel('Dimensão 2')
plt.colorbar(scatter, label='0 = Normal, 1 = Anomalia')
plt.grid()
plt.show()
