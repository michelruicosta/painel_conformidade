from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, SessionLocal
from .models import Documento
from .seed import popular_banco

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        popular_banco(db)
    yield


app = FastAPI(title="Painel de Conformidade — Finaud", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    docs = db.query(Documento).order_by(Documento.categoria, Documento.nome).all()

    vencidos = [d for d in docs if d.status == "vencido"]
    atencao = [d for d in docs if d.status == "atencao"]
    em_dia = [d for d in docs if d.status == "em_dia"]
    sem_data = [d for d in docs if d.status == "sem_data"]

    categorias = sorted(set(d.categoria for d in docs))

    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "docs": docs,
        "vencidos": vencidos,
        "atencao": atencao,
        "em_dia": em_dia,
        "sem_data": sem_data,
        "categorias": categorias,
        "total": len(docs),
    })


@app.post("/revisar/{doc_id}")
def marcar_revisado(
    doc_id: int,
    notas: str = Form(""),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if doc:
        doc.ultima_revisao = date.today()
        doc.notas = notas or doc.notas
        db.commit()
    return RedirectResponse("/", status_code=303)
