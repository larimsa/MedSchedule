/* ─────────────────────────────────────────────
   data.js — Estado global, dados iniciais
             e funções utilitárias
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

// ──────────────────────────────────────────
//  ESTADO GLOBAL
// ──────────────────────────────────────────
let currentDate = new Date();
currentDate.setHours(0,0,0,0);

let nextId = 10;

let consultas = [
  { id:1, nome:'João Silva',     email:'joao@email.com',  tel:'(11) 91111-1111', data:'2026-05-27', hora:'09:00', tipo:'consulta', esp:'Cardiologia', obs:'' },
  { id:2, nome:'Maria Oliveira', email:'maria@email.com', tel:'(11) 92222-2222', data:'2026-05-27', hora:'10:30', tipo:'retorno',  esp:'Cardiologia', obs:'Resultado de exame pendente' },
  { id:3, nome:'Pedro Santos',   email:'pedro@email.com', tel:'(11) 93333-3333', data:'2026-05-27', hora:'14:00', tipo:'exame',    esp:'Cardiologia', obs:'' },
  { id:4, nome:'Ana Lima',       email:'ana@email.com',   tel:'(11) 94444-4444', data:'2026-05-27', hora:'15:30', tipo:'consulta', esp:'Cardiologia', obs:'Primeira consulta' },
  { id:5, nome:'Carlos Rocha',   email:'carlos@email.com',tel:'(11) 95555-5555', data:'2026-05-28', hora:'09:00', tipo:'retorno',  esp:'Cardiologia', obs:'' },
  { id:6, nome:'Beatriz Costa',  email:'bea@email.com',   tel:'(11) 96666-6666', data:'2026-05-28', hora:'11:00', tipo:'consulta', esp:'Cardiologia', obs:'' },
  { id:7, nome:'Lucas Ferreira', email:'lucas@email.com', tel:'(11) 97777-7777', data:'2026-05-29', hora:'10:00', tipo:'exame',    esp:'Cardiologia', obs:'Eletro + eco' },
];

// ──────────────────────────────────────────
//  UTILITÁRIOS
// ──────────────────────────────────────────

/**
 * Converte um objeto Date para string "YYYY-MM-DD"
 */
function isoDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

/**
 * Formata data por extenso: "Quinta-feira, 27 de maio"
 */
function fmtDate(d) {
  return `${SEMANA[d.getDay()]}, ${d.getDate()} de ${MESES[d.getMonth()]}`;
}

/**
 * Formata data curta a partir de string ISO: "27 mai"
 */
function fmtDateShort(iso) {
  const d = new Date(iso + 'T00:00:00');
  return `${d.getDate()} ${MESES_SHORT[d.getMonth()]}`;
}

/**
 * Gera iniciais de até 2 palavras de um nome
 */
function initials(nome) {
  return nome.split(' ').filter(Boolean).slice(0,2).map(n => n[0]).join('').toUpperCase();
}

/**
 * Capitaliza primeira letra de uma string
 */
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Retorna horários disponíveis para uma data
 */
function getHorariosLivres(dataISO, limite = 6) {
  const ocupados = consultas.filter(c => c.data === dataISO).map(c => c.hora);
  return HORARIOS_PADRAO.filter(h => !ocupados.includes(h)).slice(0, limite);
}
