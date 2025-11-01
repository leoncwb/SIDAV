import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt

# Ler o dataset
df = pd.read_csv('results/dataset_chamadas_com_metricas.csv')

# Aplicar a regra simples
def regra_simples(row):
    if row['duracao_segundos'] < 8 or row['jitter_ms'] > 80:
        return 1  # Anomalia
    else:
        return 0  # Normal

df['pred_regra'] = df.apply(regra_simples, axis=1)
y_true = df['status'].apply(lambda x: 1 if x == 'Chamada_Curta' else 0)  # 1 = Anomalia, 0 = Normal
y_pred = df['pred_regra']

# Matriz de Confusão
print("Matriz de Confusão - Regra Simples:")
print(confusion_matrix(y_true, y_pred))

# Relatório
print("\nRelatório:")
print(classification_report(y_true, y_pred, target_names=["Normal", "Anomalia"]))

# Gerar Curva ROC
fpr, tpr, thresholds = roc_curve(y_true, y_pred)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f'ROC curve (área = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel('Taxa de Falsos Positivos (FPR)')
plt.ylabel('Taxa de Verdadeiros Positivos (TPR)')
plt.title('Curva ROC - Regras Simples (3500 chamadas)')
plt.legend(loc="lower right")
plt.grid()
plt.savefig('results/curva_roc_regra_simples.png')  # <-- Salvar o gráfico automaticamente
plt.show()
