"""
Exportação Excel — Auditoria de Segurança Finaud.
Layout profissional, paleta azul.
"""
import io
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ── Paleta ────────────────────────────────────────────────────────────────────
NAVY       = "1A3A6B"
BLUE       = "2563EB"
BLUE_DIM   = "1E4FC2"
BLUE_LIGHT = "DBEAFE"
BLUE_MID   = "BFDBFE"
WHITE      = "FFFFFF"
GRAY_H     = "F1F5F9"
GRAY_L     = "F8FAFC"
BORDER_C   = "CBD5E1"
TEXT_DARK  = "0F172A"
TEXT_MED   = "334155"
TEXT_MUTED = "64748B"

OK_BG  = "DCFCE7"; OK_FG  = "15803D"
WN_BG  = "FEF9C3"; WN_FG  = "A16207"
BD_BG  = "FEE2E2"; BD_FG  = "B91C1C"
INFO_BG = "EFF6FF"; INFO_FG = "1D4ED8"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)

def _font(bold=False, color=TEXT_DARK, size=10, italic=False) -> Font:
    return Font(name="Calibri", bold=bold, color=color, size=size, italic=italic)

def _side(style="thin", color=BORDER_C) -> Side:
    return Side(style=style, color=color)

def _border(all=True, bottom_only=False, color=BORDER_C) -> Border:
    s = _side(color=color)
    if bottom_only:
        return Border(bottom=s)
    return Border(left=s, right=s, top=s, bottom=s)

def _align(h="left", v="center", wrap=False) -> Alignment:
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap, indent=0)

def _spacer(ws, row: int, height=8) -> None:
    ws.row_dimensions[row].height = height

def _section_title(ws, row: int, text: str, col_span="A:H") -> None:
    ws.merge_cells(f"A{row}:{col_span.split(':')[1]}{row}")
    c = ws.cell(row=row, column=1, value=text.upper())
    c.font = _font(bold=True, color=NAVY, size=9)
    c.fill = _fill(BLUE_LIGHT)
    c.alignment = _align("left", "center")
    c.border = Border(
        left=_side("medium", NAVY),
        bottom=_side("thin", BLUE_MID),
        top=_side("thin", BLUE_MID),
        right=_side("thin", BLUE_MID),
    )
    ws.row_dimensions[row].height = 20

def _header_row(ws, row: int, cols: list[str]) -> None:
    for i, text in enumerate(cols, 1):
        c = ws.cell(row=row, column=i, value=text)
        c.fill = _fill(NAVY)
        c.font = _font(bold=True, color=WHITE, size=9)
        c.alignment = _align("center", "center", wrap=True)
        c.border = _border(color="1E3A5F")
    ws.row_dimensions[row].height = 30

def _status_fill(val: int, hi=0, med=5) -> tuple[str, str]:
    if val <= hi:   return OK_BG, OK_FG
    if val <= med:  return WN_BG, WN_FG
    return BD_BG, BD_FG

def _sev_label(s: str) -> str:
    return {"alto":"Alto","médio":"Médio","baixo":"Baixo",
            "high":"Alto","medium":"Médio","low":"Baixo"}.get(s.lower(), s.capitalize())

# ── Cabeçalho de aba ──────────────────────────────────────────────────────────

def _add_header(ws, logo_path, title: str, subtitle: str,
                last_col="H", n_merge_cols=8) -> int:
    """Insere cabeçalho com logo e retorna a próxima linha livre."""
    ws.row_dimensions[1].height = 52

    # Coluna A — fundo navy reservado para o logo
    ws["A1"].fill = _fill(NAVY)

    # Logo pequeno ancorado em A1 (não cobre o texto)
    if logo_path and logo_path.exists():
        try:
            img = XLImage(str(logo_path))
            img.height = 40
            img.width  = 40
            img.anchor = "A1"
            ws.add_image(img)
        except Exception:
            pass

    # Colunas B:last_col — título
    ws.merge_cells(f"B1:{last_col}1")
    c = ws["B1"]
    c.fill = _fill(NAVY)
    c.font = _font(bold=True, color=WHITE, size=15)
    c.alignment = _align("left", "center")
    c.value = f"  {title}"

    # Linha 2 — subtítulo (A:last_col inteiro)
    ws.row_dimensions[2].height = 22
    ws.merge_cells(f"A2:{last_col}2")
    s = ws["A2"]
    s.fill  = _fill(BLUE_LIGHT)
    s.font  = _font(color=NAVY, size=9, italic=True)
    s.alignment = _align("left", "center")
    s.value = f"  {subtitle}"
    s.border = Border(bottom=_side("thin", BLUE_MID))

    # Linha 3 — espaçador
    _spacer(ws, 3, 10)
    return 4  # próxima linha

