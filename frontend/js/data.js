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
//  ESTADO GLOBAL
// ──────────────────────────────────────────
let currentDate = new Date();
currentDate.setHours(0,0,0,0);

let nextMedicoId  = 10;
let nextConsultaId = 30;

// Médico ativo (ID)
let medicoAtivoId = 1;

// Lista de médicos da clínica
let medicos = [
  {
    id: 1, nome: 'Dr. Carlos Mendes', crm: '123456-SP',
    esp: 'Cardiologia', email: 'carlos@medschedule.com',
    tel: '(11) 99999-9999', end: 'Av. Paulista, 1000 — SP',
    hor: 'Seg–Sex, 08h–18h', cor: 0
  },
  {
    id: 2, nome: 'Dra. Fernanda Lima', crm: '234567-SP',
    esp: 'Dermatologia', email: 'fernanda@medschedule.com',
    tel: '(11) 98888-8888', end: 'Av. Paulista, 1000 — SP',
    hor: 'Seg–Sex, 09h–17h', cor: 1
  },
  {
    id: 3, nome: 'Dr. Rafael Souza', crm: '345678-SP',
    esp: 'Pediatria', email: 'rafael@medschedule.com',
    tel: '(11) 97777-7777', end: 'Av. Paulista, 1000 — SP',
    hor: 'Seg–Sex, 08h–16h', cor: 2
  },
  {
    id: 4, nome: 'Dra. Camila Torres', crm: '456789-SP',
    esp: 'Neurologia', email: 'camila@medschedule.com',
    tel: '(11) 96666-6666', end: 'Av. Paulista, 1000 — SP',
    hor: 'Ter–Sáb, 10h–18h', cor: 3
  },
  {
    id: 5, nome: 'Dr. André Oliveira', crm: '567890-SP',
    esp: 'Ortopedia', email: 'andre@medschedule.com',
    tel: '(11) 95555-5555', end: 'Av. Paulista, 1000 — SP',
    hor: 'Seg–Sex, 07h–15h', cor: 4
  },
  {
    id: 6, nome: 'Dra. Juliana Rocha', crm: '678901-SP',
    esp: 'Ginecologia', email: 'juliana@medschedule.com',
    tel: '(11) 94444-4444', end: 'Av. Paulista, 1000 — SP',
    hor: 'Seg–Sex, 08h–18h', cor: 5
  },
];

