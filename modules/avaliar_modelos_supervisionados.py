import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Carregar o dataset correto
df = pd.read_csv('modules/results/dataset_chamadas_com_metricas.csv')

# Renomear colunas caso necessário (baseado na visualização que você mostrou)
df.columns = ['chamada', 'bitrate_mbps', 'status', 'jitter_ms', 'latencia_ms']

# Preparar os dados
X = df[['bitrate_mbps', 'jitter_ms', 'latencia_ms']]
y = df['status'].apply(lambda x: 0 if 'Sucesso' in x else 1)  # 0 = normal, 1 = anomalia

# Dividir em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Padronizar os dados
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

def avaliar_modelo(nome, modelo, X_train, X_test):
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    y_prob = modelo.predict_proba(X_test)[:, 1] if hasattr(modelo, "predict_proba") else y_pred
    print(f"\nModelo: {nome}")
    print("Acurácia:", round(accuracy_score(y_test, y_pred) * 100, 2))
    print("Precisão:", round(precision_score(y_test, y_pred) * 100, 2))
    print("Recall:", round(recall_score(y_test, y_pred) * 100, 2))
    print("F1-Score:", round(f1_score(y_test, y_pred) * 100, 2))
    print("AUC:", round(roc_auc_score(y_test, y_prob) * 100, 2))

# Avaliar Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
avaliar_modelo("Random Forest", rf, X_train_scaled, X_test_scaled)

# Avaliar SVM com kernel RBF
svm = SVC(kernel='rbf', probability=True, random_state=42)
avaliar_modelo("SVM (RBF)", svm, X_train_scaled, X_test_scaled)