# ── Aba 1 — Resumo ────────────────────────────────────────────────────────────

def _aba_resumo(wb: Workbook, summary: dict, logo_path) -> None:
    ws = wb.active
    ws.title = "Resumo"
    ws.sheet_view.showGridLines = False

    # Larguras — A-F: 6 colunas dos KPIs; G: espaçador; H-M: tabela/gráfico auxiliar
    widths = {"A":18,"B":18,"C":18,"D":18,"E":18,"F":18,"G":3,
              "H":26,"I":8,"J":8,"K":10,"L":10,"M":10}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    next_row = _add_header(
        ws, logo_path,
        "Auditoria de Segurança",
        f"Gerado em {summary['generated_at']}   ·   {summary['total_projects']} projetos analisados   ·   Confidencial — uso interno",
    )

    # ── Seção KPIs ──
    _section_title(ws, next_row, "Indicadores principais", "A:F")
    next_row += 1
    _spacer(ws, next_row, 6); next_row += 1

    kpis = [
        ("CVEs em\nbibliotecas",        summary["total_cves"],      _status_fill(summary["total_cves"])),
        ("Problemas no\ncódigo (SAST)",  summary["total_sast"],      _status_fill(summary["total_sast"], med=5)),
        ("Segredos\nno git",             summary["secrets_git"],     _status_fill(summary["secrets_git"])),
        ("Segredos\nno disco",           summary["secrets_disk"],    _status_fill(summary["secrets_disk"], med=10)),
        ("Licenças\nrestritivas",        summary["total_licenses"],  _status_fill(summary["total_licenses"])),
        ("Projetos\nlimpos",             summary["clean_projects"],
         (INFO_BG, INFO_FG)),
    ]

    # Linha de valores
    ws.row_dimensions[next_row].height = 44
    for i, (label, val, (bg, fg)) in enumerate(kpis, 1):
        c = ws.cell(row=next_row, column=i, value=val)
        c.font = Font(name="Calibri", bold=True, size=24, color=fg)
        c.fill = _fill(bg)
        c.alignment = _align("center", "center")
        c.border = _border(color=BORDER_C)

    next_row += 1

    # Linha de labels
    ws.row_dimensions[next_row].height = 34
    for i, (label, _, (bg, fg)) in enumerate(kpis, 1):
        c = ws.cell(row=next_row, column=i, value=label)
        c.font = _font(bold=True, size=9, color=TEXT_MED)
        c.fill = _fill(GRAY_H)
        c.alignment = _align("center", "center", wrap=True)
        c.border = _border(color=BORDER_C)

    next_row += 1
    _spacer(ws, next_row, 14); next_row += 1

    # ── Glossário ──
    _section_title(ws, next_row, "Glossário — o que significa cada indicador", "A:F")
    next_row += 1
    _spacer(ws, next_row, 6); next_row += 1

    gloss = [
        ("CVE",              "Falha de segurança registrada publicamente em uma biblioteca. Pode ser explorada para acessar ou comprometer o sistema."),
        ("SAST",             "Análise estática do código-fonte. Identifica padrões de risco: senhas no código, comandos inseguros ou funções inadequadas."),
        ("Segredo no git",   "Senha, token ou chave secreta commitada no repositório. Mesmo deletando o arquivo, permanece no histórico git."),
        ("Segredo no disco", "Arquivo local com credenciais (.env, config…). Não está no repositório — comportamento correto, mas deve ser protegido."),
        ("Licença restritiva","GPL e AGPL exigem que o código que as usa seja publicado como código aberto — incompatível com produto comercial."),
        ("# nosec",          f"Trechos com riscos já avaliados e documentados como falsos positivos ({summary.get('total_suprimidos', 0)} ocorrências)."),
    ]

    for term, expl in gloss:
        ws.row_dimensions[next_row].height = 22
        ct = ws.cell(row=next_row, column=1, value=term)
        ct.font = _font(bold=True, size=9, color=NAVY)
        ct.fill = _fill(GRAY_L)
        ct.alignment = _align("left", "center")
        ct.border = _border(color=BORDER_C)

        ce = ws.cell(row=next_row, column=2, value=expl)
        ce.font = _font(size=9, color=TEXT_MED)
        ce.alignment = _align("left", "center", wrap=True)
        ce.fill = _fill(WHITE)
        ce.border = _border(color=BORDER_C)
        ws.merge_cells(f"B{next_row}:F{next_row}")
        next_row += 1

    _spacer(ws, next_row, 14); next_row += 1

    # ── Gráfico (posicionado à direita dos KPIs, coluna H linha 4) ──
    projs = [p for p in summary["projects"]
             if sum([p["cves"],p["sast"],p["secrets_git"],p["secrets_disk"],p["licenses"]]) > 0]
    projs.sort(key=lambda p: sum([p["cves"],p["sast"],p["secrets_git"],p["secrets_disk"],p["licenses"]]), reverse=True)
    top = projs[:6]

    if top:
        # Tabela de dados auxiliar: colunas H-M, a partir da linha 5 (logo abaixo do cabeçalho)
        chart_data_row = 5
        chart_cols_start = 8   # coluna H

        # Linha de cabeçalho da tabela auxiliar
        for ci, label in enumerate(["Projeto","CVEs","SAST","Seg. git","Seg. disco","Licenças"], chart_cols_start):
            c = ws.cell(row=chart_data_row, column=ci, value=label)
            c.fill = _fill(NAVY)
            c.font = _font(bold=True, color=WHITE, size=8)
            c.alignment = _align("center", "center")
            c.border = _border(color="1E3A5F")
        ws.row_dimensions[chart_data_row].height = 18

        n = len(top)
        for ri, p in enumerate(top):
            row = chart_data_row + 1 + ri
            ws.row_dimensions[row].height = 16
            for ci, val in enumerate([p["name"],p["cves"],p["sast"],p["secrets_git"],p["secrets_disk"],p["licenses"]], chart_cols_start):
                c = ws.cell(row=row, column=ci, value=val)
                c.font = _font(size=8)
                c.fill = _fill(GRAY_L if ri % 2 == 0 else WHITE)
                c.border = _border(color=BORDER_C)
                c.alignment = _align("center" if ci > chart_cols_start else "left")

        # Título da seção do gráfico (coluna H)
        col_h_letter = get_column_letter(chart_cols_start)
        col_m_letter = get_column_letter(chart_cols_start + 5)

        chart = BarChart()
        chart.type = "bar"
        chart.grouping = "stacked"
        chart.title = "Achados por projeto — top " + str(n)
        chart.style = 26
        chart.width = 20
        chart.height = 13
        chart.x_axis.numFmt = "0"
        chart.x_axis.title = "Quantidade de achados"
        chart.y_axis.title = None          # nomes dos projetos já aparecem nas barras
        chart.legend.position = "b"

        data_ref = Reference(ws,
            min_col=chart_cols_start + 1, min_row=chart_data_row,
            max_col=chart_cols_start + 5, max_row=chart_data_row + n)
        cats = Reference(ws,
            min_col=chart_cols_start, min_row=chart_data_row + 1,
            max_row=chart_data_row + n)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats)

        # Ancora o gráfico abaixo da tabela auxiliar (linha chart_data_row + n + 2)
        chart_anchor_row = chart_data_row + n + 2
        ws.add_chart(chart, f"{col_h_letter}{chart_anchor_row}")

