"""
Exportação Excel da auditoria de segurança — 4 abas.
"""
import io
import json
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import (Alignment, Border, Font, GradientFill,
                              PatternFill, Side)
from openpyxl.utils import get_column_letter

# ── Cores ─────────────────────────────────────────────────────────────────────

GREEN  = "1F7244"
WHITE  = "FFFFFF"
GRAY_H = "F2F2F2"
GRAY_L = "FAFAFA"
RED    = "C0392B"
AMBER  = "D68910"
BLUE   = "1A5276"
GREEN2 = "1E8449"
LIGHT_RED   = "FADBD8"
LIGHT_AMBER = "FEF9E7"
LIGHT_GREEN = "D5F5E3"
LIGHT_BLUE  = "D6EAF8"

def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)

def _font(bold=False, color="000000", size=11, italic=False) -> Font:
    return Font(bold=bold, color=color, size=size, italic=italic)

def _border_thin() -> Border:
    side = Side(style="thin", color="CCCCCC")
    return Border(left=side, right=side, top=side, bottom=side)

def _align(h="left", v="center", wrap=False) -> Alignment:
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def _header_row(ws, row: int, cols: list[str], fill_color=GREEN) -> None:
    for col_idx, text in enumerate(cols, 1):
        c = ws.cell(row=row, column=col_idx, value=text)
        c.fill = _fill(fill_color)
        c.font = _font(bold=True, color=WHITE, size=10)
        c.alignment = _align("center")
        c.border = _border_thin()

def _status_fill(val: int, thresholds=(0, 1, 5)) -> tuple[str, str]:
    if val == 0:
        return LIGHT_GREEN, GREEN2
    if val <= thresholds[1]:
        return LIGHT_AMBER, AMBER
    return LIGHT_RED, RED

def _severity_label(s: str) -> str:
    return {"alto": "Alto", "médio": "Médio", "baixo": "Baixo",
            "medium": "Médio", "high": "Alto", "low": "Baixo"}.get(s.lower(), s.capitalize())

# ── Cabeçalho com logo ────────────────────────────────────────────────────────

def _add_logo_header(ws, logo_path: Path | None, title: str, subtitle: str) -> None:
    ws.row_dimensions[1].height = 50
    ws.merge_cells("A1:H1")
    header = ws["A1"]
    header.value = f"  Finaud — {title}"
    header.font = _font(bold=True, color=WHITE, size=14)
    header.fill = _fill(GREEN)
    header.alignment = _align("left", "center")

    ws.merge_cells("A2:H2")
    sub = ws["A2"]
    sub.value = f"  {subtitle}"
    sub.font = _font(color="555555", size=10, italic=True)
    sub.fill = _fill("F9F9F9")
    sub.alignment = _align("left", "center")
    ws.row_dimensions[2].height = 20

    if logo_path and logo_path.exists():
        try:
            img = XLImage(str(logo_path))
            img.height = 36
            img.width = 120
            img.anchor = "A1"
            ws.add_image(img)
        except Exception:
            pass

# ── Aba 1 — Resumo executivo ──────────────────────────────────────────────────

