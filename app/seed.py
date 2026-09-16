from datetime import date
from sqlalchemy.orm import Session
from .models import Area, Controle

AREAS = [
    {"id": 1, "nome": "Segurança", "slug": "seguranca", "icone": "🔒",
     "descricao": "Cibersegurança, acessos, chaves, incidentes e mudanças", "ordem": 1},
    {"id": 2, "nome": "Infraestrutura", "slug": "infraestrutura", "icone": "🖥️",
     "descricao": "VPS, backup, recuperação de desastres e continuidade", "ordem": 2},
    {"id": 3, "nome": "LGPD", "slug": "lgpd", "icone": "🛡️",
     "descricao": "Privacidade, ciclo de vida de dados e direitos dos titulares", "ordem": 3},
    {"id": 4, "nome": "Governança", "slug": "governanca", "icone": "📋",
     "descricao": "Código de conduta, KYC e políticas de governança", "ordem": 4},
]

CONTROLES = [
    # ── Segurança ────────────────────────────────────────────────────────────
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Política de Segurança Cibernética",
        "descricao": "Política pública de segurança: CIA, autenticidade e rastreabilidade.",
        "arquivo_referencia": "politica_seguranca_cibernetica.md", "notas": "",
    },
    {
        "area_id": 1, "peso_risco": 2, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 15),
        "proxima_revisao": date(2027, 3, 15), "gatilho": None,
        "nome": "Arquitetura de Segurança",
        "descricao": "Mapeamento de todas as camadas de proteção (Cloudflare, UFW, Monarx, Nginx).",
        "arquivo_referencia": "arquitetura_seguranca_completa.md", "notas": "",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": None,
        "proxima_revisao": None, "gatilho": "deploy",
        "nome": "Cloudflare — ativação no VPS",
        "descricao": "Domínio finaudapps.com.br cadastrado. Cloudflare Free ativo, aguardando apontar DNS para o VPS em produção.",
        "arquivo_referencia": "arquitetura_cloudflare.md",
        "notas": "Conta ativa. DDoS L3/L4/L7 + Bot Fight Mode inclusos no Free.",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": None,
        "proxima_revisao": None, "gatilho": "deploy",
        "nome": "Fail2ban — instalação no VPS",
        "descricao": "IDS/IPS para bloqueio de IPs com falhas repetidas de SSH e bruteforce HTTP.",
        "arquivo_referencia": "arquitetura_seguranca_completa.md",
        "notas": "Planejado. Instalar e configurar no deploy do VPS.",
    },
    {
        "area_id": 1, "peso_risco": 2, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": None,
        "proxima_revisao": None, "gatilho": "1_cliente",
        "nome": "Monarx — auto-limpeza ativada",
        "descricao": "Monarx detecta malware (ativo). Auto-limpeza (R$17/mês) desativada até o 1º cliente.",
        "arquivo_referencia": "arquitetura_seguranca_completa.md",
        "notas": "Heartbeat: 15/09/2026 · 18.109 arquivos · zero detecções.",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 15),
        "proxima_revisao": date(2027, 3, 15), "gatilho": None,
        "nome": "Política de Gestão de Firewall",
        "descricao": "Criação, alteração e exclusão de regras nas camadas Cloudflare, UFW e Hostinger.",
        "arquivo_referencia": "politica_gestao_firewall.md", "notas": "",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Política de Gestão de Chaves e Segredos",
        "descricao": "Gestão de SECRET_KEY JWT, FERNET_KEY MFA, DATABASE_URL, SSL. Rotação semestral.",
        "arquivo_referencia": "politica_gestao_chaves.md",
        "notas": "Próxima rotação da SECRET_KEY: março/2027.",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Controle de Contas de Serviço",
        "descricao": "Registro e aprovação formal de contas genéricas e de serviço (finaud_admin, SMTP).",
        "arquivo_referencia": "controle_contas_servico.md", "notas": "",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Revisão de Acessos",
        "descricao": "Recertificação semestral de acessos lógicos (Finaud Tec + tenant/cliente_admin).",
        "arquivo_referencia": "procedimento_revisao_acessos.md",
        "notas": "Primeira revisão agendada: março/2027.",
    },
    {
        "area_id": 1, "peso_risco": 3, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Política de Gestão de Incidentes",
        "descricao": "4 fases: identificação, contenção, erradicação, recuperação. SLA LGPD Art. 48.",
        "arquivo_referencia": "politica_gestao_incidentes.md",
        "notas": "Histórico de incidentes vazio (pré-produção).",
    },
    {
        "area_id": 1, "peso_risco": 2, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Procedimento de Gestão de Mudanças",
        "descricao": "Mudanças normal, emergencial e padrão em produção. Checklist pré-deploy e rastreabilidade via Git.",
        "arquivo_referencia": "procedimento_gestao_mudancas.md", "notas": "",
    },

    # ── Infraestrutura ───────────────────────────────────────────────────────
    {
        "area_id": 2, "peso_risco": 2, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 15),
        "proxima_revisao": date(2027, 3, 15), "gatilho": None,
        "nome": "Evidências de Infraestrutura",
        "descricao": "VPS 922349 · Hostinger · São Paulo · KVM4 · 16GB RAM · 200GB NVMe · Tier III.",
        "arquivo_referencia": "evidencias_infraestrutura.md", "notas": "",
    },
    {
        "area_id": 2, "peso_risco": 1, "periodicidade": "mensal",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 15),
        "proxima_revisao": date(2026, 10, 15), "gatilho": None,
        "nome": "Custos de Infraestrutura",
        "descricao": "Registro de custos ativos, planejados e opcionais. Decisões documentadas.",
        "arquivo_referencia": "custos_infraestrutura.md", "notas": "",
    },
    {
        "area_id": 2, "peso_risco": 2, "periodicidade": "mensal",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2026, 10, 16), "gatilho": None,
        "nome": "Log de Disponibilidade",
        "descricao": "Log manual de uptime até o UptimeRobot entrar em produção. SLA 99,5%/mês.",
        "arquivo_referencia": "log_disponibilidade.md",
        "notas": "Substituído automaticamente pelo UptimeRobot após o deploy.",
    },
    {
        "area_id": 2, "peso_risco": 2, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": None,
        "proxima_revisao": None, "gatilho": "deploy",
        "nome": "UptimeRobot — ativação no deploy",
        "descricao": "Monitoramento externo de disponibilidade. Free: check a cada 5 min. Pro: 1 min.",
        "arquivo_referencia": "custos_infraestrutura.md",
        "notas": "Free suficiente para início. Pro (US$7/mês) avaliado no crescimento.",
    },
    {
        "area_id": 2, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Política de Backup",
        "descricao": "4 camadas: snapshot VPS semanal, pg_dump diário, backup diário Hostinger, Backblaze B2 offsite.",
        "arquivo_referencia": "politica_backup.md",
        "notas": "Testes de restore: março e setembro. Próximo: no deploy.",
    },
    {
        "area_id": 2, "peso_risco": 3, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": None,
        "proxima_revisao": None, "gatilho": "deploy",
        "nome": "Backup diário Hostinger (add-on)",
        "descricao": "Reduz RPO de 7 dias → 24h para o VPS inteiro. R$65/mês.",
        "arquivo_referencia": "custos_infraestrutura.md",
        "notas": "Contratar no deploy. RPO 24h é requisito mínimo aceitável para S4.",
    },
    {
        "area_id": 2, "peso_risco": 3, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": None,
        "proxima_revisao": None, "gatilho": "deploy",
        "nome": "Backup offsite — Backblaze B2",
        "descricao": "Backup dos dumps PostgreSQL fora do provedor principal. ~US$6/mês.",
        "arquivo_referencia": "politica_backup.md",
        "notas": "Custo depende do volume de dados. Ativar no deploy.",
    },
    {
        "area_id": 2, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Plano de Recuperação de Desastres (DRP)",
        "descricao": "5 cenários: queda VPS, corrupção de banco, ransomware, credenciais, Cloudflare. RPO 24h, RTO 6h.",
        "arquivo_referencia": "plano_recuperacao_desastres.md",
        "notas": "Histórico de ativações vazio (pré-produção).",
    },
    {
        "area_id": 2, "peso_risco": 3, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "Plano de Continuidade de Negócios (BCP)",
        "descricao": "Garante que clientes S4 mantenham obrigações regulatórias BCB durante indisponibilidade.",
        "arquivo_referencia": "plano_continuidade_negocios.md",
        "notas": "SLA 99,5%/mês · RTO <= 6h. Revisão: março e setembro.",
    },

    # ── LGPD ─────────────────────────────────────────────────────────────────
    {
        "area_id": 3, "peso_risco": 3, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Política do Ciclo de Vida de Dados",
        "descricao": "Coleta, armazenamento, uso, retenção e eliminação. Prazos por tipo de dado.",
        "arquivo_referencia": "politica_ciclo_vida_dados.md", "notas": "",
    },
    {
        "area_id": 3, "peso_risco": 3, "periodicidade": "por_demanda",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 15),
        "proxima_revisao": None, "gatilho": None,
        "nome": "Procedimento de Destruição de Dados",
        "descricao": "Destruição segura ao término de contrato (NIST SP 800-88). Emite Declaração de Destruição.",
        "arquivo_referencia": "procedimento_destruicao_dados.md",
        "notas": "Histórico de destruições vazio (pré-produção).",
    },
    {
        "area_id": 3, "peso_risco": 3, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Procedimento de Atendimento a Titulares",
        "descricao": "Direitos Art. 18 LGPD: acesso, correção, eliminação, portabilidade, oposição.",
        "arquivo_referencia": "procedimento_atendimento_titulares.md",
        "notas": "Histórico de solicitações vazio (pré-produção).",
    },
    {
        "area_id": 3, "peso_risco": 3, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "RIPD — Relatório de Impacto à Privacidade",
        "descricao": "10 riscos avaliados. Nenhum classificado como Alto após mitigações.",
        "arquivo_referencia": "ripd_relatorio_impacto_privacidade.md",
        "notas": "⚠️ Recomendada revisão por advogado especializado em LGPD antes do 1º cliente.",
    },
    {
        "area_id": 3, "peso_risco": 2, "periodicidade": "semestral",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 3, 16), "gatilho": None,
        "nome": "ROPA — Registro de Atividades de Tratamento",
        "descricao": "4 atividades: autenticação, trilha de auditoria, dados de compliance, Cloudflare.",
        "arquivo_referencia": "ropa_registro_atividades_tratamento.md", "notas": "",
    },
    {
        "area_id": 3, "peso_risco": 2, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Política de Privacidade Interna",
        "descricao": "Regras de conduta para colaboradores e representantes da Finaud Tec.",
        "arquivo_referencia": "politica_privacidade_interna.md", "notas": "",
    },
    {
        "area_id": 3, "peso_risco": 3, "periodicidade": "gatilho",
        "status": "pendente", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": None, "gatilho": "1_cliente",
        "nome": "DPA — Acordo de Processamento de Dados",
        "descricao": "Template de DPA entre Finaud Tec (Operadora) e Contratante (Controladora). 14 cláusulas LGPD.",
        "arquivo_referencia": "dpa_acordo_processamento_dados.md",
        "notas": "⚠️ Revisão jurídica obrigatória antes da assinatura do 1º contrato.",
    },

    # ── Governança ───────────────────────────────────────────────────────────
    {
        "area_id": 4, "peso_risco": 2, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Código de Conduta e Ética",
        "descricao": "Integridade, anticorrupção (Lei 12.846/2013), conflito de interesses, uso de IA, canal de denúncias.",
        "arquivo_referencia": "codigo_conduta_etica.md", "notas": "",
    },
    {
        "area_id": 4, "peso_risco": 2, "periodicidade": "anual",
        "status": "conforme", "ultima_atualizacao": date(2026, 9, 16),
        "proxima_revisao": date(2027, 9, 16), "gatilho": None,
        "nome": "Política KYC para Contratação",
        "descricao": "Verificação de CNPJ, autorização BCB, representante legal e listas restritivas OFAC/BCB.",
        "arquivo_referencia": "politica_kyc_contratacao.md", "notas": "",
    },
]


def popular_banco(db: Session) -> None:
    if db.query(Area).count() > 0:
        return
    for a in AREAS:
        db.add(Area(**a))
    db.flush()
    for c in CONTROLES:
        db.add(Controle(**c))
    db.commit()