# ── Aba 2 — Por projeto ───────────────────────────────────────────────────────

def _aba_projetos(wb: Workbook, summary: dict, logo_path) -> None:
    ws = wb.create_sheet("Por Projeto")
    ws.sheet_view.showGridLines = False

    for col, w in zip("ABCDEFGH", [32,36,10,10,14,16,12,18]):
        ws.column_dimensions[col].width = w

    next_row = _add_header(ws, logo_path,
        "Situação por Projeto",
        f"Gerado em {summary['generated_at']}   ·   verde = limpo   ·   amarelo = monitorar   ·   vermelho = ação necessária",
    )
    _spacer(ws, next_row, 6); next_row += 1

    _header_row(ws, next_row,
        ["Projeto","O que é","CVEs","Código\n(SAST)","Segredo\nno git","Segredo\nno disco","Licença","Status"])
    next_row += 1

    for i, p in enumerate(summary["projects"]):
        total = p["cves"]+p["sast"]+p["secrets_git"]+p["secrets_disk"]+p["licenses"]
        if total == 0:
            status, s_bg, s_fg = "✔ Limpo",      OK_BG,  OK_FG
        elif p["secrets_git"] > 0 or p["cves"] > 0:
            status, s_bg, s_fg = "⚠ Ação urgente", BD_BG, BD_FG
        else:
            status, s_bg, s_fg = "● Monitorar",   WN_BG,  WN_FG

        row_bg = GRAY_L if i % 2 == 0 else WHITE
        ws.row_dimensions[next_row].height = 22

        cn = ws.cell(next_row, 1, p["name"])
        cn.font = _font(bold=True, size=10, color=NAVY)
        cn.fill = _fill(row_bg)
        cn.border = _border(color=BORDER_C)

        cd = ws.cell(next_row, 2, p.get("description",""))
        cd.font = _font(size=9, color=TEXT_MUTED, italic=True)
        cd.fill = _fill(row_bg)
        cd.border = _border(color=BORDER_C)
        cd.alignment = _align("left", "center", wrap=True)

        for col_idx, val, (bg, fg) in [
            (3, p["cves"],         _status_fill(p["cves"])),
            (4, p["sast"],         _status_fill(p["sast"], med=5)),
            (5, p["secrets_git"],  _status_fill(p["secrets_git"])),
            (6, p["secrets_disk"], _status_fill(p["secrets_disk"], med=10)),
            (7, p["licenses"],     _status_fill(p["licenses"])),
        ]:
            c = ws.cell(next_row, col_idx, val)
            c.fill  = _fill(bg)
            c.font  = _font(bold=True, size=10, color=fg)
            c.alignment = _align("center")
            c.border = _border(color=BORDER_C)

        cs = ws.cell(next_row, 8, status)
        cs.fill = _fill(s_bg)
        cs.font = _font(bold=True, size=9, color=s_fg)
        cs.alignment = _align("center")
        cs.border = _border(color=BORDER_C)

        next_row += 1

