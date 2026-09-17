from datetime import date, timedelta
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


PERIODICIDADE_DIAS = {
    "mensal": 30,
    "trimestral": 90,
    "semestral": 180,
    "anual": 365,
}


class Revisao(Base):
    __tablename__ = "revisoes"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documentos.id"), nullable=False)
    versao = Column(String, nullable=False)  # "1.0", "1.1", "2.0"
    data = Column(Date, nullable=False)
    responsavel = Column(String, default="Michel Rui Costa")
    notas = Column(Text, nullable=True)

    documento = relationship("Documento", back_populates="revisoes")


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    arquivo = Column(String, nullable=True)
    periodicidade = Column(String, nullable=False, default="anual")
    classificacao = Column(String, nullable=False, default="Confidencial")
    responsavel = Column(String, default="Michel Rui Costa")

    revisoes = relationship("Revisao", back_populates="documento",
                            order_by="Revisao.data", cascade="all, delete-orphan")

    # ── propriedades calculadas ──────────────────────────────

    @property
    def ultima_revisao(self) -> date | None:
        if not self.revisoes:
            return None
        return self.revisoes[-1].data

    @property
    def versao_atual(self) -> str:
        if not self.revisoes:
            return "—"
        return self.revisoes[-1].versao

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

    @property
    def proxima_versao_sugerida(self) -> str:
        if not self.revisoes:
            return "1.0"
        partes = self.versao_atual.split(".")
        try:
            maior, menor = int(partes[0]), int(partes[1])
            return f"{maior}.{menor + 1}"
        except Exception:
            return "1.0"
