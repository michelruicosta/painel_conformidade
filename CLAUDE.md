# Painel de Conformidade — Instruções para o Claude Code

> **Este arquivo é lido em toda mensagem de todo chat.** Só entra aqui o que vale sempre.

---

## Sobre o projeto

Painel interno da Finaud Tec para gestão de conformidade: segurança cibernética, infraestrutura, LGPD e governança.  
Uso solo (Michel). Pode evoluir para produto comercial.

**Stack:** FastAPI · SQLite (SQLAlchemy) · Jinja2 · CSS puro  
**Porta:** 8009  
**Banco:** `conformidade.db` (local, ignorado no git)

---

## Como rodar

```bash
# Criar venv (primeira vez)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Rodar
python -m uvicorn app.main:app --host 127.0.0.1 --port 8009 --reload

# Acesse: http://127.0.0.1:8009/
```

O banco é criado e populado automaticamente na primeira execução.

---

## Estrutura

```
painel_conformidade/
├── app/
│   ├── main.py          # FastAPI app, rotas, startup
│   ├── database.py      # SQLite + SQLAlchemy engine
│   ├── models.py        # Area, Controle, HistoricoControle
│   ├── seed.py          # Dados iniciais (29 controles)
│   └── routers/
│       └── controles.py # CRUD de controles
├── templates/           # Jinja2: base, dashboard, area
├── static/              # CSS, JS
├── conformidade.db      # Banco local (não vai ao git)
└── requirements.txt
```

---

## Regras de trabalho

1. **Antes de qualquer alteração:** declarar o que vai mudar e aguardar OK
2. **Commits em português:** `feat:`, `fix:`, `docs:`, `refactor:`
3. **Nunca** `git push --force`
4. **Seed data** (`seed.py`) é a fonte dos controles — editar lá para adicionar novos controles na carga inicial
5. O banco `conformidade.db` nunca vai ao git — backup manual se necessário

---

## Áreas e controles

| Área | Slug | Controles |
|------|------|-----------|
| Segurança | seguranca | 11 |
| Infraestrutura | infraestrutura | 9 |
| LGPD | lgpd | 7 |
| Governança | governanca | 2 |

---

## Rituais de sessão

- **`/iniciar`** — abre o chat com contexto
- **`/salvar`** — salva no meio da sessão
- **`/fechar`** — commit + encerra o dia
