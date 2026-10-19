// funcoes de chamada de api e recebimento de eventos por SSE
const baseUrl = "http://localhost:8000"


// recebe atualizacao do status dos pedidos por SSE
export function recebe_status() {
    const url = baseUrl + "/status"
    const source = new EventSource(url)

    source.onmessage = function(event) {
        onStatusReceived?.(event.data)
    };
    source.onerror = function (err) {
        console.error("Erro na conexão SSE:", err);
    };
}

export async function produtos() {
  const resp = await fetch(`${baseUrl}/produtos`);  
  if (!resp.ok) {
    throw new Error(`Erro de requisição: ${resp.status}`);
  }
  const dados = await resp.json();
  return dados.produtos || [];
}