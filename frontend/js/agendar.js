/* ─────────────────────────────────────────────
   agendar.js — Lógica do formulário de
                agendamento de consultas
   ───────────────────────────────────────────── */

/**
 * Renderiza os horários disponíveis no painel lateral.
 * Usa a data selecionada no formulário, ou hoje.
 */
function renderHorarios() {
  const container = document.getElementById('horarios-container');
  const dataSel   = document.getElementById('f-data').value || isoDate(new Date());
  const livres    = getHorariosLivres(dataSel);

  container.innerHTML = '';

  if (!livres.length) {
    container.innerHTML = '<p style="font-size:13px;color:var(--text-faint);">Sem horários disponíveis neste dia.</p>';
    return;
  }

  livres.forEach(h => {
    const el = document.createElement('div');
    el.className = 'horario-item';
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');
    el.setAttribute('aria-label', `Selecionar horário ${h}`);
    el.innerHTML = `
      <span class="horario-item-time">
        <i class="ti ti-clock" style="font-size:14px;vertical-align:-2px" aria-hidden="true"></i> ${h}
      </span>
      <span class="horario-item-tag">disponível</span>`;

    el.onclick = () => {
      document.getElementById('f-data').value = dataSel;
      document.getElementById('f-hora').value = h;
      updatePreview();
    };

    el.onkeydown = (e) => { if (e.key === 'Enter' || e.key === ' ') el.click(); };
    container.appendChild(el);
  });
}

/**
 * Atualiza o box de pré-visualização com os dados do formulário.
 */
function updatePreview() {
  const nome = document.getElementById('f-nome').value.trim();
  const data = document.getElementById('f-data').value;
  const hora = document.getElementById('f-hora').value;
  const tipo = document.getElementById('f-tipo').value;
  const esp  = document.getElementById('f-esp').value;
  const obs  = document.getElementById('f-obs').value.trim();
  const cont = document.getElementById('preview-container');

  if (!nome && !data) {
    cont.innerHTML = '<p style="font-size:13px;color:var(--text-faint);text-align:center;padding:1rem 0">Preencha os campos ao lado para visualizar o resumo.</p>';
    return;
  }

  cont.innerHTML = `
    <div class="preview-box">
      <div class="preview-row">
        <span class="preview-label">Paciente</span>
        <span class="preview-val">${nome || '–'}</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">Data</span>
        <span class="preview-val">${data ? fmtDateShort(data) : '–'}</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">Horário</span>
        <span class="preview-val">${hora || '–'}</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">Tipo</span>
        <span class="preview-val">${capitalize(tipo)}</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">Especialidade</span>
        <span class="preview-val">${esp}</span>
      </div>
      ${obs ? `
      <div class="preview-row">
        <span class="preview-label">Observações</span>
        <span class="preview-val" style="max-width:60%;text-align:right">${obs}</span>
      </div>` : ''}
    </div>`;
}

/**
 * Valida e salva um novo agendamento.
 */
function agendarConsulta() {
  const nome  = document.getElementById('f-nome').value.trim();
  const email = document.getElementById('f-email').value.trim();
  const tel   = document.getElementById('f-tel').value.trim();
  const data  = document.getElementById('f-data').value;
  const hora  = document.getElementById('f-hora').value;
  const tipo  = document.getElementById('f-tipo').value;
  const esp   = document.getElementById('f-esp').value;
  const obs   = document.getElementById('f-obs').value.trim();

  // Validações
  if (!nome) { showToast('Informe o nome do paciente.', true); document.getElementById('f-nome').focus(); return; }
  if (!data) { showToast('Selecione uma data.', true); document.getElementById('f-data').focus(); return; }
  if (!hora) { showToast('Selecione um horário.', true); document.getElementById('f-hora').focus(); return; }

  const conflito = consultas.find(c => c.data === data && c.hora === hora);
  if (conflito) { showToast(`Horário ${hora} já está ocupado!`, true); return; }

  consultas.push({ id: nextId++, nome, email, tel, data, hora, tipo, esp, obs });
  showToast(`Consulta de ${nome} agendada com sucesso!`);
  limparForm();
  renderHorarios();
}

/**
 * Limpa todos os campos do formulário.
 */
function limparForm() {
  ['f-nome','f-email','f-tel','f-data','f-hora','f-obs'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('f-tipo').selectedIndex = 0;
  document.getElementById('f-esp').selectedIndex  = 0;
  document.getElementById('preview-container').innerHTML =
    '<p style="font-size:13px;color:var(--text-faint);text-align:center;padding:1rem 0">Preencha os campos ao lado para visualizar o resumo.</p>';
}
