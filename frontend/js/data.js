/* ─────────────────────────────────────────────
   data.js — Estado global, constantes e utilitários
   (os dados de médicos/consultas vêm do backend agora)
   ───────────────────────────────────────────── */

// ──────────────────────────────────────────
//  CONSTANTES
// ──────────────────────────────────────────
const MESES = [
  'janeiro','fevereiro','março','abril','maio','junho',
  'julho','agosto','setembro','outubro','novembro','dezembro'
];
const MESES_SHORT = [
  'jan','fev','mar','abr','mai','jun',
  'jul','ago','set','out','nov','dez'
];
const SEMANA = [
  'Domingo','Segunda-feira','Terça-feira','Quarta-feira',
  'Quinta-feira','Sexta-feira','Sábado'
];
const HORARIOS_PADRAO = [
  '08:00','08:30','09:00','09:30','10:00','10:30',
  '11:00','11:30','14:00','14:30','15:00','15:30',
  '16:00','16:30','17:00','17:30'
];
const ESPECIALIDADES = [
  'Cardiologia','Dermatologia','Pediatria','Ortopedia',
  'Clínica Geral','Neurologia','Ginecologia','Oftalmologia',
  'Psiquiatria','Endocrinologia','Urologia','Reumatologia'
];
const CORES_AVATAR = [
  { bg:'#E1F5EE', text:'#085041', border:'#9FE1CB' },
  { bg:'#E6F1FB', text:'#042C53', border:'#B5D4F4' },
  { bg:'#FAEEDA', text:'#412402', border:'#FAC775' },
  { bg:'#FBEAF0', text:'#4B1528', border:'#F4C0D1' },
  { bg:'#EEEDFE', text:'#26215C', border:'#CECBF6' },
  { bg:'#EAF3DE', text:'#173404', border:'#C0DD97' },
];

// ──────────────────────────────────────────
//  ESTADO GLOBAL (preenchido pela API)
// ──────────────────────────────────────────
let currentDate = new Date();
currentDate.setHours(0,0,0,0);

let medicos       = [];   // [{id, nome, crm, esp, email, tel, end, hor, cor}]
let consultas     = [];   // [{id, medicoId, nome, email, tel, data, hora, tipo, obs}]
let medicoAtivoId = null;

// ──────────────────────────────────────────
//  CARREGAMENTO DO BACKEND
// ──────────────────────────────────────────

async function carregarMedicos() {
  try {
    medicos = await MedicosAPI.listar();
  } catch (e) {
    medicos = [];
    showToast('Não foi possível carregar médicos: ' + e.message, true);
  }
}

async function carregarConsultas() {
  try {
    consultas = await ConsultasAPI.listar();
  } catch (e) {
    consultas = [];
    showToast('Não foi possível carregar consultas: ' + e.message, true);
  }
}

// ──────────────────────────────────────────
//  UTILITÁRIOS
// ──────────────────────────────────────────

function isoDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function fmtDate(d) {
  return `${SEMANA[d.getDay()]}, ${d.getDate()} de ${MESES[d.getMonth()]}`;
}

function fmtDateShort(iso) {
  const d = new Date(iso + 'T00:00:00');
  return `${d.getDate()} ${MESES_SHORT[d.getMonth()]}`;
}

function initials(nome) {
  return (nome || '').replace(/^Dr[a]?\.\s*/i,'').split(' ').filter(Boolean).slice(0,2).map(n => n[0]).join('').toUpperCase();
}

function capitalize(str) {
  return (str || '').charAt(0).toUpperCase() + (str || '').slice(1);
}

function getMedicoAtivo() {
  return medicos.find(m => m.id === medicoAtivoId);
}

function getConsultasMedico(medicoId) {
  return consultas.filter(c => c.medicoId === medicoId);
}

function getHorariosLivres(dataISO, medicoId, limite = 6) {
  const ocupados = consultas.filter(c => c.medicoId === medicoId && c.data === dataISO).map(c => c.hora);
  return HORARIOS_PADRAO.filter(h => !ocupados.includes(h)).slice(0, limite);
}

function getCorMedico(medico) {
  return CORES_AVATAR[(medico.cor || 0) % CORES_AVATAR.length];
}
