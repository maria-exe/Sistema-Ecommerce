
// ligacao com as apis
API_URL = "http://localhost:8000"
// pedidos

async function requisicao(caminho, opcoes = {}) {
  const resp = await fetch(`${API_URL}${caminho}`, {
    headers: { "Content-Type": "application/json" },
    ...opcoes,
  });

  if (!resp.ok) {
    throw new Error(`Erro ${resp.status} em ${caminho}`);
  }
  const texto = await resp.text();
  return texto ? JSON.parse(texto) : null;
}

function produtos() {
    return requisicao("/produtos")
}

// 