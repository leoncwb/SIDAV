import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc

# Valores da matriz de confusão que obtivemos
y_true = [0] * 70 + [1] * 30  # 70 normais, 30 anômalos
# Simulando as probabilidades (normal: baixa probabilidade de ser anômalo, anômalo: alta probabilidade)
y_scores = np.concatenate([np.random.uniform(0, 0.3, 70), np.random.uniform(0.7, 1, 30)])

# Plotar curva ROC
fpr, tpr, thresholds = roc_curve(y_true, y_scores)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taxa de Falsos Positivos')
plt.ylabel('Taxa de Verdadeiros Positivos')
plt.title('Curva ROC - Isolation Forest (VoIP)')
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()

# Salvar figura
plt.savefig("curva_roc_isolation_forest.png")
print("✅ Curva ROC salva como curva_roc_isolation_forest.png")
