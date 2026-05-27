/* ─────────────────────────────────────────────
   agenda.js — Lógica da seção Agenda
   ───────────────────────────────────────────── */

function renderAgenda() {
  const medico = getMedicoAtivo();
  if (!medico) return;

  document.getElementById('day-label').textContent = fmtDate(currentDate);

  const hoje     = isoDate(currentDate);
  const mesStr   = `${currentDate.getFullYear()}-${String(currentDate.getMonth()+1).padStart(2,'0')}`;
  const doMedico = getConsultasMedico(medico.id);
  const doHoje   = doMedico.filter(c => c.data === hoje).sort((a,b) => a.hora.localeCompare(b.hora));
  const doMes    = doMedico.filter(c => c.data.startsWith(mesStr));
  const retornos = doMedico.filter(c => c.tipo === 'retorno');

  document.getElementById('metric-hoje').textContent     = doHoje.length;
  document.getElementById('metric-hoje-sub').textContent = doHoje.length === 1 ? 'agendamento' : 'agendamentos';
  document.getElementById('metric-mes').textContent      = doMes.length;

  const retPct = doMedico.length ? Math.round(retornos.length / doMedico.length * 100) : 0;
  document.getElementById('metric-retorno').textContent  = retPct + '%';

  if (doHoje.length > 0) {
    document.getElementById('metric-proxima').textContent     = doHoje[0].hora;
    document.getElementById('metric-proxima-sub').textContent = doHoje[0].nome;
  } else {
    document.getElementById('metric-proxima').textContent     = '—';
    document.getElementById('metric-proxima-sub').textContent = 'sem consultas';
  }

  // Timeline
  const tl = document.getElementById('timeline');
  tl.innerHTML = '';

  HORARIOS_PADRAO.forEach(hora => {
    const appts = doHoje.filter(c => c.hora === hora);
    const slot  = document.createElement('div');
    slot.className = 'slot';
    slot.setAttribute('role', 'listitem');

    const timeEl = document.createElement('div');
    timeEl.className   = 'slot-time';
    timeEl.textContent = hora;

    const body = document.createElement('div');
    body.className = 'slot-body';

    if (appts.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'slot-empty';
      const line = document.createElement('div');
      line.className = 'slot-empty-line';
      empty.appendChild(line);
      body.appendChild(empty);
    } else {
      appts.forEach(a => {
        const el = document.createElement('div');
        el.className = `appt ${a.tipo}`;
        el.setAttribute('role', 'button');
        el.setAttribute('tabindex', '0');
        el.innerHTML = `
          <div class="appt-info">
            <div class="appt-name">${a.nome}</div>
            <div class="appt-detail">${medico.esp}${a.obs ? ' · ' + a.obs : ''}</div>
          </div>
          <span class="appt-badge">${capitalize(a.tipo)}</span>`;
        body.appendChild(el);
      });
    }

    slot.appendChild(timeEl);
    slot.appendChild(body);
    tl.appendChild(slot);
  });
}

function changeDay(delta) {
  currentDate.setDate(currentDate.getDate() + delta);
  renderAgenda();
}
