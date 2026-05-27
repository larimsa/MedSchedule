/* ─────────────────────────────────────────────
   consultas.js — Lógica da seção Consultas
   ───────────────────────────────────────────── */

function renderConsultas(filtro) {
  const medico = getMedicoAtivo();
  if (!medico) return;

  const list  = document.getElementById('consult-list');
  const base  = getConsultasMedico(medico.id);
  const items = filtro === 'todas' ? base : base.filter(c => c.tipo === filtro);
  list.innerHTML = '';

  if (!items.length) {
    list.innerHTML = `
      <div class="empty-state">
        <i class="ti ti-calendar-off" aria-hidden="true"></i>
        <p>Nenhuma consulta encontrada para ${medico.nome}.</p>
      </div>`;
    return;
  }

  const sorted = [...items].sort((a,b) => a.data.localeCompare(b.data) || a.hora.localeCompare(b.hora));

  sorted.forEach(c => {
    const inits = initials(c.nome);
    const el = document.createElement('div');
    el.className = 'consult-item';
    el.setAttribute('role', 'listitem');
    el.innerHTML = `
      <div class="ci-left">
        <div class="ci-avatar">${inits}</div>
        <div>
          <div class="ci-name">${c.nome}</div>
          <div class="ci-detail">
            <i class="ti ti-calendar" style="font-size:12px;vertical-align:-1px" aria-hidden="true"></i>
            ${fmtDateShort(c.data)} · ${c.hora} · ${medico.esp}
            ${c.obs ? `<br><i class="ti ti-note" style="font-size:12px;vertical-align:-1px" aria-hidden="true"></i> ${c.obs}` : ''}
          </div>
        </div>
      </div>
      <div class="ci-right">
        <span class="badge ${c.tipo}">${capitalize(c.tipo)}</span>
        <button class="btn-danger" onclick="cancelarConsulta(${c.id})" aria-label="Cancelar consulta de ${c.nome}">
          <i class="ti ti-trash" aria-hidden="true"></i>
        </button>
      </div>`;
    list.appendChild(el);
  });
}

function filterConsultas(filtro, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderConsultas(filtro);
}

function cancelarConsulta(id) {
  consultas = consultas.filter(c => c.id !== id);
  const activeBtn = document.querySelector('.filter-btn.active');
  const filtro    = activeBtn ? activeBtn.textContent.trim().toLowerCase() : 'todas';
  renderConsultas(filtro === 'todas' ? 'todas' : filtro);
  renderAgenda();
  showToast('Consulta removida com sucesso.');
}
