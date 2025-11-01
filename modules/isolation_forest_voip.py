import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.manifold import TSNE
import seaborn as sns

# 1. Carregar o dataset
dataset = pd.read_csv('../results/dataset_chamadas_variado.csv')

# 2. Pré-processamento
# Vamos usar apenas 'duracao_segundos' como feature
X = dataset[['duracao_segundos']]

# Para avaliação supervisionada: criar os labels
# Sucesso = 0 (normal), Chamada_Curta = 1 (anômalo)
y_true = dataset['status'].apply(lambda x: 0 if x == 'Sucesso' else 1)

# 3. Criar e treinar o Isolation Forest
model = IsolationForest(contamination=0.3, random_state=42)  # 30% anomalias esperadas
model.fit(X)

# 4. Fazer predições
y_pred = model.predict(X)
# Ajustar predição: Isolation Forest retorna -1 para anomalias e 1 para normais
y_pred = np.where(y_pred == 1, 0, 1)

# 5. Avaliação dos resultados
print("\n📊 Matriz de Confusão:")
cm = confusion_matrix(y_true, y_pred)
print(cm)

print("\n📋 Relatório de Classificação:")
print(classification_report(y_true, y_pred, target_names=["Normal", "Anômalo"]))

# 6. Visualização com t-SNE
tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
X_embedded = tsne.fit_transform(X)

plt.figure(figsize=(8,6))
sns.scatterplot(x=X_embedded[:,0], y=X_embedded[:,1], hue=y_pred, palette=["blue", "red"], legend='full')
plt.title('Visualização t-SNE: Normais (azul) vs Anômalos (vermelho)')
plt.xlabel('t-SNE Dimension 1')
plt.ylabel('t-SNE Dimension 2')
plt.legend(title="Classe")
plt.grid(True)
plt.tight_layout()
plt.savefig('results/tsne_isolation_forest.png')
plt.show()

print("\n✅ Script finalizado com sucesso!")
