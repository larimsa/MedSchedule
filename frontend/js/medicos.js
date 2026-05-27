/* ─────────────────────────────────────────────
   medicos.js — Gerenciamento de médicos da clínica:
                listagem, adição, edição e remoção
   ───────────────────────────────────────────── */

// ──────────────────────────────────────────
//  SIDEBAR DE SELEÇÃO DE MÉDICO
// ──────────────────────────────────────────

/**
 * Renderiza a lista de médicos na sidebar.
 */
function renderSidebar() {
  const list = document.getElementById('sidebar-medicos');
  list.innerHTML = '';

  medicos.forEach(m => {
    const cor   = getCorMedico(m);
    const inits = initials(m.nome);
    const ativo = m.id === medicoAtivoId;

    const item = document.createElement('button');
    item.className = `sidebar-item${ativo ? ' active' : ''}`;
    item.setAttribute('aria-current', ativo ? 'true' : 'false');
    item.onclick = () => selecionarMedico(m.id);
    item.innerHTML = `
      <div class="sidebar-avatar" style="background:${cor.bg};color:${cor.text};border-color:${cor.border}">${inits}</div>
      <div class="sidebar-info">
        <div class="sidebar-nome">${m.nome}</div>
        <div class="sidebar-esp">${m.esp}</div>
      </div>
      ${ativo ? '<i class="ti ti-check sidebar-check" aria-hidden="true"></i>' : ''}`;
    list.appendChild(item);
  });
}

/**
 * Seleciona um médico como ativo e atualiza toda a interface.
 */
function selecionarMedico(id) {
  medicoAtivoId = id;
  const m = getMedicoAtivo();

  // Atualiza header
  document.getElementById('header-doctor-name').textContent = m.nome;
  document.getElementById('header-doctor-esp').textContent  = m.esp;

  // Re-render sidebar
  renderSidebar();

  // Atualiza seção ativa
  const secaoAtiva = document.querySelector('.section.active');
  if (secaoAtiva) {
    const id = secaoAtiva.id;
    if (id === 'agenda')    renderAgenda();
    if (id === 'consultas') { renderConsultas('todas'); resetFiltros(); }
    if (id === 'agendar')   { renderHorarios(); updatePreview(); }
    if (id === 'perfil')    renderPerfil();
  }
}

function resetFiltros() {
  document.querySelectorAll('.filter-btn').forEach((b,i) => b.classList.toggle('active', i === 0));
}

// ──────────────────────────────────────────
//  MODAL: ADICIONAR / EDITAR MÉDICO
// ──────────────────────────────────────────

let editandoMedicoId = null; // null = adicionando novo

function abrirModalMedico(medicoId = null) {
  editandoMedicoId = medicoId;
  const modal   = document.getElementById('modal-medico');
  const titulo  = document.getElementById('modal-titulo');

  if (medicoId !== null) {
    // Editar existente
    const m = medicos.find(m => m.id === medicoId);
    if (!m) return;
    titulo.textContent = 'Editar médico';
    document.getElementById('m-nome').value  = m.nome;
    document.getElementById('m-crm').value   = m.crm;
    document.getElementById('m-email').value = m.email;
    document.getElementById('m-tel').value   = m.tel;
    document.getElementById('m-end').value   = m.end;
    document.getElementById('m-hor').value   = m.hor;
    document.getElementById('m-esp').value   = m.esp;
    document.getElementById('btn-deletar-medico').style.display = 'flex';
  } else {
    // Novo médico
    titulo.textContent = 'Adicionar médico';
    ['m-nome','m-crm','m-email','m-tel','m-end','m-hor'].forEach(id => {
      document.getElementById(id).value = '';
    });
    document.getElementById('m-esp').selectedIndex = 0;
    document.getElementById('btn-deletar-medico').style.display = 'none';
  }

  modal.classList.add('open');
  document.getElementById('m-nome').focus();
}

function fecharModalMedico() {
  document.getElementById('modal-medico').classList.remove('open');
  editandoMedicoId = null;
}

