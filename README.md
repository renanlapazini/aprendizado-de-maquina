# Avaliação 2 – Aprendizado de Máquina (Heart Disease / UCI)

Classificação de doença cardíaca (atributo `num`) com Árvore de Decisão, Naive Bayes e Random Forest.

| Pasta / arquivo | Conteúdo |
|---|---|
| `dados/processed.cleveland.data` | dataset original ([UCI](https://archive.ics.uci.edu/dataset/45/heart+disease)) |
| `dados/heart_multiclasse.csv`, `dados/heart_binario.csv` | datasets pré-processados (variações A e B) |
| `experimento.py` | caracterização, pré-processamento e experimentos |
| `resultados/` | log, tabelas (CSV) e gráficos |
| `modelos/` | modelos treinados (`joblib`) |
| `relatorio.md` / `relatorio.pdf` | relatório |

```
pip install -r requirements.txt
python experimento.py
python gerar_pdf.py
```
