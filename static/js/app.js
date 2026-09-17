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
    return '<div class="doc-card ' + cls + '">' +
      '<div class="card-cat">' + d.categoria + '</div>' +
      '<div class="card-nome">' + d.nome + '</div>' +
      '<div class="card-meta">' +
        '<span class="card-period">' + d.periodicidade + '</span>' +
        '<span class="card-prazo ' + cls + '">' + prazo + '</span>' +
      '</div>' +
      '<div class="card-acoes">' +
        '<a href="/editar/' + d.id + '" class="btn-revisar">Revisar →</a>' +
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
    document.getElementById('topbar-title').textContent = 'Visão Geral';
    document.getElementById('filter-bar').style.display = 'flex';
    setFiltro(filtroAtual);
  }

  function toggleSec(btn, id) {
    var sec = document.getElementById(id);
    var chevron = btn.querySelector('.nav-chevron');
    var isOpen = sec.classList.contains('open');
    sec.classList.toggle('open', !isOpen);
    chevron.classList.toggle('open', !isOpen);
  }

  function toggleCat(btn, id, catNome) {
    var list = document.getElementById(id);
    var chevron = btn.querySelector('.nav-chevron');
    var isOpen = list.classList.contains('open');
    list.classList.toggle('open', !isOpen);
    chevron.classList.toggle('open', !isOpen);
    document.querySelectorAll('.nav-item').forEach(function (b) { b.classList.remove('active'); });
    btn.classList.add('active');
    if (!isOpen) {
      renderCategoria(catNome);
    } else {
      document.getElementById('filter-bar').style.display = 'flex';
      document.getElementById('topbar-title').textContent = 'Visão Geral';
      setFiltro(filtroAtual);
    }
  }

  /* ── Cards de categoria ── */
  function catCardHTML(d) {
    var cls = urgClass(d.dias);
    var prazo = prazoStr(d.dias, d.prazo_str);
    var statusMap = { vencido: 'Vencido', urgente: 'Urgente', breve: 'Vence em breve', ok: 'Em dia' };
    var statusLabel = statusMap[cls] || 'Em dia';
    return '<a class="cat-card cat-card-' + cls + '" href="/ver/' + d.id + '">' +
      '<div class="cat-card-body">' +
        '<div class="cat-card-nome">' + d.nome + '</div>' +
        '<div class="cat-card-meta">' +
          '<span class="cat-tag">' + d.periodicidade + '</span>' +
          '<span class="cat-prazo">' + prazo + '</span>' +
          '<span class="cat-status cat-status-' + cls + '">' + statusLabel + '</span>' +
        '</div>' +
      '</div>' +
      '<span class="cat-abrir">Abrir →</span>' +
    '</a>';
  }

  function renderCategoria(catNome) {
    var docs = DOCS.filter(function (d) { return d.categoria === catNome; });
    docs.sort(function (a, b) {
      var da = a.dias === null ? 9999 : a.dias;
      var db = b.dias === null ? 9999 : b.dias;
      return da - db;
    });
    var html = '<div class="cat-view">' +
      '<div class="secao-titulo">' +
        '<span class="secao-label muted">' + catNome.toUpperCase() + '</span>' +
        '<div class="secao-linha"></div>' +
        '<span style="font-size:12px;color:var(--muted)">' + docs.length + ' documento' + (docs.length !== 1 ? 's' : '') + '</span>' +
      '</div>' +
      '<div class="cat-lista">' +
        docs.map(catCardHTML).join('<div class="cat-sep"></div>') +
      '</div>' +
    '</div>';
    document.getElementById('content').innerHTML = html;
    document.getElementById('topbar-title').textContent = catNome;
    document.getElementById('filter-bar').style.display = 'none';
  }

  /* Expõe funções globais usadas pelo template */
  window.setFiltro       = setFiltro;
  window.navDash         = navDash;
  window.toggleSec       = toggleSec;
  window.toggleCat       = toggleCat;
  window.renderCategoria = renderCategoria;

  /* Init */
  atualizarBadges();
  renderDash(30);
}
