from datetime import date, timedelta
from sqlalchemy import Column, Integer, String, Date, Text
from .database import Base


PERIODICIDADE_DIAS = {
    "mensal": 30,
    "trimestral": 90,
    "semestral": 180,
    "anual": 365,
}


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    arquivo = Column(String, nullable=True)
    periodicidade = Column(String, nullable=False, default="anual")
    ultima_revisao = Column(Date, nullable=True)
    responsavel = Column(String, default="Michel Rui Costa")
    notas = Column(Text, nullable=True)

    @property
    def proxima_revisao(self) -> date | None:
        if not self.ultima_revisao:
            return None
        dias = PERIODICIDADE_DIAS.get(self.periodicidade, 365)
        return self.ultima_revisao + timedelta(days=dias)

    @property
    def dias_para_revisao(self) -> int | None:
        if not self.proxima_revisao:
            return None
        return (self.proxima_revisao - date.today()).days

    @property
    def status(self) -> str:
        d = self.dias_para_revisao
        if d is None:
            return "sem_data"
        if d < 0:
            return "vencido"
        if d <= 30:
            return "atencao"
        return "em_dia"

    @property
    def status_label(self) -> str:
        return {
            "vencido": "Vencido",
            "atencao": "Vence em breve",
            "em_dia": "Em dia",
            "sem_data": "Sem data",
        }[self.status]

    @property
    def proxima_revisao_str(self) -> str:
        if not self.proxima_revisao:
            return "—"
        d = self.dias_para_revisao
        if d < 0:
            return f"Vencido há {abs(d)} dias"
        if d == 0:
            return "Vence hoje"
        if d <= 30:
            return f"Em {d} dias ({self.proxima_revisao.strftime('%d/%m/%Y')})"
        return self.proxima_revisao.strftime("%d/%m/%Y")
