import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix, classification_report

# Carregar o novo dataset
print("\U0001F4C2 Lendo o dataset real...")
data = pd.read_csv('results/dataset_chamadas_real.csv')

# Selecionar features para o modelo
features = ['bitrate_kbps', 'jitter_ms', 'latencia_ms', 'packet_loss_percent']
X = data[features]

# Preparar rótulos reais
# 'Sucesso' = 0 (Normal)
# Outros ('Problema_Metrica', 'Chamada_Curta') = 1 (Anômalo)
data['target'] = np.where(data['status'] == 'Sucesso', 0, 1)
y_true = data['target']

# Treinar Isolation Forest
print("\U0001F9EA Treinando Isolation Forest...")
iso_forest = IsolationForest(contamination=0.3, random_state=42)
iso_forest.fit(X)

# Previsões
y_pred = iso_forest.predict(X)

# Ajustar a saída: IsolationForest retorna -1 para anomalia, 1 para normal
# Vamos converter para 0 (normal) e 1 (anomalia) igual o nosso y_true
y_pred = np.where(y_pred == 1, 0, 1)

# Avaliação
print("\n\U0001F4CA Matriz de Confusão:")
print(confusion_matrix(y_true, y_pred))

print("\n\U0001F4CB Relatório de Classificação:")
print(classification_report(y_true, y_pred))

# Visualização com t-SNE
print("\n\U0001F5FA️ Reduzindo dimensionalidade com t-SNE para visualizar...")
tsne = TSNE(n_components=2, random_state=42)
X_embedded = tsne.fit_transform(X)

plt.figure(figsize=(10,6))
sns.scatterplot(x=X_embedded[:,0], y=X_embedded[:,1], hue=y_pred, palette='coolwarm', s=60)
plt.title('Visualização das Chamadas (t-SNE) - Isolation Forest')
plt.xlabel('t-SNE Dimensão 1')
plt.ylabel('t-SNE Dimensão 2')
plt.legend(title='Predição (0=Normal, 1=Anômalo)')
plt.tight_layout()
plt.savefig('results/tsne_isolation_forest.png')
print("\U0001F4F7 Gráfico salvo em results/tsne_isolation_forest.png!")
plt.show()