function salvarModalMedico() {
  const nome  = document.getElementById('m-nome').value.trim();
  const crm   = document.getElementById('m-crm').value.trim();
  const email = document.getElementById('m-email').value.trim();
  const tel   = document.getElementById('m-tel').value.trim();
  const end   = document.getElementById('m-end').value.trim();
  const hor   = document.getElementById('m-hor').value.trim();
  const esp   = document.getElementById('m-esp').value;

  if (!nome) { showToast('Informe o nome do médico.', true); document.getElementById('m-nome').focus(); return; }
  if (!crm)  { showToast('Informe o CRM.', true); document.getElementById('m-crm').focus(); return; }

  if (editandoMedicoId !== null) {
    // Atualizar existente
    const idx = medicos.findIndex(m => m.id === editandoMedicoId);
    if (idx !== -1) {
      medicos[idx] = { ...medicos[idx], nome, crm, email, tel, end, hor, esp };
    }
    showToast(`${nome} atualizado(a)!`);

    // Se editou o médico ativo, atualiza header e re-render
    if (editandoMedicoId === medicoAtivoId) {
      selecionarMedico(medicoAtivoId);
    }
  } else {
    // Novo médico
    const novoCor = nextMedicoId % CORES_AVATAR.length;
    medicos.push({ id: nextMedicoId++, nome, crm, email, tel, end, hor, esp, cor: novoCor });
    showToast(`${nome} adicionado(a) à clínica!`);
  }

  fecharModalMedico();
  renderSidebar();
  renderEquipe();
}

function confirmarDeletarMedico() {
  if (editandoMedicoId === null) return;
  const m = medicos.find(m => m.id === editandoMedicoId);
  if (!m) return;

  if (medicos.length <= 1) {
    showToast('Não é possível remover o único médico da clínica.', true);
    return;
  }

  // Remove médico e suas consultas
  medicos  = medicos.filter(m => m.id !== editandoMedicoId);
  consultas = consultas.filter(c => c.medicoId !== editandoMedicoId);

  // Se era o ativo, selecionar o primeiro
  if (medicoAtivoId === editandoMedicoId) {
    selecionarMedico(medicos[0].id);
  }

  fecharModalMedico();
  renderSidebar();
  renderEquipe();
  showToast(`${m.nome} removido(a) da clínica.`);
}

// ──────────────────────────────────────────
//  SEÇÃO EQUIPE
// ──────────────────────────────────────────

/**
 * Renderiza o grid de cards de médicos na seção Equipe.
 */
function renderEquipe() {
  const grid = document.getElementById('equipe-grid');
  grid.innerHTML = '';

  medicos.forEach(m => {
    const cor   = getCorMedico(m);
    const inits = initials(m.nome);
    const total = getConsultasMedico(m.id).length;
    const ativo = m.id === medicoAtivoId;

    const card = document.createElement('div');
    card.className = `medico-card${ativo ? ' ativo' : ''}`;
    card.innerHTML = `
      <div class="medico-card-top">
        <div class="medico-avatar-lg" style="background:${cor.bg};color:${cor.text};border-color:${cor.border}">${inits}</div>
        <div class="medico-card-actions">
          <button class="btn-icon" onclick="abrirModalMedico(${m.id})" aria-label="Editar ${m.nome}">
            <i class="ti ti-edit" aria-hidden="true"></i>
          </button>
        </div>
      </div>
      <div class="medico-nome">${m.nome}</div>
      <div class="medico-esp-badge" style="background:${cor.bg};color:${cor.text}">${m.esp}</div>
      <div class="medico-meta">
        <span><i class="ti ti-id-badge" aria-hidden="true"></i> CRM ${m.crm}</span>
        <span><i class="ti ti-mail" aria-hidden="true"></i> ${m.email}</span>
        <span><i class="ti ti-phone" aria-hidden="true"></i> ${m.tel}</span>
        <span><i class="ti ti-clock" aria-hidden="true"></i> ${m.hor}</span>
      </div>
      <div class="medico-card-footer">
        <span class="medico-stat">${total} consulta${total !== 1 ? 's' : ''}</span>
        <button class="btn-secondary" style="font-size:12px;padding:6px 12px" onclick="selecionarMedico(${m.id}); showSection('agenda', document.querySelector('.nav-btn'))">
          ${ativo ? '<i class="ti ti-check" aria-hidden="true"></i> Selecionado' : '<i class="ti ti-calendar" aria-hidden="true"></i> Ver agenda'}
        </button>
      </div>`;
    grid.appendChild(card);
  });
}
