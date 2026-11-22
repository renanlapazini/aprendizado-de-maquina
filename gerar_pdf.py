"""Converte relatorio.md em relatorio.pdf no padrão ABNT (usa o Microsoft Edge em modo headless)."""
import re
import subprocess
from pathlib import Path

import markdown

BASE = Path(__file__).parent.resolve()
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CAPA = """<div class="capa">
<div><b>UNIVERSIDADE FEEVALE</b><br><br>Iago Mauri<br>Renan Lapazini</div>
<div><b>APRENDIZADO DE MÁQUINA: CLASSIFICAÇÃO DE DOENÇA CARDÍACA</b></div>
<div>Novo Hamburgo<br>2026</div></div>"""
# ABNT NBR 14724: A4, margens sup./esq. 3 cm e inf./dir. 2 cm, Arial 12, entrelinha 1,5,
# recuo de parágrafo 1,25 cm, legendas/fontes/tabelas em tamanho menor (10),
# página contada desde a capa e numerada no canto superior direito a partir do texto.
CSS = """@page{size:A4;margin:30mm 20mm 20mm 30mm;
  @top-right{content:counter(page);font:10pt Arial,sans-serif;vertical-align:bottom;padding-bottom:10mm}}
@page:first{@top-right{content:none}}
@counter-style alinea{system:extends lower-alpha;suffix:") "}
body{font-family:Arial,sans-serif;font-size:12pt;line-height:1.5;text-align:justify;margin:0}
.capa{height:245mm;display:flex;flex-direction:column;justify-content:space-between;text-align:center;
  break-after:page}
p{margin:0;text-indent:12.5mm}
h1,h2{font-size:12pt;font-weight:bold;text-transform:uppercase;margin:18pt 0;break-after:avoid}
h1{text-align:center}
h1~p{text-align:left;text-indent:0;line-height:1;margin-bottom:12pt}
ol{margin:0;padding-left:18mm;list-style-type:alinea}
.tit,.fonte{font-size:10pt;line-height:1.2;text-indent:0;text-align:left}
.tit{margin-top:12pt;margin-bottom:4pt;break-after:avoid}
.fonte{margin-top:4pt;margin-bottom:12pt;break-before:avoid}
table{border-collapse:collapse;width:100%;font-size:10pt;line-height:1.2;break-inside:avoid;
  border-top:1px solid #000;border-bottom:1px solid #000}
th{border-bottom:1px solid #000;text-align:left} th,td{padding:2pt 3pt;white-space:nowrap}
p:has(img){text-indent:0;line-height:1;break-inside:avoid} img{width:100%;display:block}
:is(th,td):nth-child(5):nth-last-child(4){border-left:1px solid #000}
code{font-family:inherit;font-style:italic} a{color:inherit;text-decoration:none;word-break:break-all}"""

html = markdown.markdown((BASE / "relatorio.md").read_text(encoding="utf-8"), extensions=["tables"])
html = re.sub(r"<p>((?:Tabela|Figura) \d+ –)", r'<p class="tit">\1', html)
html = html.replace("<p>Fonte:", '<p class="fonte">Fonte:')
tmp = BASE / "_relatorio.html"
tmp.write_text(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{CAPA}{html}</body></html>",
               encoding="utf-8")
subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={BASE / 'relatorio.pdf'}", tmp.as_uri()], check=True)
tmp.unlink()
print("relatorio.pdf gerado")
