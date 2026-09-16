from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Controle, HistoricoControle

router = APIRouter(prefix="/controles", tags=["controles"])

_PERIODOS = {
    "mensal": lambda d: d + relativedelta(months=1),
    "trimestral": lambda d: d + relativedelta(months=3),
    "semestral": lambda d: d + relativedelta(months=6),
    "anual": lambda d: d + relativedelta(years=1),
}


@router.post("/{controle_id}/editar")
def editar_controle(
    controle_id: int,
    status: str = Form(...),
    notas: str = Form(""),
    proxima_revisao: str = Form(""),
    db: Session = Depends(get_db),
):
    controle = db.get(Controle, controle_id)
    if not controle:
        raise HTTPException(status_code=404)

    status_anterior = controle.status
    controle.status = status
    controle.notas = notas
    controle.ultima_atualizacao = date.today()

    if proxima_revisao:
        controle.proxima_revisao = date.fromisoformat(proxima_revisao)
    elif controle.periodicidade in _PERIODOS:
        controle.proxima_revisao = _PERIODOS[controle.periodicidade](date.today())

    if status_anterior != status:
        db.add(HistoricoControle(
            controle_id=controle_id,
            status_anterior=status_anterior,
            status_novo=status,
            notas=notas,
        ))

    db.commit()

    area_slug = controle.area.slug
    return RedirectResponse(url=f"/area/{area_slug}", status_code=303)
