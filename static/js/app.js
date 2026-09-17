/* ── Modal ── */
function abrirModal(id, nome, versaoSugerida) {
  document.getElementById('modal-titulo').textContent = 'Revisar: ' + nome;
  document.getElementById('modal-versao').value = versaoSugerida || '1.0';
  document.getElementById('modal-notas').value = '';
  document.getElementById('modal-form').action = '/revisar/' + id;
  document.getElementById('modal').classList.add('aberto');
  document.getElementById('modal-versao').focus();
}

function fecharModal(e) {
  if (e && e.target !== document.getElementById('modal')) return;
  document.getElementById('modal').classList.remove('aberto');
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') document.getElementById('modal').classList.remove('aberto');
});

/* ── Dashboard (só existe em dashboard.html) ── */
if (typeof DOCS !== 'undefined') {
  let filtroAtual = 30;

  function urgClass(dias) {
    if (dias === null || dias === undefined) return 'ok';
    if (dias < 0)   return 'vencido';
    if (dias <= 14) return 'urgente';
    if (dias <= 30) return 'breve';
    return 'ok';
  }

  function prazoStr(dias, prazoStr) {
    return prazoStr || (dias === null ? '—' : dias < 0
      ? 'Vencido há ' + Math.abs(dias) + ' dias'
      : 'Em ' + dias + ' dias');
  }

  function countPara(janela) {
    if (janela === 0) return DOCS.length;
    return DOCS.filter(function (d) {
      return d.dias !== null && d.dias <= janela;
    }).length;
  }

  function temAlerta(janela) {
    var docsJanela = janela === 0 ? DOCS : DOCS.filter(function (d) {
      return d.dias !== null && d.dias <= janela;
    });
    return docsJanela.some(function (d) { return d.dias === null || d.dias <= 30; });
  }

  function atualizarBadges() {
    [7, 30, 90, 0].forEach(function (v) {
      var key = String(v);
      document.getElementById('c' + key).textContent = countPara(v);
      var btn = document.getElementById('f' + key);
      btn.classList.toggle('alerta', temAlerta(v) && countPara(v) > 0);
    });
  }

  function cardHTML(d) {
    var cls = urgClass(d.dias);
    var prazo = prazoStr(d.dias, d.prazo_str);
    var btnAbrir = d.tem_arquivo
      ? '<a href="/abrir/' + d.id + '" class="btn-ver" title="Abrir no editor">✏</a>'
      : '';
    return '<div class="doc-card ' + cls + '">' +
      '<div class="card-cat">' + d.categoria + '</div>' +
      '<div class="card-nome">' + d.nome + '</div>' +
      '<div class="card-meta">' +
        '<span class="card-period">' + d.periodicidade + '</span>' +
        '<span class="card-prazo ' + cls + '">' + prazo + '</span>' +
      '</div>' +
      '<div class="card-acoes">' +
        '<button class="btn-revisar" onclick="abrirModal(' + d.id + ',\'' +
          d.nome.replace(/'/g, "\\'") + '\',\'' + d.proxima_versao + '\')">Revisar →</button>' +
        btnAbrir +
        '<a href="/ver/' + d.id + '" class="btn-ver" target="_blank">↗</a>' +
      '</div>' +
    '</div>';
  }

  function listaHTML(d) {
    return '<div class="lista-row">' +
      '<span class="lista-cat">' + d.categoria + '</span>' +
      '<span class="lista-nome">' + d.nome + '</span>' +
      '<span class="lista-versao">v' + d.versao + '</span>' +
      '<span class="lista-prazo verde">' + d.prazo_str + '</span>' +
    '</div>';
  }

  function renderDash(janela) {
    var todos = DOCS.slice().sort(function (a, b) {
      var da = a.dias === null ? 9999 : a.dias;
      var db = b.dias === null ? 9999 : b.dias;
      return da - db;
    });

    var visiveis = janela === 0 ? todos : todos.filter(function (d) {
      return d.dias !== null && d.dias <= janela;
    });

    var vencidos  = visiveis.filter(function (d) { return d.dias !== null && d.dias < 0; });
    var breve     = visiveis.filter(function (d) { return d.dias !== null && d.dias >= 0 && d.dias <= 30; });
    var restante  = visiveis.filter(function (d) { return d.dias === null || d.dias > 30; });

    var html = '';

    if (vencidos.length) {
      html += '<div><div class="secao-titulo">' +
        '<span class="secao-label red">Vencidos</span><div class="secao-linha"></div></div>' +
        '<div class="cards-grid">' + vencidos.map(cardHTML).join('') + '</div></div>';
    }

    if (breve.length) {
      html += '<div><div class="secao-titulo">' +
        '<span class="secao-label amber">Vence em breve</span><div class="secao-linha"></div></div>' +
        '<div class="cards-grid">' + breve.map(cardHTML).join('') + '</div></div>';
    }

    if (restante.length && janela > 30 && janela !== 0) {
      html += '<div><div class="secao-titulo">' +
        '<span class="secao-label muted">Próximos ' + janela + ' dias</span><div class="secao-linha"></div></div>' +
        '<div class="cards-grid">' + restante.map(cardHTML).join('') + '</div></div>';
    }

    if (restante.length && janela === 0) {
      html += '<div><div class="secao-titulo">' +
        '<span class="secao-label muted">Todos em dia</span><div class="secao-linha"></div></div>' +
        '<div class="lista-compacta">' + restante.map(listaHTML).join('') + '</div></div>';
    }

    if (!vencidos.length && !breve.length) {
      var proximos30 = DOCS.filter(function (d) { return d.dias !== null && d.dias >= 0 && d.dias <= 30; }).length;
      var hint = proximos30 > 0 && janela !== 30
        ? '<button class="estado-limpo-hint" onclick="setFiltro(30)">Ver ' + proximos30 +
          ' documento' + (proximos30 > 1 ? 's' : '') + ' que venc' +
          (proximos30 > 1 ? 'em' : 'e') + ' nos próximos 30 dias →</button>'
        : '';
      html += '<div class="estado-limpo">' +
        '<div class="estado-limpo-ico">✓</div>' +
        '<div class="estado-limpo-t">Nenhum alerta' + (janela > 0 ? ' nos próximos ' + janela + ' dias' : '') + '</div>' +
        '<div class="estado-limpo-sub">Todos os ' + DOCS.length + ' documentos estão dentro do prazo.</div>' +
        hint +
      '</div>';
    }

    document.getElementById('content').innerHTML = html;
  }

  function setFiltro(janela) {
    filtroAtual = janela;
    [7, 30, 90, 0].forEach(function (v) {
      document.getElementById('f' + v).classList.toggle('on', v === janela);
    });
    renderDash(janela);
  }

  function navDash(btn) {
    document.querySelectorAll('.nav-item').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active');
    document.getElementById('topbar-title').textContent = 'Dashboard';
    document.getElementById('filter-bar').style.display = 'flex';
    setFiltro(filtroAtual);
  }

  function toggleCat(btn, id) {
    var list = document.getElementById(id);
    var chevron = btn.querySelector('.nav-chevron');
    var isOpen = list.classList.contains('open');
    list.classList.toggle('open', !isOpen);
    chevron.classList.toggle('open', !isOpen);
    document.querySelectorAll('.nav-item').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active');
  }

  /* Expõe funções globais usadas pelo template */
  window.setFiltro   = setFiltro;
  window.navDash     = navDash;
  window.toggleCat   = toggleCat;

  /* Init */
  atualizarBadges();
  renderDash(30);
}
