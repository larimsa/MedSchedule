/* ─────────────────────────────────────────────
   agenda.js — Lógica da seção Agenda
   ───────────────────────────────────────────── */

/**
 * Renderiza a agenda do dia atual (currentDate).
 * Atualiza métricas e timeline.
 */
function renderAgenda() {
  document.getElementById('day-label').textContent = fmtDate(currentDate);

  const hoje   = isoDate(currentDate);
  const doHoje = consultas.filter(c => c.data === hoje).sort((a, b) => a.hora.localeCompare(b.hora));
  const mes    = `${currentDate.getFullYear()}-${String(currentDate.getMonth()+1).padStart(2,'0')}`;
  const doMes  = consultas.filter(c => c.data.startsWith(mes));
  const retornos = consultas.filter(c => c.tipo === 'retorno');

  // Métricas
  document.getElementById('metric-hoje').textContent      = doHoje.length;
  document.getElementById('metric-hoje-sub').textContent  = doHoje.length === 1 ? 'agendamento' : 'agendamentos';
  document.getElementById('metric-mes').textContent       = doMes.length;

  const retPct = consultas.length ? Math.round(retornos.length / consultas.length * 100) : 0;
  document.getElementById('metric-retorno').textContent   = retPct + '%';

  if (doHoje.length > 0) {
    const prox = doHoje[0];
    document.getElementById('metric-proxima').textContent     = prox.hora;
    document.getElementById('metric-proxima-sub').textContent = prox.nome;
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
        el.setAttribute('aria-label', `${a.nome} - ${a.tipo} às ${a.hora}`);
        el.innerHTML = `
          <div class="appt-info">
            <div class="appt-name">${a.nome}</div>
            <div class="appt-detail">${a.esp}${a.obs ? ' · ' + a.obs : ''}</div>
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

/**
 * Avança ou recua um dia na agenda.
 * @param {number} delta - +1 próximo, -1 anterior
 */
function changeDay(delta) {
  currentDate.setDate(currentDate.getDate() + delta);
  renderAgenda();
}