def _aba_resumo(wb: Workbook, summary: dict, logo_path: Path | None) -> None:
    ws = wb.active
    ws.title = "Resumo"
    ws.column_dimensions["A"].width = 28
    for col in "BCDEFGH":
        ws.column_dimensions[col].width = 18

    _add_logo_header(ws, logo_path, "Auditoria de Segurança",
                     f"Gerado em {summary['generated_at']}  ·  {summary['total_projects']} projetos analisados  ·  Confidencial — uso interno")

    # KPI cards (row 4-9)
    kpis = [
        ("Falhas em bibliotecas\n(CVEs)", summary["total_cves"],
         "Bibliotecas com falha de segurança conhecida. Se zero, todas estão atualizadas."),
        ("Problemas no código\n(SAST)", summary["total_sast"],
         "Pontos de risco no próprio código-fonte. Se zero, nenhum risco ativo detectado."),
        ("Segredos no repositório\ngit", summary["secrets_git"],
         "Senha/chave commitada no histórico git. Visível para qualquer pessoa com acesso ao repo."),
        ("Segredos só no disco\n(arquivos locais)", summary["secrets_disk"],
         "Arquivos locais com senhas (.env). Não estão no git — comportamento esperado, mas monitorar."),
        ("Licenças\nRestritivas", summary["total_licenses"],
         "Bibliotecas com licença incompatível com uso comercial (GPL, AGPL…)."),
        ("Projetos\nLimpos", summary["clean_projects"],
         f"Projetos sem nenhum achado ativo de {summary['total_projects']} analisados."),
    ]

    ws["A4"] = "INDICADORES PRINCIPAIS"
    ws["A4"].font = _font(bold=True, color="888888", size=9)
    ws.row_dimensions[4].height = 16

    for i, (label, val, note) in enumerate(kpis):
        col = i + 1
        col_l = get_column_letter(col)
        # Value
        c_val = ws.cell(row=5, column=col, value=val)
        c_val.font = Font(bold=True, size=22, color=GREEN2 if val == 0 else (RED if i in (2,) and val > 0 else AMBER if val > 0 else GREEN2))
        c_val.alignment = _align("center", "center")
        c_val.fill = _fill(LIGHT_GREEN if val == 0 else (LIGHT_RED if i == 2 and val > 0 else LIGHT_AMBER if val > 0 else LIGHT_GREEN))
        ws.row_dimensions[5].height = 36
        # Label
        c_lbl = ws.cell(row=6, column=col, value=label)
        c_lbl.font = _font(bold=True, size=9, color="333333")
        c_lbl.alignment = _align("center", "center", wrap=True)
        c_lbl.fill = _fill(GRAY_H)
        ws.row_dimensions[6].height = 32
        # Note
        c_note = ws.cell(row=7, column=col, value=note)
        c_note.font = _font(size=8, color="777777", italic=True)
        c_note.alignment = _align("left", "top", wrap=True)
        c_note.fill = _fill(GRAY_L)
        ws.row_dimensions[7].height = 48

    # Legenda (row 9-11)
    ws.row_dimensions[9].height = 12
    ws["A10"] = "GLOSSÁRIO — O QUE SIGNIFICA CADA ITEM"
    ws["A10"].font = _font(bold=True, color="888888", size=9)
    ws.merge_cells("A10:F10")

    gloss = [
        ("CVE", "Falha de segurança registrada publicamente em uma biblioteca. Pode ser explorada por atacantes para acessar ou comprometer o sistema."),
        ("SAST", "Análise estática do código-fonte. Identifica padrões de risco como senhas no código, comandos inseguros ou uso inadequado de funções."),
        ("Segredo no git", "Uma senha, token ou chave secreta foi commitada no repositório. Mesmo deletando o arquivo, ela permanece no histórico."),
        ("Segredo no disco", "Arquivo local com credenciais (.env, config.json…). Não está no repositório — é o comportamento correto, mas deve ser protegido."),
        ("Licença restritiva", "GPL e AGPL exigem que o código que as usa seja também publicado como código aberto — incompatível com produto comercial."),
        ("# nosec", f"Trechos de código com riscos já avaliados e documentados como falsos positivos ({summary.get('total_suprimidos',0)} ocorrências)."),
    ]
    for j, (term, expl) in enumerate(gloss):
        r = 11 + j
        ws.cell(row=r, column=1, value=term).font = _font(bold=True, size=9, color=GREEN)
        ws.cell(row=r, column=2, value=expl).font = _font(size=9, color="444444")
        ws.merge_cells(f"B{r}:F{r}")
        ws.cell(row=r, column=2).alignment = _align("left", "center", wrap=True)
        ws.row_dimensions[r].height = 22

    # Gráfico de barras — top projetos com achados
    projs_com_achados = [p for p in summary["projects"] if (p["cves"]+p["sast"]+p["secrets_git"]+p["secrets_disk"]+p["licenses"]) > 0]
    projs_com_achados.sort(key=lambda p: p["cves"]+p["sast"]+p["secrets_git"]+p["secrets_disk"]+p["licenses"], reverse=True)
    top5 = projs_com_achados[:6]

    if top5:
        data_row_start = 19
        ws[f"A{data_row_start}"] = "Projeto"
        ws[f"B{data_row_start}"] = "CVEs"
        ws[f"C{data_row_start}"] = "SAST"
        ws[f"D{data_row_start}"] = "Seg. git"
        ws[f"E{data_row_start}"] = "Seg. disco"
        ws[f"F{data_row_start}"] = "Licenças"
        for cell in ws[data_row_start]:
            if cell.value:
                cell.font = _font(bold=True, size=9, color=WHITE)
                cell.fill = _fill(GREEN)
        for i, p in enumerate(top5):
            r = data_row_start + 1 + i
            ws.cell(r, 1, p["name"])
            ws.cell(r, 2, p["cves"])
            ws.cell(r, 3, p["sast"])
            ws.cell(r, 4, p["secrets_git"])
            ws.cell(r, 5, p["secrets_disk"])
            ws.cell(r, 6, p["licenses"])

        chart = BarChart()
        chart.type = "bar"
        chart.grouping = "stacked"
        chart.title = "Achados por projeto (top 6)"
        chart.y_axis.title = "Projeto"
        chart.x_axis.title = "Quantidade"
        chart.style = 10
        chart.width = 22
        chart.height = 12

        n = len(top5)
        cats = Reference(ws, min_col=1, min_row=data_row_start+1, max_row=data_row_start+n)
        for col_idx, label in [(2,"CVEs"),(3,"SAST"),(4,"Seg. git"),(5,"Seg. disco"),(6,"Licenças")]:
            data = Reference(ws, min_col=col_idx, min_row=data_row_start, max_row=data_row_start+n)
            series = chart.series.SeriesConstructor(data, cats, title_from_data=True)
            chart.series.append(series)

        ws.add_chart(chart, "H4")

