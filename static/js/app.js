function abrirModal(id, nome, notas) {
  document.getElementById('modal-titulo').textContent = nome;
  document.getElementById('modal-notas').value = notas || '';
  document.getElementById('modal-form').action = '/revisar/' + id;
  document.getElementById('modal').classList.add('aberto');
}

function fecharModal(e) {
  if (e && e.target !== document.getElementById('modal')) return;
  document.getElementById('modal').classList.remove('aberto');
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') document.getElementById('modal').classList.remove('aberto');
});
