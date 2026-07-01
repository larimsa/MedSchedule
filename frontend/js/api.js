/* ─────────────────────────────────────────────
   api.js — Cliente HTTP + tradução de campos
   (front usa nomes curtos; backend usa nomes completos)
   ───────────────────────────────────────────── */

const API_URL =
  location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.protocol === "file:"
    ? "http://localhost:8000"
    : "https://medschedule-wfpd.onrender.com";


async function request(method, path, body = null) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_URL}${path}`, options);

  if (!res.ok) {
    const erro = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(erro.detail || "Erro na requisição");
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── MAPPERS ─────────────────────────────────

function medicoFromApi(m) {
  return {
    id: m.id,
    nome: m.nome,
    crm: m.crm,
    esp: m.especialidade,
    email: m.email,
    tel: m.telefone || "",
    end: m.endereco || "",
    hor: m.horario || "",
    cor: m.cor || 0,
  };
}

function medicoToApi(m) {
  return {
    nome: m.nome,
    crm: m.crm,
    especialidade: m.esp,
    email: m.email,
    telefone: m.tel || "",
    endereco: m.end || "",
    horario: m.hor || "",
    cor: m.cor ?? 0,
  };
}

function consultaFromApi(c) {
  return {
    id: c.id,
    medicoId: c.medico_id,
    nome: c.nome,
    email: c.email || "",
    tel: c.telefone || "",
    data: c.data,
    hora: c.hora,
    tipo: c.tipo,
    obs: c.observacoes || "",
  };
}

function consultaToApi(c) {
  return {
    medico_id: c.medicoId,
    nome: c.nome,
    email: c.email || "",
    telefone: c.tel || "",
    data: c.data,
    hora: c.hora,
    tipo: c.tipo,
    observacoes: c.obs || "",
  };
}

// ── ENDPOINTS ───────────────────────────────

const MedicosAPI = {
  listar:    async ()          => (await request("GET", "/medicos/")).map(medicoFromApi),
  buscar:    async (id)        => medicoFromApi(await request("GET", `/medicos/${id}`)),
  criar:     async (dados)     => medicoFromApi(await request("POST", "/medicos/", medicoToApi(dados))),
  atualizar: async (id, dados) => medicoFromApi(await request("PUT", `/medicos/${id}`, medicoToApi(dados))),
  deletar:   (id)              => request("DELETE", `/medicos/${id}`),
};

const ConsultasAPI = {
  listar: async ({ medicoId, data, tipo } = {}) => {
    const params = new URLSearchParams();
    if (medicoId) params.append("medico_id", medicoId);
    if (data)     params.append("data", data);
    if (tipo)     params.append("tipo", tipo);
    const qs = params.toString();
    const arr = await request("GET", `/consultas/${qs ? "?" + qs : ""}`);
    return arr.map(consultaFromApi);
  },
  criar:     async (dados)     => consultaFromApi(await request("POST", "/consultas/", consultaToApi(dados))),
  atualizar: async (id, dados) => consultaFromApi(await request("PUT", `/consultas/${id}`, consultaToApi(dados))),
  deletar:   (id)              => request("DELETE", `/consultas/${id}`),
};