# ── Aba 2 — Por projeto ───────────────────────────────────────────────────────

def _aba_projetos(wb: Workbook, summary: dict, logo_path: Path | None) -> None:
    ws = wb.create_sheet("Por Projeto")
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 16
    ws.column_dimensions["G"].width = 12
    ws.column_dimensions["H"].width = 18

    _add_logo_header(ws, logo_path, "Situação por projeto",
                     f"Gerado em {summary['generated_at']}  ·  verde = ok  ·  amarelo = atenção  ·  vermelho = ação necessária")

    headers = ["Projeto", "O que é", "CVEs", "Código\n(SAST)", "Segredo\nno git", "Segredo\nno disco", "Licença\nRestritiva", "Status Geral"]
    _header_row(ws, 4, headers)
    ws.row_dimensions[4].height = 32

    for i, p in enumerate(summary["projects"]):
        r = 5 + i
        total = p["cves"] + p["sast"] + p["secrets_git"] + p["secrets_disk"] + p["licenses"]
        if total == 0:
            status, status_color, status_bg = "Limpo", GREEN2, LIGHT_GREEN
        elif p["secrets_git"] > 0 or p["cves"] > 0:
            status, status_color, status_bg = "Ação urgente", RED, LIGHT_RED
        else:
            status, status_color, status_bg = "Monitorar", AMBER, LIGHT_AMBER

        ws.cell(r, 1, p["name"]).font = _font(bold=True, size=10)
        ws.cell(r, 2, p.get("description", "")).font = _font(size=9, color="555555", italic=True)
        ws.cell(r, 2).alignment = _align("left", "center", wrap=True)

        for col_idx, val, (bg, fg) in [
            (3, p["cves"],         _status_fill(p["cves"])),
            (4, p["sast"],         _status_fill(p["sast"])),
            (5, p["secrets_git"],  _status_fill(p["secrets_git"])),
            (6, p["secrets_disk"], _status_fill(p["secrets_disk"], (0,1,10))),
            (7, p["licenses"],     _status_fill(p["licenses"])),
        ]:
            c = ws.cell(r, col_idx, val)
            c.fill = _fill(bg)
            c.font = _font(bold=True, size=10, color=fg)
            c.alignment = _align("center")
            c.border = _border_thin()

        c_st = ws.cell(r, 8, status)
        c_st.fill = _fill(status_bg)
        c_st.font = _font(bold=True, size=9, color=status_color)
        c_st.alignment = _align("center")
        c_st.border = _border_thin()

        for col in range(1, 9):
            ws.cell(r, col).border = _border_thin()
        ws.row_dimensions[r].height = 20
        if i % 2 == 0:
            for col in [1, 2]:
                ws.cell(r, col).fill = _fill(GRAY_L)

# ── Aba 3 — Achados detalhados ────────────────────────────────────────────────

TYPE_LABELS = {
    "cve":         "CVE — Biblioteca",
    "sast":        "Código (SAST)",
    "secret_git":  "Segredo no git",
    "secret_disk": "Segredo no disco",
    "license":     "Licença restritiva",
}
TYPE_COLORS = {
    "cve":         (LIGHT_RED,   RED),
    "sast":        (LIGHT_AMBER, AMBER),
    "secret_git":  (LIGHT_RED,   RED),
    "secret_disk": (LIGHT_AMBER, AMBER),
    "license":     (LIGHT_AMBER, AMBER),
}

