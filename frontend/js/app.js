/* ─────────────────────────────────────────────
   app.js — Inicialização e controle de navegação
   ───────────────────────────────────────────── */

function showSection(id, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.remove('active');
    b.removeAttribute('aria-current');
  });

  document.getElementById(id).classList.add('active');
  if (btn) { btn.classList.add('active'); btn.setAttribute('aria-current', 'page'); }

  if (id === 'agenda')    renderAgenda();
  if (id === 'consultas') { renderConsultas('todas'); resetFiltros(); }
  if (id === 'agendar')   { renderHorarios(); updatePreview(); }
  if (id === 'perfil')    renderPerfil();
  if (id === 'equipe')    renderEquipe();
}

// Fecha modal ao clicar no overlay
document.addEventListener('click', (e) => {
  const modal = document.getElementById('modal-medico');
  if (e.target === modal) fecharModalMedico();
});

// Fecha modal com Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') fecharModalMedico();
});

// ──────────────────────────────────────────
//  INICIALIZAÇÃO
// ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const m = getMedicoAtivo();
  if (m) {
    document.getElementById('header-doctor-name').textContent = m.nome;
    document.getElementById('header-doctor-esp').textContent  = m.esp;
  }

  renderSidebar();
  renderAgenda();
  renderHorarios();
});
