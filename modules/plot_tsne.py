import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE

# Carregar o dataset
data = pd.read_csv('results/dataset_chamadas_real.csv')

# Selecionar features
features = ['bitrate_kbps', 'jitter_ms', 'latencia_ms', 'packet_loss_percent']
X = data[features]

# Carregar as predições feitas anteriormente
# Ou refaça aqui, se necessário
y_pred = np.where(data['status'] == 'Sucesso', 0, 1)  # Ajuste se tiver salvo os rótulos preditos antes

# Padronizar os dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Aplicar t-SNE
tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, learning_rate='auto', init='pca', random_state=42)
X_embedded = tsne.fit_transform(X_scaled)

# Plot
plt.figure(figsize=(10,6))
sns.scatterplot(x=X_embedded[:,0], y=X_embedded[:,1], hue=y_pred, palette='coolwarm', s=60)
plt.title('Visualização das Chamadas (t-SNE) - Isolation Forest')
plt.xlabel('t-SNE Dimensão 1')
plt.ylabel('t-SNE Dimensão 2')
plt.legend(title='Predição (0=Normal, 1=Anômalo)')
plt.tight_layout()
plt.savefig('results/tsne_isolation_forest_corrigido.png')
plt.show()
