/* ─────────────────────────────────────────────
   app.js — Inicialização e controle de navegação
   ───────────────────────────────────────────── */

/**
 * Exibe uma seção e oculta as demais.
 * Executa o render da seção ao ativar.
 * @param {string}      id  - ID da seção alvo
 * @param {HTMLElement} btn - Botão de navegação clicado
 */
function showSection(id, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.remove('active');
    b.removeAttribute('aria-current');
  });

  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
  btn.setAttribute('aria-current', 'page');

  // Render específico por seção
  if (id === 'agenda')    renderAgenda();
  if (id === 'consultas') renderConsultas('todas');
  if (id === 'agendar')   { renderHorarios(); updatePreview(); }
  if (id === 'perfil')    renderStats();
}

// ──────────────────────────────────────────
//  INICIALIZAÇÃO
// ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderAgenda();
  renderHorarios();
});