# ── Aba 3 — Achados detalhados ────────────────────────────────────────────────

TYPE_LABELS = {
    "cve":         "CVE — Biblioteca",
    "sast":        "Código (SAST)",
    "secret_git":  "Segredo no git",
    "secret_disk": "Segredo no disco",
    "license":     "Licença restritiva",
}
TYPE_COLORS = {
    "cve":         (BD_BG, BD_FG),
    "sast":        (WN_BG, WN_FG),
    "secret_git":  (BD_BG, BD_FG),
    "secret_disk": (WN_BG, WN_FG),
    "license":     (WN_BG, WN_FG),
}

def _aba_achados(wb: Workbook, summary: dict, logo_path) -> None:
    ws = wb.create_sheet("Achados Detalhados")
    ws.sheet_view.showGridLines = False

    for col, w in zip("ABCDEFG", [26,18,12,36,42,42,30]):
        ws.column_dimensions[col].width = w

    next_row = _add_header(ws, logo_path,
        "Achados Detalhados",
        f"Gerado em {summary['generated_at']}   ·   ordenado por gravidade",
        last_col="G",
    )
    _spacer(ws, next_row, 6); next_row += 1

    _header_row(ws, next_row,
        ["Projeto","Tipo","Gravidade","O que foi encontrado",
         "O que significa","O que fazer","Arquivo / Detalhe"])
    next_row += 1

    findings = summary.get("findings", [])
    ORDER = {"alto":0,"high":0,"médio":1,"medium":1,"baixo":2,"low":2}
    findings_sorted = sorted(findings,
        key=lambda f: (ORDER.get(f.get("severity","").lower(), 9), f.get("project","")))

    for i, f in enumerate(findings_sorted):
        t   = f.get("type","")
        sev = f.get("severity","médio")
        bg, fg  = TYPE_COLORS.get(t, (WN_BG, WN_FG))
        sev_bg  = BD_BG if sev in ("alto","high") else WN_BG if sev in ("médio","medium") else OK_BG
        sev_fg  = BD_FG if sev in ("alto","high") else WN_FG if sev in ("médio","medium") else OK_FG
        row_bg  = GRAY_L if i % 2 == 0 else WHITE

        ws.row_dimensions[next_row].height = 42

        for col, val, extra_bg, extra_fg in [
            (1, f.get("project",""),               row_bg,  TEXT_DARK),
            (4, f.get("title",""),                 row_bg,  TEXT_MED),
            (5, f.get("meaning",""),               row_bg,  TEXT_MED),
            (6, f.get("action",""),                row_bg,  NAVY),
            (7, f.get("file","") or f.get("detail",""), row_bg, TEXT_MUTED),
        ]:
            c = ws.cell(next_row, col, val)
            c.font = _font(size=9, color=extra_fg,
                           bold=(col==1), italic=(col==7))
            c.fill = _fill(extra_bg)
            c.alignment = _align("left", "top", wrap=True)
            c.border = _border(color=BORDER_C)

        ct = ws.cell(next_row, 2, TYPE_LABELS.get(t, t))
        ct.fill = _fill(bg); ct.font = _font(bold=True, size=9, color=fg)
        ct.alignment = _align("center", "top"); ct.border = _border(color=BORDER_C)

        cs = ws.cell(next_row, 3, _sev_label(sev))
        cs.fill = _fill(sev_bg); cs.font = _font(bold=True, size=9, color=sev_fg)
        cs.alignment = _align("center", "top"); cs.border = _border(color=BORDER_C)

        next_row += 1

    if not findings_sorted:
        ws.row_dimensions[next_row].height = 30
        ws.merge_cells(f"A{next_row}:G{next_row}")
        c = ws.cell(next_row, 1, "✔  Nenhum achado ativo — todos os projetos estão limpos!")
        c.font = _font(bold=True, color=OK_FG, size=11)
        c.fill = _fill(OK_BG); c.alignment = _align("center")
        c.border = _border(color=BORDER_C)