// Consultas (com medicoId)
let consultas = [
  // Dr. Carlos Mendes — Cardiologia
  { id:1,  medicoId:1, nome:'João Silva',       email:'joao@email.com',    tel:'(11) 91111-1111', data:'2026-05-27', hora:'09:00', tipo:'consulta', obs:'' },
  { id:2,  medicoId:1, nome:'Maria Oliveira',   email:'maria@email.com',   tel:'(11) 92222-2222', data:'2026-05-27', hora:'10:30', tipo:'retorno',  obs:'Resultado de exame pendente' },
  { id:3,  medicoId:1, nome:'Pedro Santos',     email:'pedro@email.com',   tel:'(11) 93333-3333', data:'2026-05-27', hora:'14:00', tipo:'exame',    obs:'' },
  { id:4,  medicoId:1, nome:'Ana Lima',         email:'ana@email.com',     tel:'(11) 94444-4444', data:'2026-05-27', hora:'15:30', tipo:'consulta', obs:'Primeira consulta' },
  { id:5,  medicoId:1, nome:'Carlos Rocha',     email:'carlos@email.com',  tel:'(11) 95555-5555', data:'2026-05-28', hora:'09:00', tipo:'retorno',  obs:'' },
  { id:6,  medicoId:1, nome:'Beatriz Costa',    email:'bea@email.com',     tel:'(11) 96666-6666', data:'2026-05-28', hora:'11:00', tipo:'consulta', obs:'' },
  { id:7,  medicoId:1, nome:'Lucas Ferreira',   email:'lucas@email.com',   tel:'(11) 97777-7777', data:'2026-05-29', hora:'10:00', tipo:'exame',    obs:'Eletro + eco' },

  // Dra. Fernanda Lima — Dermatologia
  { id:8,  medicoId:2, nome:'Isabela Neves',    email:'isa@email.com',     tel:'(11) 91212-1212', data:'2026-05-27', hora:'09:30', tipo:'consulta', obs:'Mancha suspeita no braço' },
  { id:9,  medicoId:2, nome:'Roberto Alves',    email:'rob@email.com',     tel:'(11) 91313-1313', data:'2026-05-27', hora:'11:00', tipo:'retorno',  obs:'' },
  { id:10, medicoId:2, nome:'Patrícia Duarte',  email:'pat@email.com',     tel:'(11) 91414-1414', data:'2026-05-27', hora:'14:30', tipo:'consulta', obs:'' },
  { id:11, medicoId:2, nome:'Thiago Campos',    email:'thiago@email.com',  tel:'(11) 91515-1515', data:'2026-05-28', hora:'10:00', tipo:'exame',    obs:'Biópsia de pele' },
  { id:12, medicoId:2, nome:'Larissa Monteiro', email:'lari@email.com',    tel:'(11) 91616-1616', data:'2026-05-29', hora:'15:00', tipo:'consulta', obs:'' },

  // Dr. Rafael Souza — Pediatria
  { id:13, medicoId:3, nome:'Sofia Mendes',     email:'sofia@email.com',   tel:'(11) 91717-1717', data:'2026-05-27', hora:'08:30', tipo:'consulta', obs:'Febre persistente' },
  { id:14, medicoId:3, nome:'Miguel Azevedo',   email:'mig@email.com',     tel:'(11) 91818-1818', data:'2026-05-27', hora:'10:00', tipo:'retorno',  obs:'Pós-vacinação' },
  { id:15, medicoId:3, nome:'Laura Barros',     email:'laura@email.com',   tel:'(11) 91919-1919', data:'2026-05-27', hora:'14:00', tipo:'consulta', obs:'' },
  { id:16, medicoId:3, nome:'Davi Carvalho',    email:'davi@email.com',    tel:'(11) 92020-2020', data:'2026-05-28', hora:'09:00', tipo:'exame',    obs:'Hemograma' },
  { id:17, medicoId:3, nome:'Alice Ribeiro',    email:'alice@email.com',   tel:'(11) 92121-2121', data:'2026-05-28', hora:'11:00', tipo:'consulta', obs:'Primeira consulta' },

  // Dra. Camila Torres — Neurologia
  { id:18, medicoId:4, nome:'Marcelo Pinto',    email:'marcelo@email.com', tel:'(11) 92222-2222', data:'2026-05-27', hora:'10:00', tipo:'consulta', obs:'Enxaqueca crônica' },
  { id:19, medicoId:4, nome:'Renata Faria',     email:'renata@email.com',  tel:'(11) 92323-2323', data:'2026-05-27', hora:'14:30', tipo:'retorno',  obs:'' },
  { id:20, medicoId:4, nome:'Paulo Gonçalves',  email:'paulo@email.com',   tel:'(11) 92424-2424', data:'2026-05-28', hora:'10:30', tipo:'exame',    obs:'EEG agendado' },
  { id:21, medicoId:4, nome:'Cristina Moura',   email:'cris@email.com',    tel:'(11) 92525-2525', data:'2026-05-29', hora:'14:00', tipo:'consulta', obs:'' },

  // Dr. André Oliveira — Ortopedia
  { id:22, medicoId:5, nome:'Gustavo Leal',     email:'gus@email.com',     tel:'(11) 92626-2626', data:'2026-05-27', hora:'08:00', tipo:'consulta', obs:'Dor no joelho' },
  { id:23, medicoId:5, nome:'Fernanda Braga',   email:'fern2@email.com',   tel:'(11) 92727-2727', data:'2026-05-27', hora:'11:30', tipo:'retorno',  obs:'Pós-operatório' },
  { id:24, medicoId:5, nome:'Rodrigo Cunha',    email:'rod@email.com',     tel:'(11) 92828-2828', data:'2026-05-28', hora:'09:30', tipo:'exame',    obs:'Raio-X coluna' },
  { id:25, medicoId:5, nome:'Aline Correia',    email:'aline@email.com',   tel:'(11) 92929-2929', data:'2026-05-28', hora:'14:00', tipo:'consulta', obs:'' },

  // Dra. Juliana Rocha — Ginecologia
  { id:26, medicoId:6, nome:'Vanessa Teixeira', email:'van@email.com',     tel:'(11) 93030-3030', data:'2026-05-27', hora:'09:00', tipo:'consulta', obs:'Pré-natal' },
  { id:27, medicoId:6, nome:'Sandra Vieira',    email:'san@email.com',     tel:'(11) 93131-3131', data:'2026-05-27', hora:'10:30', tipo:'retorno',  obs:'Resultado de ultrassom' },
  { id:28, medicoId:6, nome:'Débora Castro',    email:'deb@email.com',     tel:'(11) 93232-3232', data:'2026-05-27', hora:'14:00', tipo:'consulta', obs:'Primeira consulta' },
  { id:29, medicoId:6, nome:'Mariana Luz',      email:'mari@email.com',    tel:'(11) 93333-3333', data:'2026-05-28', hora:'09:30', tipo:'exame',    obs:'Papanicolau' },
];

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
  return nome.replace(/^Dr[a]?\.\s*/i,'').split(' ').filter(Boolean).slice(0,2).map(n => n[0]).join('').toUpperCase();
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
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
  return CORES_AVATAR[medico.cor % CORES_AVATAR.length];
}