def _aba_achados(wb: Workbook, summary: dict, logo_path: Path | None) -> None:
    ws = wb.create_sheet("Achados Detalhados")
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 35
    ws.column_dimensions["E"].width = 42
    ws.column_dimensions["F"].width = 42
    ws.column_dimensions["G"].width = 30

    _add_logo_header(ws, logo_path, "Achados detalhados",
                     f"Gerado em {summary['generated_at']}  ·  ordenado por gravidade")

    headers = ["Projeto", "Tipo", "Gravidade", "O que foi encontrado", "O que significa", "O que fazer", "Arquivo / Detalhe"]
    _header_row(ws, 4, headers)
    ws.row_dimensions[4].height = 22

    findings = summary.get("findings", [])
    ORDER = {"alto": 0, "médio": 1, "baixo": 2, "high": 0, "medium": 1, "low": 2}
    findings_sorted = sorted(findings, key=lambda f: (ORDER.get(f.get("severity","").lower(), 9), f.get("project","")))

    for i, f in enumerate(findings_sorted):
        r = 5 + i
        t = f.get("type", "")
        sev = f.get("severity", "médio")
        bg, fg = TYPE_COLORS.get(t, (LIGHT_AMBER, AMBER))
        sev_bg = LIGHT_RED if sev in ("alto","high") else LIGHT_AMBER if sev in ("médio","medium") else LIGHT_GREEN
        sev_fg = RED       if sev in ("alto","high") else AMBER       if sev in ("médio","medium") else GREEN2

        ws.cell(r, 1, f.get("project", "")).font = _font(bold=True, size=9)
        c_type = ws.cell(r, 2, TYPE_LABELS.get(t, t))
        c_type.fill = _fill(bg)
        c_type.font = _font(bold=True, size=9, color=fg)
        c_sev = ws.cell(r, 3, _severity_label(sev))
        c_sev.fill = _fill(sev_bg)
        c_sev.font = _font(bold=True, size=9, color=sev_fg)
        ws.cell(r, 4, f.get("title", "")).font = _font(size=9)
        ws.cell(r, 5, f.get("meaning", "")).font = _font(size=9, color="444444")
        ws.cell(r, 6, f.get("action", "")).font = _font(size=9, color=GREEN)
        ws.cell(r, 7, f.get("file","") or f.get("detail","")).font = _font(size=9, color="777777", italic=True)

        for col in range(1, 8):
            c = ws.cell(r, col)
            c.alignment = _align("left", "top", wrap=True)
            c.border = _border_thin()
            if col not in (2, 3) and i % 2 == 1:
                c.fill = _fill(GRAY_L)
        ws.row_dimensions[r].height = 44

    if not findings_sorted:
        ws.cell(5, 1, "Nenhum achado ativo encontrado. Todos os projetos estão limpos!")
        ws.cell(5, 1).font = _font(bold=True, color=GREEN2, size=11)
        ws.merge_cells("A5:G5")

# ── Aba 4 — Histórico ─────────────────────────────────────────────────────────

def _aba_historico(wb: Workbook, history: list[dict], summary: dict, logo_path: Path | None) -> None:
    ws = wb.create_sheet("Histórico")
    for col, w in zip("ABCDEFGH", [22, 12, 12, 14, 16, 14, 18, 18]):
        ws.column_dimensions[col].width = w

    _add_logo_header(ws, logo_path, "Histórico de Auditorias",
                     "Evolução ao longo do tempo — cada linha é uma auditoria rodada")

    headers = ["Data", "CVEs", "SAST", "Seg. git", "Seg. disco", "Licenças", "Proj. limpos", "Total proj."]
    _header_row(ws, 4, headers)
    ws.row_dimensions[4].height = 22

    for i, h in enumerate(reversed(history)):
        r = 5 + i
        is_latest = (i == 0)
        vals = [
            h.get("generated_at",""),
            h.get("total_cves",0),
            h.get("total_sast",0),
            h.get("secrets_git",0),
            h.get("secrets_disk",0),
            h.get("total_licenses",0),
            h.get("clean_projects",0),
            h.get("total_projects",0),
        ]
        for col, v in enumerate(vals, 1):
            c = ws.cell(r, col, v)
            c.font = _font(bold=is_latest, size=10, color=GREEN2 if is_latest else "333333")
            c.border = _border_thin()
            c.alignment = _align("center" if col > 1 else "left")
            if is_latest:
                c.fill = _fill(LIGHT_GREEN)
        ws.row_dimensions[r].height = 18

    # Gráfico de linha — tendência
    if len(history) >= 2:
        data_start = 4
        data_end = 4 + len(history)
        chart = LineChart()
        chart.title = "Tendência de achados por auditoria"
        chart.style = 10
        chart.y_axis.title = "Quantidade"
        chart.x_axis.title = "Data"
        chart.width = 24
        chart.height = 12

        cats = Reference(ws, min_col=1, min_row=5, max_row=data_end)
        for col_idx, label in [(2,"CVEs"),(3,"SAST"),(4,"Seg. git"),(5,"Seg. disco"),(6,"Licenças")]:
            data = Reference(ws, min_col=col_idx, min_row=4, max_row=data_end)
            series = chart.series.SeriesConstructor(data, cats, title_from_data=True)
            chart.series.append(series)

        ws.add_chart(chart, "A" + str(data_end + 3))

# ── Ponto de entrada ──────────────────────────────────────────────────────────

def gerar_excel(summary_path: Path, history_path: Path, logo_path: Path | None = None) -> bytes:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    history: list[dict] = []
    if history_path.exists():
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