# ── Aba 4 — Histórico ─────────────────────────────────────────────────────────

def _aba_historico(wb: Workbook, history: list[dict], summary: dict, logo_path) -> None:
    ws = wb.create_sheet("Histórico")
    ws.sheet_view.showGridLines = False

    for col, w in zip("ABCDEFGH", [22,12,12,14,16,14,18,18]):
        ws.column_dimensions[col].width = w

    next_row = _add_header(ws, logo_path,
        "Histórico de Auditorias",
        "Evolução ao longo do tempo — cada linha é uma auditoria rodada",
    )
    _spacer(ws, next_row, 6); next_row += 1

    _header_row(ws, next_row,
        ["Data","CVEs","SAST","Seg. git","Seg. disco","Licenças","Proj. limpos","Total proj."])
    next_row += 1
    data_start = next_row

    for i, h in enumerate(reversed(history)):
        is_latest = (i == 0)
        ws.row_dimensions[next_row].height = 22
        row_bg = BLUE_LIGHT if is_latest else (GRAY_L if i % 2 == 0 else WHITE)

        vals = [h.get("generated_at",""), h.get("total_cves",0), h.get("total_sast",0),
                h.get("secrets_git",0), h.get("secrets_disk",0), h.get("total_licenses",0),
                h.get("clean_projects",0), h.get("total_projects",0)]

        for col, v in enumerate(vals, 1):
            c = ws.cell(next_row, col, v)
            c.font = _font(bold=is_latest, size=10,
                           color=NAVY if is_latest else TEXT_MED)
            c.fill = _fill(row_bg)
            c.border = _border(color=BORDER_C)
            c.alignment = _align("center" if col > 1 else "left")

        next_row += 1

    # Gráfico de linha
    if len(history) >= 2:
        _spacer(ws, next_row, 14); next_row += 1
        data_end = data_start + len(history) - 1
        chart = LineChart()
        chart.title = "Evolução de achados por auditoria"
        chart.style = 26
        chart.width = 24; chart.height = 12
        chart.y_axis.title = "Quantidade de achados"
        chart.x_axis.title = "Data da auditoria"
        chart.legend.position = "b"

        cats    = Reference(ws, min_col=1, min_row=data_start, max_row=data_end)
        data_ref = Reference(ws, min_col=2, min_row=data_start-1, max_col=6, max_row=data_end)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats)
        ws.add_chart(chart, f"A{next_row}")

# ── Ponto de entrada ──────────────────────────────────────────────────────────

def gerar_excel(summary_path: Path, history_path: Path, logo_path=None) -> bytes:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    history: list[dict] = []
    if history_path and history_path.exists():
        try:
            history = json.loads(history_path.read_text(encoding="utf-8"))
        except Exception:
            history = [summary]
    else:
        history = [summary]

    wb = Workbook()
    _aba_resumo(wb, summary, logo_path)
    _aba_projetos(wb, summary, logo_path)
    _aba_achados(wb, summary, logo_path)
    _aba_historico(wb, history, summary, logo_path)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
