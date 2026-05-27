/* ─────────────────────────────────────────────
   perfil.js — Lógica da seção Perfil Médico
   ───────────────────────────────────────────── */

/**
 * Alterna entre modo visualização e modo edição do perfil.
 * @param {boolean} on - true = modo edição, false = modo visualização
 */
function toggleEdit(on) {
  document.getElementById('view-mode').style.display = on ? 'none' : 'block';
  document.getElementById('edit-mode').style.display = on ? 'block' : 'none';
}

/**
 * Salva as alterações do formulário de edição e atualiza a visualização.
 */
function salvarPerfil() {
  const nome  = document.getElementById('e-nome').value.trim();
  const crm   = document.getElementById('e-crm').value.trim();
  const esp   = document.getElementById('e-esp').value;
  const email = document.getElementById('e-email').value.trim();
  const tel   = document.getElementById('e-tel').value.trim();
  const end   = document.getElementById('e-end').value.trim();
  const hor   = document.getElementById('e-hor').value.trim();

  // Atualiza campos de visualização
  document.getElementById('p-nome-view').textContent  = nome;
  document.getElementById('p-crm-view').textContent   = 'CRM ' + crm;
  document.getElementById('p-esp-view').textContent   = esp;
  document.getElementById('p-email-view').textContent = email;
  document.getElementById('p-tel-view').textContent   = tel;
  document.getElementById('p-end-view').textContent   = end;
  document.getElementById('p-hor-view').textContent   = hor;

  // Atualiza avatar e header
  const nomeSimples = nome.replace(/^Dr[a]?\.\s*/i, '');
  document.getElementById('p-avatar').textContent           = initials(nomeSimples);
  document.getElementById('header-doctor-name').textContent = nome;

  toggleEdit(false);
  showToast('Perfil atualizado com sucesso!');
}

/**
 * Renderiza as estatísticas de consultas do mês no painel do perfil.
 */
function renderStats() {
  const container = document.getElementById('stats-container');
  const total     = consultas.length;

  const tipos = [
    { key: 'consulta', label: 'Consultas', cls: 'fill-green' },
    { key: 'retorno',  label: 'Retornos',  cls: 'fill-blue'  },
    { key: 'exame',    label: 'Exames',    cls: 'fill-amber'  },
  ];

  let html = '';

  tipos.forEach(t => {
    const n   = consultas.filter(c => c.tipo === t.key).length;
    const pct = total > 0 ? Math.round(n / total * 100) : 0;
    html += `
      <div class="stat-row">
        <div class="stat-row-top">
          <span class="stat-label">${t.label}</span>
          <span class="stat-value">${n}<span class="stat-pct">(${pct}%)</span></span>
        </div>
        <div class="progress-track">
          <div class="progress-fill ${t.cls}" style="width:${pct}%"></div>
        </div>
      </div>`;
  });

  html += `
    <div class="stat-total">
      <span class="stat-total-label">
        <i class="ti ti-users" style="font-size:16px;vertical-align:-2px" aria-hidden="true"></i>
        Total de pacientes
      </span>
      <span class="stat-total-val">${total}</span>
    </div>`;

  container.innerHTML = html;
}
