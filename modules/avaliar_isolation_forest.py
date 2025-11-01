import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

# Ler o dataset
df = pd.read_csv('results/dataset_chamadas_com_metricas.csv')

# Preparar os dados
X = df[['duracao_segundos', 'bitrate_mbps', 'jitter_ms']].values
y_true = df['status'].apply(lambda x: 1 if x == 'Chamada_Curta' else 0)  # 1 = Anomalia, 0 = Normal

# Treinar Isolation Forest
modelo = IsolationForest(contamination=0.3, random_state=42)
modelo.fit(X)

# Prever
y_pred = modelo.predict(X)
y_pred = np.where(y_pred == -1, 1, 0)  # Isolation Forest: -1 = Anomalia, 1 = Normal

# Matriz de Confusão
print("Matriz de Confusão - Isolation Forest:")
print(confusion_matrix(y_true, y_pred))

# Relatório
print("\nRelatório:")
print(classification_report(y_true, y_pred, target_names=["Normal", "Anomalia"]))

# Curva ROC
fpr, tpr, thresholds = roc_curve(y_true, y_pred)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f'ROC curve (área = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel('Taxa de Falsos Positivos (FPR)')
plt.ylabel('Taxa de Verdadeiros Positivos (TPR)')
plt.title('Curva ROC - Isolation Forest (3500 chamadas)')
plt.legend(loc="lower right")
plt.grid()

# >>>> Adicione esta linha para SALVAR o gráfico
plt.savefig('results/curva_roc_isolation_forest_3500.png', dpi=300)

# >>>> Depois exibe normalmente
plt.show()
