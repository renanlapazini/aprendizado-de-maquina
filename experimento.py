"""Avaliação 2 - Classificação supervisionada no dataset Heart Disease (Cleveland/UCI).

Uso: python experimento.py
Gera: dados/*.csv (pré-processados), resultados/ (log, tabelas, gráficos), modelos/ (.joblib)
"""
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Arial"
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")  # precisão indefinida (=0) em folds sem predição da classe 4
BASE = Path(__file__).parent
DADOS, RES, MOD = BASE / "dados", BASE / "resultados", BASE / "modelos"
RES.mkdir(exist_ok=True); MOD.mkdir(exist_ok=True)

COLUNAS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
           "exang", "oldpeak", "slope", "ca", "thal", "num"]
CATEGORICOS = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal", "num"]
ALGORITMOS = {
    "Árvore de Decisão": DecisionTreeClassifier(random_state=42),
    "Naive Bayes": GaussianNB(),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
}
log = open(RES / "log.txt", "w", encoding="utf-8")
def out(*a):
    print(*a); print(*a, file=log)

# ---------- 1. Caracterização ----------
df = pd.read_csv(DADOS / "processed.cleveland.data", names=COLUNAS, na_values="?")
out(f"Instâncias: {len(df)} | Atributos: {df.shape[1]} (13 preditores + classe 'num')\n")
linhas = []
for c in df.columns:
    tipo = "categórico" if c in CATEGORICOS else "numérico"
    if tipo == "numérico":
        valores = f"{df[c].min():g} a {df[c].max():g}"
    else:
        valores = "{" + ", ".join(f"{v:g}" for v in sorted(df[c].dropna().unique())) + "}"
    linhas.append([c, tipo, valores, int(df[c].isna().sum())])
carac = pd.DataFrame(linhas, columns=["atributo", "tipo", "valores", "faltantes"])
carac.to_csv(RES / "caracterizacao.csv", index=False)
out(carac.to_string(index=False))

razao = {c: df[c].value_counts().max() / df[c].value_counts().min() for c in CATEGORICOS}
mais_desb = max(razao, key=razao.get)
out(f"\nAtributo mais desbalanceado (maior/menor classe): {mais_desb} = {razao[mais_desb]:.1f}x")
out(df[mais_desb].value_counts().to_string())
out("\nDistribuição da classe 'num':\n" + df["num"].value_counts().sort_index().to_string())

# ---------- 2. Pré-processamento ----------
# Comum: imputação dos 6 valores faltantes (ca, thal) pela moda.
for c in ["ca", "thal"]:
    df[c] = df[c].fillna(df[c].mode()[0])
multi = df.copy()                                   # Variação A: classe original 0-4
bina = df.copy(); bina["num"] = (bina["num"] > 0).astype(int)  # Variação B: 0=ausente, 1=presente
multi.to_csv(DADOS / "heart_multiclasse.csv", index=False)
bina.to_csv(DADOS / "heart_binario.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
multi["num"].value_counts().sort_index().plot.bar(ax=ax[0], color="#4C72B0", title="A) Classe 'num' (0-4)")
bina["num"].value_counts().sort_index().plot.bar(ax=ax[1], color="#DD8452", title="B) Classe binária")
for a in ax: a.set_xlabel(""); a.set_ylabel("instâncias"); a.tick_params(axis="x", rotation=0)
plt.tight_layout(); plt.savefig(RES / "fig_classes.png", dpi=120); plt.close()

# ---------- 3. Experimentos (validação cruzada estratificada 10-fold) ----------
cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
metricas = {"accuracy": "Acurácia", "precision_macro": "Precisão", "recall_macro": "Recall",
            "f1_macro": "F-Measure"}
todas = []
for nome_var, dados in [("A - multiclasse", multi), ("B - binário", bina)]:
    X, y = dados.drop(columns="num"), dados["num"]
    out(f"\n===== Variação {nome_var} =====")
    linhas = []
    for nome, modelo in ALGORITMOS.items():
        r = cross_validate(modelo, X, y, cv=cv, scoring=list(metricas), return_train_score=True)
        linha = {"Variação": nome_var, "Algoritmo": nome}
        linha.update({rot: r[f"test_{m}"].mean() for m, rot in metricas.items()})
        # Tempo: média do treino nos 10 folds (mais estável que uma única medição)
        linha["Tempo treino (s)"] = r["fit_time"].mean()
        # Acurácia nos próprios dados de treino de cada fold (comparada à de teste, indica sobreajuste)
        linha["Acurácia treino"] = r["train_accuracy"].mean()
        modelo.fit(X, y)  # modelo final, treinado com a base completa, salvo em modelos/
        linhas.append(linha)
    tab = pd.DataFrame(linhas)
    out(tab.drop(columns="Variação").round(3).to_string(index=False))
    todas.append(tab)
    joblib.dump(ALGORITMOS, MOD / f"modelos_{nome_var[0]}.joblib")

    melhor = tab.loc[tab["F-Measure"].idxmax(), "Algoritmo"]
    pred = cross_val_predict(ALGORITMOS[melhor], X, y, cv=cv)
    out(f"\nDesempenho por classe - {melhor} (melhor F-Measure):")
    out(classification_report(y, pred, digits=3, zero_division=0))

res = pd.concat(todas)
res.round(3).to_csv(RES / "resultados.csv", index=False)
piv = res.pivot(index="Algoritmo", columns="Variação", values="F-Measure")
piv.plot.bar(figsize=(9, 3.2), rot=0)
plt.ylim(0, 1.15); plt.xlabel(""); plt.legend(loc="upper center", ncol=2); plt.tight_layout(); plt.savefig(RES / "fig_f1.png", dpi=120); plt.close()
log.close()
