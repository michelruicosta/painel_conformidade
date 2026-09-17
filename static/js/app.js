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

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') document.getElementById('modal').classList.remove('aberto');
});
