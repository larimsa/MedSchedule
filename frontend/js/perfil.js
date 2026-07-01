/* ─────────────────────────────────────────────
   perfil.js — Lógica da seção Perfil Médico
   ───────────────────────────────────────────── */

function renderPerfil() {
  const m = getMedicoAtivo();
  if (!m) return;

  const cor   = getCorMedico(m);
  const inits = initials(m.nome);

  // Avatar
  const av = document.getElementById('p-avatar');
  av.textContent  = inits;
  av.style.background  = cor.bg;
  av.style.color       = cor.text;
  av.style.borderColor = cor.border;

  // View mode
  document.getElementById('p-nome-view').textContent  = m.nome;
  document.getElementById('p-crm-view').textContent   = 'CRM ' + m.crm;
  document.getElementById('p-esp-view').textContent   = m.esp;
  document.getElementById('p-email-view').textContent = m.email;
  document.getElementById('p-tel-view').textContent   = m.tel;
  document.getElementById('p-end-view').textContent   = m.end;
  document.getElementById('p-hor-view').textContent   = m.hor;

  // Preenche form de edição
  document.getElementById('e-nome').value  = m.nome;
  document.getElementById('e-crm').value   = m.crm;
  document.getElementById('e-email').value = m.email;
  document.getElementById('e-tel').value   = m.tel;
  document.getElementById('e-end').value   = m.end;
  document.getElementById('e-hor').value   = m.hor;
  document.getElementById('e-esp').value   = m.esp;

  toggleEdit(false);
  renderStats();
}

function toggleEdit(on) {
  document.getElementById('view-mode').style.display = on ? 'none' : 'block';
  document.getElementById('edit-mode').style.display = on ? 'block' : 'none';
}

async function salvarPerfil() {
  const m = getMedicoAtivo();
  if (!m) return;

  const nome  = document.getElementById('e-nome').value.trim();
  const crm   = document.getElementById('e-crm').value.trim();
  const esp   = document.getElementById('e-esp').value;
  const email = document.getElementById('e-email').value.trim();
  const tel   = document.getElementById('e-tel').value.trim();
  const end   = document.getElementById('e-end').value.trim();
  const hor   = document.getElementById('e-hor').value.trim();

  try {
    const atualizado = await MedicosAPI.atualizar(m.id, {
      ...m, nome, crm, esp, email, tel, end, hor,
    });
    const idx = medicos.findIndex(med => med.id === m.id);
    if (idx !== -1) medicos[idx] = atualizado;

    document.getElementById('header-doctor-name').textContent = nome;
    document.getElementById('header-doctor-esp').textContent  = esp;

    renderSidebar();
    renderPerfil();
    showToast('Perfil atualizado com sucesso!');
  } catch (e) {
    showToast(e.message, true);
  }
}

function renderStats() {
  const m         = getMedicoAtivo();
  const container = document.getElementById('stats-container');
  if (!m || !container) return;

  const doMedico = getConsultasMedico(m.id);
  const total    = doMedico.length;
  const tipos    = [
    { key:'consulta', label:'Consultas', cls:'fill-green' },
    { key:'retorno',  label:'Retornos',  cls:'fill-blue'  },
    { key:'exame',    label:'Exames',    cls:'fill-amber'  },
  ];

  let html = '';
  tipos.forEach(t => {
    const n   = doMedico.filter(c => c.tipo === t.key).length;
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
