from datetime import date
from sqlalchemy.orm import Session
from .models import Documento

# (nome, categoria, arquivo, periodicidade, ultima_revisao)
DOCUMENTOS = [
    # ── Políticas ────────────────────────────────────────────
    ("Política de Backup",                    "Política",    "documentacao/evidencias/politica_backup.md",                   "semestral", date(2026, 9, 16)),
    ("Política de Ciclo de Vida dos Dados",   "Política",    "documentacao/evidencias/politica_ciclo_vida_dados.md",         "anual",     date(2026, 9, 16)),
    ("Política de Classificação de Informações", "Política", "documentacao/evidencias/politica_classificacao_informacoes.md","anual",     date(2026, 9, 16)),
    ("Política de Gestão de Atualizações",    "Política",    "documentacao/evidencias/politica_gestao_atualizacoes.md",      "semestral", date(2026, 9, 16)),
    ("Política de Gestão de Chaves",          "Política",    "documentacao/evidencias/politica_gestao_chaves.md",            "semestral", date(2026, 9, 16)),
    ("Política de Gestão de Firewall",        "Política",    "documentacao/evidencias/politica_gestao_firewall.md",          "semestral", date(2026, 9, 16)),
    ("Política de Gestão de Incidentes",      "Política",    "documentacao/evidencias/politica_gestao_incidentes.md",        "anual",     date(2026, 9, 16)),
    ("Política de KYC na Contratação",        "Política",    "documentacao/evidencias/politica_kyc_contratacao.md",          "anual",     date(2026, 9, 16)),
    ("Política de Privacidade Interna",       "Política",    "documentacao/evidencias/politica_privacidade_interna.md",      "anual",     date(2026, 9, 16)),
    ("Política de Segurança Cibernética",     "Política",    "documentacao/evidencias/politica_seguranca_cibernetica.md",    "anual",     date(2026, 9, 16)),

    # ── Procedimentos ────────────────────────────────────────
    ("Procedimento de Atendimento a Titulares", "Procedimento", "documentacao/evidencias/procedimento_atendimento_titulares.md", "anual",     date(2026, 9, 16)),
    ("Procedimento de Destruição de Dados",     "Procedimento", "documentacao/evidencias/procedimento_destruicao_dados.md",      "anual",     date(2026, 9, 16)),
    ("Procedimento de Gestão de Mudanças",      "Procedimento", "documentacao/evidencias/procedimento_gestao_mudancas.md",       "semestral", date(2026, 9, 16)),
    ("Procedimento de Revisão de Acessos",      "Procedimento", "documentacao/evidencias/procedimento_revisao_acessos.md",       "semestral", date(2026, 9, 16)),

    # ── Governança (planos + LGPD + gov) ─────────────────────
    ("Plano de Continuidade de Negócios (BCP)", "Governança", "documentacao/evidencias/plano_continuidade_negocios.md",          "semestral", date(2026, 9, 16)),
    ("Plano de Recuperação de Desastres (DRP)", "Governança", "documentacao/evidencias/plano_recuperacao_desastres.md",          "semestral", date(2026, 9, 16)),
    ("DPA — Acordo de Processamento de Dados",  "Governança", "documentacao/evidencias/dpa_acordo_processamento_dados.md",       "anual",     date(2026, 9, 16)),
    ("RIPD — Relatório de Impacto à Privacidade","Governança","documentacao/evidencias/ripd_relatorio_impacto_privacidade.md",   "anual",     date(2026, 9, 16)),
    ("RoPA — Registro de Atividades de Tratamento","Governança","documentacao/evidencias/ropa_registro_atividades_tratamento.md","semestral", date(2026, 9, 16)),
    ("Código de Conduta e Ética",               "Governança", "documentacao/evidencias/codigo_conduta_etica.md",                 "anual",     date(2026, 9, 16)),
    ("Controle de Contas de Serviço",           "Governança", "documentacao/evidencias/controle_contas_servico.md",              "semestral", date(2026, 9, 16)),
    ("Inventário de Ativos",                    "Governança", "documentacao/evidencias/inventario_ativos.md",                    "semestral", date(2026, 9, 16)),
    ("SLA do Serviço findabc",                  "Governança", "documentacao/evidencias/sla_servico_findabc.html",                "anual",     date(2026, 9, 16)),
    ("Template de E-mail de Manutenção",        "Governança", "documentacao/evidencias/template_email_manutencao.md",            "anual",     date(2026, 9, 16)),

    # ── Técnico (arquitetura + registros operacionais) ────────
    ("Arquitetura Cloudflare",                  "Técnico",    "documentacao/evidencias/arquitetura_cloudflare.md",              "semestral", date(2026, 9, 16)),
    ("Arquitetura de Segurança Completa",       "Técnico",    "documentacao/evidencias/arquitetura_seguranca_completa.md",      "semestral", date(2026, 9, 16)),
    ("Evidências de Infraestrutura",            "Técnico",    "documentacao/evidencias/evidencias_infraestrutura.md",           "semestral", date(2026, 9, 16)),
    ("Custos de Infraestrutura",                "Técnico",    "documentacao/evidencias/custos_infraestrutura.md",               "mensal",    date(2026, 9, 16)),
    ("Log de Disponibilidade",                  "Técnico",    "documentacao/evidencias/log_disponibilidade.md",                 "mensal",    date(2026, 9, 16)),

    # ── Certificados de terceiros ─────────────────────────────
    ("Cloudflare — SOC 2 Type II (2025)",       "Certificado","documentacao/evidencias/cloudflare_2025_type_2_soc_2_report.pdf",              "anual", date(2026, 9, 16)),
    ("Cloudflare — ISO 27001/27701 (2026)",     "Certificado","documentacao/evidencias/cloudflare_2026_iso_27001_27701_certificate.pdf",       "anual", date(2026, 9, 16)),
    ("Cloudflare — PCI DSS v4.0.1 (2026)",     "Certificado","documentacao/evidencias/cloudflare_pci_aocv_4.0.1_service_providers_march_2026.pdf","anual", date(2026, 9, 16)),
    ("Cloudflare — ISO 27001 (Applicability)", "Certificado","documentacao/evidencias/cloudflare_iso_27001_statement_of_applicability_v4.4.pdf","anual", date(2026, 9, 16)),
    ("Cloudflare — ISO 27701 (Applicability)", "Certificado","documentacao/evidencias/cloudflare_iso_27701_statement_of_applicability_v2.4.pdf","anual", date(2026, 9, 16)),
    ("Hostinger — ISO/IEC 27001:2022",         "Certificado","documentacao/evidencias/Hostinger ISO_IEC 27001_2022.pdf",                      "anual", date(2026, 9, 16)),
    ("Hostinger — Hosting Agreement",          "Certificado","documentacao/evidencias/Hosting agreement.pdf",                                  "anual", date(2026, 9, 16)),
]


def popular_banco(db: Session):
    if db.query(Documento).count() > 0:
        return
    for nome, cat, arquivo, period, ultima in DOCUMENTOS:
        db.add(Documento(
            nome=nome,
            categoria=cat,
            arquivo=arquivo,
            periodicidade=period,
            ultima_revisao=ultima,
        ))
    db.commit()
