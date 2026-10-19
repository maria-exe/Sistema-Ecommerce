const baseUrl = "http://localhost:8000"; 
let carrinho = []; 

async function getProdutos() {
  const resp = await fetch(`${baseUrl}/produtos`);  
  if (!resp.ok) {
    throw new Error(`Erro de requisição: ${resp.status}`);
  }
  const dados = await resp.json();
  return dados.produtos || [];
}

function formatarPreco(valor) {
  return `R$ ${Number(valor).toFixed(2).replace(".", ",")}`;
}

function criarCard(produto) {
  const card = document.createElement("div");
  card.className = "card";

  const img = document.createElement("img");
  img.className = "card-img";
  img.src = produto.capa || "assets/placeholder.svg";
  img.alt = `Capa de ${produto.titulo}`;

  const titulo = document.createElement("span");
  titulo.className = "card-nome";
  titulo.textContent = produto.titulo;

  const autor = document.createElement("span");
  autor.className = "card-autor";
  autor.textContent = produto.autor;

  const preco = document.createElement("span");
  preco.className = "card-preco";
  preco.textContent = formatarPreco(produto.preco);

  const info = document.createElement("div");
  info.className = "card-info";
  info.append(titulo, autor, preco);

  const qtd = document.createElement("input");
  qtd.type = "number";
  qtd.className = "card-qtd";
  qtd.min = 1;
  qtd.max = produto.quantidade;
  qtd.value = 1;
  qtd.disabled = produto.quantidade === 0;

  const botao = document.createElement("button");
  botao.className = "btn-comprar";
  botao.textContent = "Adicionar ao carrinho";
  botao.disabled = produto.quantidade === 0;
  botao.addEventListener("click", () => {
    adicionarAoCarrinho(produto, lerQuantidade(qtd, produto.quantidade));
  });

  const acoes = document.createElement("div");
  acoes.className = "card-acoes";

  card.append(img, info, acoes);
  acoes.append(qtd, botao);
  return card;
}

function renderizarProdutos(produtos) {
  const container = document.querySelector(".container-catalogo");
  container.innerHTML = "";

  if (produtos.length === 0) {
    container.textContent = "Nenhum produto disponível em estoque.";
    return;
  }

  produtos.forEach(produto => container.appendChild(criarCard(produto)));
}

function lerQuantidade(input, estoque) {
  const valor = parseInt(input.value, 10);
  if (isNaN(valor) || valor < 1) return 1;
  return Math.min(valor, estoque);
}

function adicionarAoCarrinho(produto, quantidade) {
  const item = carrinho.find(i => i.produto.id === produto.id);

  if (item) {
    item.quantidade = Math.min(item.quantidade + quantidade, produto.quantidade);
  } else {
    carrinho.push({ produto, quantidade });
  }
  console.log(carrinho);
}

async function carregarCatalogo() {
  try {
    const produtos = await getProdutos();
    renderizarProdutos(produtos);
  } catch (erro) {
    console.error("Falha ao buscar os dados:", erro);
    document.querySelector(".container-catalogo").textContent =
      "Não foi possível carregar os produtos.";
  }
}

carregarCatalogo();


