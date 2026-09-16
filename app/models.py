from datetime import date, datetime
from sqlalchemy import Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    descricao: Mapped[str] = mapped_column(String(200), default="")
    icone: Mapped[str] = mapped_column(String(10), default="📋")
    ordem: Mapped[int] = mapped_column(Integer, default=0)

    controles: Mapped[list["Controle"]] = relationship(
        back_populates="area",
        order_by="Controle.peso_risco.desc()",
    )

    @property
    def total(self) -> int:
        return len(self.controles)

    @property
    def conformes(self) -> int:
        return sum(1 for c in self.controles if c.status == "conforme")

    @property
    def score(self) -> int:
        if not self.controles:
            return 0
        return round(self.conformes / self.total * 100)


class Controle(Base):
    __tablename__ = "controles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"))
    nome: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str] = mapped_column(Text, default="")
    peso_risco: Mapped[int] = mapped_column(Integer, default=2)
    periodicidade: Mapped[str] = mapped_column(String(50), default="anual")
    status: Mapped[str] = mapped_column(String(20), default="pendente")
    ultima_atualizacao: Mapped[date | None] = mapped_column(Date, nullable=True)
    proxima_revisao: Mapped[date | None] = mapped_column(Date, nullable=True)
    gatilho: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notas: Mapped[str] = mapped_column(Text, default="")
    arquivo_referencia: Mapped[str | None] = mapped_column(String(200), nullable=True)

    area: Mapped["Area"] = relationship(back_populates="controles")
    historico: Mapped[list["HistoricoControle"]] = relationship(
        back_populates="controle",
        order_by="HistoricoControle.data.desc()",
    )

    @property
    def cor(self) -> str:
        if self.status == "conforme":
            return "verde"
        if self.status == "vencido":
            return "vermelho"
        return "amarelo"

    @property
    def urgencia(self) -> float:
        if self.status == "conforme":
            return 0.0
        peso = float(self.peso_risco)
        if self.periodicidade in ("gatilho", "por_demanda") or not self.proxima_revisao:
            return peso
        hoje = date.today()
        dias = (hoje - self.proxima_revisao).days
        if dias > 0:
            return peso * (1.0 + dias / 30)
        if dias > -30:
            return peso * 0.5
        return 0.0

    @property
    def proxima_revisao_str(self) -> str:
        if self.periodicidade == "gatilho" and self.gatilho:
            rotulos = {"deploy": "No deploy", "1_cliente": "1º cliente"}
            return rotulos.get(self.gatilho, self.gatilho)
        if self.periodicidade == "por_demanda":
            return "Por demanda"
        if self.proxima_revisao:
            return self.proxima_revisao.strftime("%d/%m/%Y")
        return "—"

    @property
    def dias_para_revisao(self) -> int | None:
        if not self.proxima_revisao:
            return None
        return (self.proxima_revisao - date.today()).days


class HistoricoControle(Base):
    __tablename__ = "historico_controles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    controle_id: Mapped[int] = mapped_column(ForeignKey("controles.id"))
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status_anterior: Mapped[str] = mapped_column(String(20))
    status_novo: Mapped[str] = mapped_column(String(20))
    notas: Mapped[str] = mapped_column(Text, default="")

    controle: Mapped["Controle"] = relationship(back_populates="historico")
