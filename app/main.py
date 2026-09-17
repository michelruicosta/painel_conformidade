import json
import os
import subprocess
import threading
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

import markdown as md_lib
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, SessionLocal
from .excel_export import gerar_excel
from .models import Documento, Revisao
from .seed import popular_banco

TEMPLATES_DIR    = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR       = Path(__file__).resolve().parent.parent / "static"
FINDABC_DIR      = Path("D:/02_Finaud/Projetos/ativos/findabc")
AUDIT_REPORT_DIR = Path(r"D:\02_Finaud\Projetos\ativos\_auditoria_seguranca\relatorios")
AUDIT_SCRIPT     = Path(r"D:\02_Finaud\Projetos\ativos\_auditoria_seguranca\security_audit.py")
AUDIT_PYTHON     = Path(r"D:\02_Finaud\Projetos\ativos\_auditoria_seguranca\.venv\Scripts\python.exe")
LOGO_PATH        = STATIC_DIR / "img" / "logo_finaud.png"

# ── Estado da auditoria em background ────────────────────────────────────────
_audit_lock   = threading.Lock()
_audit_status: dict = {"running": False, "started_at": None, "finished_at": None, "error": None}

def _run_audit_bg() -> None:
    global _audit_status
    try:
        subprocess.run(
            [str(AUDIT_PYTHON), str(AUDIT_SCRIPT)],
            capture_output=True, timeout=900,
        )
        with _audit_lock:
            _audit_status["error"] = None
    except Exception as e:
        with _audit_lock:
            _audit_status["error"] = str(e)
    finally:
        with _audit_lock:
            _audit_status["running"]     = False
            _audit_status["finished_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE revisoes ADD COLUMN hora TEXT"))
            conn.commit()
    except Exception:  # nosec B110 — coluna já existe no banco (ALTER TABLE idempotente)
        pass  # coluna já existe
    with SessionLocal() as db:
        popular_banco(db)
    yield


