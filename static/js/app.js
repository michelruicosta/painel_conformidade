function abrirModal(id, nome, status, notas, proximaRevisao) {
  document.getElementById('modal-titulo').textContent = nome;
  document.getElementById('modal-form').action = `/controles/${id}/editar`;
  document.querySelector(`input[name=status][value="${status}"]`).checked = true;
  document.getElementById('input-notas').value = notas || '';
  document.getElementById('input-revisao').value = proximaRevisao || '';
  document.getElementById('modal').classList.add('aberto');
}

function fecharModal(event) {
  if (!event || event.target === document.getElementById('modal')) {
    document.getElementById('modal').classList.remove('aberto');
  }
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') fecharModal();
});
