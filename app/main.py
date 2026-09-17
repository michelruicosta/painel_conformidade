import os
import subprocess
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

import markdown as md_lib
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    docs = db.query(Documento).order_by(Documento.categoria, Documento.nome).all()

    vencidos = [d for d in docs if d.status == "vencido"]
    atencao  = [d for d in docs if d.status == "atencao"]
    em_dia   = [d for d in docs if d.status == "em_dia"]
    sem_data = [d for d in docs if d.status == "sem_data"]

    return templates.TemplateResponse(request, "dashboard.html", {
        "request":  request,
        "vencidos": vencidos,
        "atencao":  atencao,
        "em_dia":   em_dia,
        "sem_data": sem_data,
        "total":    len(docs),
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


# ── registrar revisão ────────────────────────────────────────────────────────

@app.post("/revisar/{doc_id}")
def revisar_documento(
    doc_id: int,
    versao: str = Form(...),
    notas:  str = Form(""),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if doc:
        db.add(Revisao(
            doc_id=doc_id,
            versao=versao,
            data=date.today(),
            responsavel="Michel Rui Costa",
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
