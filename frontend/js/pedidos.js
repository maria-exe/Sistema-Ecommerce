const ETAPAS = [
  { rotulo: "Pedido criado",       aguardando: "Pedido criado" },
  { rotulo: "Estoque confirmado",  aguardando: "Aguardando o estoque" },
  { rotulo: "Pagamento aprovado",  aguardando: "Aguardando o pagamento" },
  { rotulo: "Pedido enviado",      aguardando: "Aguardando o envio" },
];

const FINAIS_RUINS = {
  estoque_indisponivel: "Estoque indisponível",
  pagamento_recusado: "Pagamento recusado",
  cancelado: "Pedido cancelado",
};

const CHAVE_STORAGE = "pagina-sete:pedidos";

const painelPedidos = document.getElementById("painel-pedidos");
const overlayPedidos = document.getElementById("overlay-pedidos");
const listaPedidos = document.getElementById("lista-pedidos");
const btnAbrirPedidos = document.getElementById("abrir-pedidos");
const btnFecharPedidos = document.getElementById("fechar-pedidos");
const novidadeEl = document.getElementById("pedidos-novidade");
const avisosEl = document.getElementById("avisos");

const pedidos = new Map();
const streams = new Map(); 

// recebe o sse do gateaway
function abrirStream(idPedido) {
  if (streams.has(idPedido)) return;

  const fonte = new EventSource(`${baseUrl}/sse/${encodeURIComponent(idPedido)}`);
  fonte.onmessage = (e) => aplicarStatus(idPedido, e.data.replace(/^data:\s*/, ""));
  fonte.onerror = () => console.warn(`SSE do pedido ${idPedido} desconectado`);
  streams.set(idPedido, fonte);
}

// funcoes de frontend
function fecharStream(idPedido) {
  const fonte = streams.get(idPedido);
  if (fonte) {
    fonte.close();
    streams.delete(idPedido);
  }
} 

function salvarPedidos() {
  try {
    localStorage.setItem(CHAVE_STORAGE, JSON.stringify([...pedidos.values()]));
  } catch (erro) {
    console.warn("Não foi possível salvar os pedidos:", erro);
  }
}

function carregarPedidos() {
  try {
    const lista = JSON.parse(localStorage.getItem(CHAVE_STORAGE) || "[]");
    lista.forEach(p => pedidos.set(p.id, p));
  } catch (erro) {
    console.warn("Não foi possível ler os pedidos salvos:", erro);
  }
}

function interpretarStatus(bruto) {
  let dados;
  try {
    dados = JSON.parse(bruto);
  } catch {
    dados = { status: bruto };
  }
  if (typeof dados !== "object" || dados === null) dados = { status: String(dados) };

  const chave = String(dados.evento || dados.status || "").toLowerCase();
  const r = { url: dados.url_pagamento || null, nota: dados.nota_fiscal || null };

  if (chave.includes("estoque.indisponivel") || chave.includes("estoque indisponivel")) {
    r.final = "estoque_indisponivel";
  } else if (chave.includes("pagamento.recusado") || chave.includes("falha no pagamento") || chave.includes("recusado")) {
    r.final = "pagamento_recusado";
  } else if (chave.includes("enviado")) {
    r.etapa = 3;
  } else if (chave.includes("pagamento.aprovado") || chave.includes("pagamento aprovado")) {
    r.etapa = 2;
  } else if (chave.includes("estoque_ok") || chave.includes("em estoque") || chave.includes("estoque confirmado")) {
    r.etapa = 1;
  } else if (chave.includes("excluido") || chave.includes("cancelado")) {
    r.final = "cancelado";
  }
  return r;
}

function aplicarStatus(idPedido, bruto) {
  const p = pedidos.get(idPedido);
  if (!p || p.final) return;

  const r = interpretarStatus(bruto);
  let mudou = false;

  if (r.url && r.url !== p.urlPagamento) {
    p.urlPagamento = r.url;
    mudou = true;
  }
  if (r.nota) p.nota = r.nota;
  if (r.etapa != null && r.etapa > p.etapa) {
    p.etapa = r.etapa;
    mudou = true;
  }
  if (r.final) {
    p.final = r.final;
    mudou = true;
  }
  if (!mudou) return;

  if (p.final || p.etapa === 3) fecharStream(idPedido);

  salvarPedidos();
  renderizarPedidos();

  const texto = p.final
    ? FINAIS_RUINS[p.final]
    : (r.etapa != null ? ETAPAS[p.etapa].rotulo : "Pagamento disponível");

  if (!painelPedidos.classList.contains("aberto")) novidadeEl.hidden = false;
}

