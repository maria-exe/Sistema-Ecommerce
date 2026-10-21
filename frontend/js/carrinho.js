let carrinho = [];  

const painel = document.getElementById("carrinho-lateral");
const overlay = document.getElementById("overlay");
const listaItens = document.getElementById("carrinho-itens");
const totalEl = document.getElementById("carrinho-total");
const contadorEl = document.getElementById("contador-carrinho");
const statusEl = document.getElementById("carrinho-status");
const btnAbrir = document.getElementById("abrir-carrinho");
const btnFechar = document.getElementById("fechar-carrinho");
const btnFinalizar = document.getElementById("finalizar-pedido");

// funcao da api para criar pedido
async function criarPedido(pedido) {
  const resp = await fetch(`${baseUrl}/pedido`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(pedido),
  });
  if (!resp.ok) throw new Error(`Erro ${resp.status}`);
  return resp.json();
}

// funcoes de front
function adicionarAoCarrinho(produto, quantidade) {
  const item = carrinho.find(i => i.produto.id === produto.id);

  if (item) {
    item.quantidade = Math.min(item.quantidade + quantidade, produto.quantidade);
  } else {
    carrinho.push({ produto, quantidade });
  }

  atualizarCarrinho();
}

function removerDoCarrinho(id) {
  carrinho = carrinho.filter(i => i.produto.id !== id);
  atualizarCarrinho();
}

function alterarQuantidade(id, delta) {
  const item = carrinho.find(i => i.produto.id === id);
  if (!item) return;

  const nova = item.quantidade + delta;
  if (nova < 1 || nova > item.produto.quantidade) return;  

  item.quantidade = nova;
  atualizarCarrinho();
}

function calcularTotal() {
  return carrinho.reduce((soma, i) => soma + i.produto.preco * i.quantidade, 0);
}

function atualizarContadorCarrinho() {
  const total = carrinho.reduce((soma, i) => soma + i.quantidade, 0);
  contadorEl.textContent = total;
  contadorEl.hidden = total === 0;
}

function criarLinhaCarrinho(item) {
  const { produto, quantidade } = item;

  const linha = document.createElement("div");
  linha.className = "carrinho-item";

  const nome = document.createElement("span");
  nome.className = "carrinho-item-nome";
  nome.textContent = produto.titulo;

  const subtotal = document.createElement("span");
  subtotal.className = "carrinho-item-subtotal";
  subtotal.textContent = formatarPreco(produto.preco * quantidade);

  const menos = document.createElement("button");
  menos.type = "button";
  menos.className = "carrinho-qtd-btn";
  menos.textContent = "−";
  menos.disabled = quantidade <= 1;
  menos.setAttribute("aria-label", `Diminuir quantidade de ${produto.titulo}`);
  menos.addEventListener("click", () => alterarQuantidade(produto.id, -1));

  const qtd = document.createElement("span");
  qtd.className = "carrinho-item-qtd";
  qtd.textContent = quantidade;

  const mais = document.createElement("button");
  mais.type = "button";
  mais.className = "carrinho-qtd-btn";
  mais.textContent = "+";
  mais.disabled = quantidade >= produto.quantidade;
  mais.setAttribute("aria-label", `Aumentar quantidade de ${produto.titulo}`);
  mais.addEventListener("click", () => alterarQuantidade(produto.id, 1));

  const remover = document.createElement("button");
  remover.type = "button";
  remover.className = "carrinho-remover";
  remover.textContent = "Remover";
  remover.addEventListener("click", () => removerDoCarrinho(produto.id));

  const controles = document.createElement("div");
  controles.className = "carrinho-item-controles";
  controles.append(menos, qtd, mais, remover);

  linha.append(nome, subtotal, controles);
  return linha;
}

function renderizarCarrinho() {
  listaItens.innerHTML = "";

  if (carrinho.length === 0) {
    listaItens.textContent = "Seu carrinho está vazio.";
  } else {
    carrinho.forEach(item => listaItens.appendChild(criarLinhaCarrinho(item)));
  }

  totalEl.textContent = formatarPreco(calcularTotal());
  btnFinalizar.disabled = carrinho.length === 0;
}

function atualizarCarrinho() {
  atualizarContadorCarrinho();
  renderizarCarrinho();
}

function abrirCarrinho() {
  renderizarCarrinho();
  painel.classList.add("aberto");
  overlay.classList.add("visivel");
  painel.setAttribute("aria-hidden", "false");
  btnFechar.focus();
}

function fecharCarrinho() {
  painel.classList.remove("aberto");
  overlay.classList.remove("visivel");
  painel.setAttribute("aria-hidden", "true");
  btnAbrir.focus();
}

function mostrarStatus(texto, erro = false) {
  statusEl.innerHTML = "";
  statusEl.hidden = false;
  statusEl.classList.toggle("erro", erro);

  const p = document.createElement("p");
  p.textContent = texto;
  statusEl.appendChild(p);
}

async function finalizarPedido() {
  if (carrinho.length === 0) return;

  btnFinalizar.disabled = true;   
  mostrarStatus("Enviando pedido...");

  const itens = carrinho.map(i => ({ titulo: i.produto.titulo, quantidade: i.quantidade }));

  const pedido = {
    produtos: carrinho.map(i => ({
      id_livro: i.produto.id,
      quantidade: i.quantidade,
    })),
  };

  try {
    const resposta = await criarPedido(pedido);

    carrinho = [];
    atualizarCarrinho();
    statusEl.hidden = true;
    fecharCarrinho();

    acompanharPedido(resposta.id_pedido, itens, resposta.url_pagamento || null);
    abrirPedidos();
  } catch (erro) {
    console.error("Falha ao criar pedido:", erro);
    mostrarStatus("Não foi possível finalizar o pedido. Tente novamente.", true);
    btnFinalizar.disabled = false;
  }
}

btnAbrir.addEventListener("click", abrirCarrinho);
btnFechar.addEventListener("click", fecharCarrinho);
overlay.addEventListener("click", fecharCarrinho);
btnFinalizar.addEventListener("click", finalizarPedido);

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && painel.classList.contains("aberto")) fecharCarrinho();
});

atualizarCarrinho();