import json
import os
import subprocess
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

import markdown as md_lib
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, SessionLocal
from .models import Documento, Revisao
from .seed import popular_banco

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR    = Path(__file__).resolve().parent.parent / "static"
FINDABC_DIR   = Path("D:/02_Finaud/Projetos/ativos/findabc")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE revisoes ADD COLUMN hora TEXT"))
            conn.commit()
    except Exception:
        pass  # coluna já existe
    with SessionLocal() as db:
        popular_banco(db)
    yield


app = FastAPI(title="Painel de Conformidade — Finaud", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
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
def abrir_arquivo(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc or not doc.arquivo:
        return RedirectResponse("/", status_code=303)
    path = FINDABC_DIR / doc.arquivo
    if path.exists():
        os.startfile(str(path))
    return RedirectResponse("/", status_code=303)


# ── editar e registrar revisão ───────────────────────────────────────────────

@app.get("/editar/{doc_id}", response_class=HTMLResponse)
def editar_documento(doc_id: int, request: Request, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        return HTMLResponse("Documento não encontrado.", status_code=404)
    tem_arquivo = bool(doc.arquivo and doc.categoria != "Certificado")
    conteudo = (_ler_arquivo(doc.arquivo) or "") if tem_arquivo else ""
    return templates.TemplateResponse(request, "editar.html", {
        "request":      request,
        "doc":          doc,
        "conteudo":     conteudo,
        "tem_arquivo":  tem_arquivo,
    })


@app.post("/editar/{doc_id}")
def salvar_revisao(
    doc_id:   int,
    conteudo: str = Form(""),
    versao:   str = Form(...),
    notas:    str = Form(""),
    revisor:  str = Form("Michel Rui Costa"),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if doc:
        if doc.arquivo and doc.categoria != "Certificado":
            (FINDABC_DIR / doc.arquivo).write_text(conteudo, encoding="utf-8")
        agora = datetime.now()
        db.add(Revisao(
            doc_id=doc_id,
            versao=versao,
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

# ── /p/{token} — reservado para Opção 2 (portal do cliente, pós-deploy) ─────
# @app.get("/p/{token}", response_class=HTMLResponse)
# def portal_cliente(token: str, ...): ...