function acompanharPedido(idPedido, itens, urlPagamento = null) {
  pedidos.set(idPedido, { id: idPedido, itens, etapa: 0, final: null, urlPagamento, nota: null });
  salvarPedidos();
  renderizarPedidos();
  abrirStream(idPedido);
}

async function cancelarPedido(p, botao) {
  if (!confirm(`Cancelar o pedido ${p.id}?`)) return;

  botao.disabled = true;
  try {
    const resp = await fetch(`${baseUrl}/pedido/cancela/${encodeURIComponent(p.id)}`, { method: "DELETE" });
    if (!resp.ok) throw new Error(`Erro ${resp.status}`);

    p.final = "cancelado";
    fecharStream(p.id);
    salvarPedidos();
    renderizarPedidos();
 
  } catch (erro) {
    console.error("Falha ao cancelar:", erro);
    botao.disabled = false;
  }
}

function criarCartaoPedido(p) {
  const card = document.createElement("article");
  card.className = "pedido-card";

  const topo = document.createElement("div");
  topo.className = "pedido-topo";
  const titulo = document.createElement("strong");
  titulo.textContent = `Pedido ${p.id}`;
  topo.appendChild(titulo);
  if (p.nota) {
    const nota = document.createElement("span");
    nota.textContent = `NF ${p.nota}`;
    topo.appendChild(nota);
  }

  const itens = document.createElement("ul");
  itens.className = "pedido-itens";
  p.itens.forEach(i => {
    const li = document.createElement("li");
    li.textContent = `${i.quantidade}× ${i.titulo}`;
    itens.appendChild(li);
  });

  const linha = document.createElement("ol");
  linha.className = "linha-tempo";
  ETAPAS.forEach((etapa, i) => {
    const li = document.createElement("li");
    if (i <= p.etapa) {
      li.className = "feito";
      li.textContent = etapa.rotulo;
    } else if (!p.final && i === p.etapa + 1) {
      li.className = "atual";
      li.textContent = etapa.aguardando;
    } else {
      li.textContent = etapa.rotulo;
    }
    linha.appendChild(li);
  });

  card.append(topo, itens, linha);

  if (p.final) {
    const aviso = document.createElement("p");
    aviso.className = `pedido-final ${p.final}`;
    aviso.textContent = FINAIS_RUINS[p.final];
    card.appendChild(aviso);
  }

  const acoes = document.createElement("div");
  acoes.className = "pedido-acoes";

  if (p.urlPagamento && !p.final && p.etapa === 1) {
    const pagar = document.createElement("button");
    pagar.type = "button";
    pagar.className = "btn-comprar";
    pagar.textContent = "Ir para o pagamento";
    pagar.addEventListener("click", () => window.open(p.urlPagamento, "_blank", "noopener"));
    acoes.appendChild(pagar);
  }

  if (!p.final && p.etapa < 2) {
    const cancelar = document.createElement("button");
    cancelar.type = "button";
    cancelar.className = "pedido-cancelar";
    cancelar.textContent = "Cancelar";
    cancelar.addEventListener("click", () => cancelarPedido(p, cancelar));
    acoes.appendChild(cancelar);
  }

  if (acoes.children.length > 0) card.appendChild(acoes);
  return card;
}

function renderizarPedidos() {
  listaPedidos.innerHTML = "";

  if (pedidos.size === 0) {
    const vazio = document.createElement("p");
    vazio.className = "pedidos-vazio";
    vazio.textContent = "Você ainda não fez pedidos.";
    listaPedidos.appendChild(vazio);
    return;
  }

  [...pedidos.values()].reverse().forEach(p => listaPedidos.appendChild(criarCartaoPedido(p)));
}

function abrirPedidos() {
  renderizarPedidos();
  painelPedidos.classList.add("aberto");
  overlayPedidos.classList.add("visivel");
  painelPedidos.setAttribute("aria-hidden", "false");
  novidadeEl.hidden = true;
  btnFecharPedidos.focus();
}

function fecharPedidos() {
  painelPedidos.classList.remove("aberto");
  overlayPedidos.classList.remove("visivel");
  painelPedidos.setAttribute("aria-hidden", "true");
  btnAbrirPedidos.focus();
}

btnAbrirPedidos.addEventListener("click", abrirPedidos);
btnFecharPedidos.addEventListener("click", fecharPedidos);
overlayPedidos.addEventListener("click", fecharPedidos);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && painelPedidos.classList.contains("aberto")) fecharPedidos();
});

carregarPedidos();
renderizarPedidos();
pedidos.forEach(p => {
  if (!p.final && p.etapa < 3) abrirStream(p.id);  
});