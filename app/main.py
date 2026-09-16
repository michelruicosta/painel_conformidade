from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Area, Controle
from .seed import popular_banco
from .routers import controles as controles_router

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from .database import SessionLocal
    with SessionLocal() as db:
        popular_banco(db)
    yield


app = FastAPI(title="Painel de Conformidade", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(controles_router.router)


def _ctx_base(db: Session) -> dict:
    areas = db.query(Area).order_by(Area.ordem).all()
    return {"areas": areas}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    ctx = _ctx_base(db)
    areas = ctx["areas"]

    todos = [c for a in areas for c in a.controles]
    total = len(todos)
    conformes = sum(1 for c in todos if c.status == "conforme")
    score_global = round(conformes / total * 100) if total else 0

    criticos = sorted(
        [c for c in todos if c.status != "conforme" and c.urgencia > 0],
        key=lambda c: c.urgencia,
        reverse=True,
    )

    hoje = date.today()
    proximos = sorted(
        [
            c for c in todos
            if c.status == "conforme"
            and c.proxima_revisao
            and 0 <= (c.proxima_revisao - hoje).days <= 30
        ],
        key=lambda c: c.proxima_revisao,
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            **ctx,
            "score_global": score_global,
            "total": total,
            "conformes": conformes,
            "criticos": criticos,
            "proximos": proximos,
            "pagina": "dashboard",
        },
    )


@app.get("/area/{slug}", response_class=HTMLResponse)
def area_detalhe(slug: str, request: Request, db: Session = Depends(get_db)):
    ctx = _ctx_base(db)
    area = db.query(Area).filter(Area.slug == slug).first()
    if not area:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Área não encontrada")

    controles = sorted(area.controles, key=lambda c: (-c.peso_risco, c.nome))

    return templates.TemplateResponse(
        "area.html",
        {
            "request": request,
            **ctx,
            "area": area,
            "controles": controles,
            "pagina": slug,
        },
    )