app = FastAPI(title="Painel de Conformidade — Finaud", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if AUDIT_REPORT_DIR.exists():
    app.mount("/relatorios", StaticFiles(directory=AUDIT_REPORT_DIR), name="relatorios")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ── utilitários ──────────────────────────────────────────────────────────────

def _ler_arquivo(arquivo: str) -> str | None:
    """Lê .md ou .html relativo ao findabc. Retorna None se não encontrar."""
    path = FINDABC_DIR / arquivo
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _renderizar(arquivo: str) -> str:
    """Converte .md para HTML. Para outros formatos retorna texto cru."""
    conteudo = _ler_arquivo(arquivo)
    if conteudo is None:
        return "<p><em>Arquivo não encontrado.</em></p>"
    if arquivo.endswith(".md"):
        return md_lib.markdown(conteudo, extensions=["tables", "fenced_code"])
    return f"<pre>{conteudo}</pre>"


# ── health ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── dashboard ────────────────────────────────────────────────────────────────

_CATEGORIAS_ORDEM = ["Política", "Procedimento", "Governança", "Técnico", "Certificado"]


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    docs = db.query(Documento).order_by(Documento.nome).all()

    por_categoria: dict[str, list] = {}
    for cat in _CATEGORIAS_ORDEM:
        cat_docs = [d for d in docs if d.categoria == cat]
        if cat_docs:
            por_categoria[cat] = cat_docs
    for d in docs:
        if d.categoria not in por_categoria:
            por_categoria.setdefault(d.categoria, []).append(d)

    docs_json = json.dumps([{
        "id":           d.id,
        "nome":         d.nome,
        "categoria":    d.categoria,
        "periodicidade":d.periodicidade,
        "versao":       d.versao_atual,
        "proxima_versao": d.proxima_versao_sugerida,
        "prazo_str":    d.proxima_revisao_str,
        "dias":         d.dias_para_revisao,
        "status":       d.status,
        "tem_arquivo":  bool(d.arquivo and d.categoria != "Certificado"),
    } for d in docs], ensure_ascii=False)

    return templates.TemplateResponse(request, "dashboard.html", {
        "request":       request,
        "por_categoria": por_categoria,
        "docs_json":     docs_json,
        "total":         len(docs),
    })


# ── ver / exportar documento ─────────────────────────────────────────────────

@app.get("/ver/{doc_id}", response_class=HTMLResponse)
def ver_documento(doc_id: int, request: Request, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        return HTMLResponse("Documento não encontrado.", status_code=404)

    eh_pdf = doc.arquivo and doc.arquivo.endswith(".pdf")
    conteudo_html = "" if eh_pdf else _renderizar(doc.arquivo or "")

    return templates.TemplateResponse(request, "ver.html", {
        "request":       request,
        "doc":           doc,
        "conteudo_html": conteudo_html,
        "eh_pdf":        eh_pdf,
    })


# ── abrir arquivo no editor ──────────────────────────────────────────────────

@app.get("/abrir/{doc_id}")
def abrir_arquivo(doc_id: int, ajax: bool = False, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if doc and doc.arquivo:
        path = FINDABC_DIR / doc.arquivo
        if path.exists():
            os.startfile(str(path))  # nosec B606 — caminho vem de constante interna
    if ajax:
        return {"ok": True}
    return RedirectResponse("/", status_code=303)


# ── editar e registrar revisão ───────────────────────────────────────────────

@app.get("/editar/{doc_id}", response_class=HTMLResponse)
def editar_documento(doc_id: int, request: Request, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        return HTMLResponse("Documento não encontrado.", status_code=404)
    tem_arquivo = bool(doc.arquivo and doc.categoria != "Certificado")
    conteudo_html = _renderizar(doc.arquivo) if tem_arquivo else ""
    return templates.TemplateResponse(request, "editar.html", {
        "request":       request,
        "doc":           doc,
        "tem_arquivo":   tem_arquivo,
        "conteudo_html": conteudo_html,
    })


@app.post("/editar/{doc_id}")
def salvar_revisao(
    doc_id:  int,
    notas:   str = Form(""),
    revisor: str = Form("Michel Rui Costa"),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if doc:
        agora = datetime.now()
        db.add(Revisao(
            doc_id=doc_id,
            versao=doc.proxima_versao_sugerida,
            data=agora.date(),
            hora=agora.strftime("%H:%M"),
            responsavel=revisor,
            notas=notas or "—",
        ))
        db.commit()
    return RedirectResponse("/", status_code=303)


# ── pacote de due diligence ──────────────────────────────────────────────────

@app.get("/pacote", response_class=HTMLResponse)
def pacote_due_diligence(request: Request, db: Session = Depends(get_db)):
    """Opção 1: página imprimível com índice de todos os documentos próprios."""
    docs = (
        db.query(Documento)
        .filter(Documento.categoria != "Certificado")
        .order_by(Documento.categoria, Documento.nome)
        .all()
    )
    return templates.TemplateResponse(request, "pacote.html", {
        "request": request,
        "docs":    docs,
        "hoje":    date.today(),
    })

# ── segurança — painel de auditoria de segurança ─────────────────────────────

@app.get("/seguranca", response_class=HTMLResponse)
def seguranca(request: Request):
    summary_path = AUDIT_REPORT_DIR / "latest_summary.json"
    summary = None
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    with _audit_lock:
        audit_st = _audit_status.copy()
    return templates.TemplateResponse(request, "seguranca.html", {
        "request":    request,
        "summary":    summary,
        "audit_st":   audit_st,
    })


@app.post("/seguranca/rodar")
def seguranca_rodar():
    with _audit_lock:
        if _audit_status["running"]:
            return {"ok": False, "message": "Auditoria já em andamento"}
        _audit_status["running"]     = True
        _audit_status["started_at"]  = datetime.now().strftime("%d/%m/%Y %H:%M")
        _audit_status["finished_at"] = None
        _audit_status["error"]       = None
    t = threading.Thread(target=_run_audit_bg, daemon=True)
    t.start()
    return {"ok": True, "message": "Auditoria iniciada"}


@app.get("/seguranca/status")
def seguranca_status():
    with _audit_lock:
        return _audit_status.copy()


@app.get("/seguranca/exportar")
def seguranca_exportar():
    summary_path = AUDIT_REPORT_DIR / "latest_summary.json"
    history_path = AUDIT_REPORT_DIR / "history.json"
    if not summary_path.exists():
        return Response("Nenhuma auditoria disponível.", status_code=404)
    try:
        xlsx = gerar_excel(summary_path, history_path, LOGO_PATH if LOGO_PATH.exists() else None)
    except Exception as e:
        return Response(f"Erro ao gerar Excel: {e}", status_code=500)
    ts = datetime.now().strftime("%Y-%m-%d")
    filename = f"auditoria_seguranca_{ts}.xlsx"
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── /p/{token} — reservado para Opção 2 (portal do cliente, pós-deploy) ─────
# @app.get("/p/{token}", response_class=HTMLResponse)
# def portal_cliente(token: str, ...): ...
