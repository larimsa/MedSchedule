/* ─────────────────────────────────────────────
   toast.js — Notificações temporárias (toast)
   ───────────────────────────────────────────── */

let toastTimeout = null;

/**
 * Exibe uma notificação temporária na tela.
 * @param {string}  msg     - Mensagem a exibir
 * @param {boolean} isError - true = vermelho (erro), false = verde (sucesso)
 */
function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  const icon  = document.getElementById('toast-icon');
  const text  = document.getElementById('toast-msg');

  toast.className   = `toast ${isError ? 'error' : 'success'}`;
  icon.className    = `ti ${isError ? 'ti-alert-circle' : 'ti-check'}`;
  text.textContent  = msg;

  toast.classList.add('show');

  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.remove('show'), 3000);
}
