const API_URL = "https://medschedule-wfpd.onrender.com";

async function request(method, path, body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_URL}${path}`, options);

  if (!res.ok) {
    const erro = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(erro.detail || "Erro na requisição");
  }

  if (res.status === 204) return null;
  return res.json();
}

const MedicosAPI = {
  listar:    ()          => request("GET",    "/medicos/"),
  buscar:    (id)        => request("GET",    `/medicos/${id}`),
  criar:     (dados)     => request("POST",   "/medicos/", dados),
  atualizar: (id, dados) => request("PUT",    `/medicos/${id}`, dados),
  deletar:   (id)        => request("DELETE", `/medicos/${id}`),
};

const ConsultasAPI = {
  listar: ({ medicoId, data, tipo } = {}) => {
    const params = new URLSearchParams();
    if (medicoId) params.append("medico_id", medicoId);
    if (data)     params.append("data", data);
    if (tipo)     params.append("tipo", tipo);
    return request("GET", `/consultas/?${params}`);
  },
  criar:     (dados)     => request("POST",   "/consultas/", dados),
  atualizar: (id, dados) => request("PUT",    `/consultas/${id}`, dados),
  deletar:   (id)        => request("DELETE", `/consultas/${id}`),
};