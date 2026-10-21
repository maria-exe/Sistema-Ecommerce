const botaoInteresse = document.querySelector(".botao-interesse");
const botaoCancelamento = document.getElementById("botaoCancelaInteresse");
const inputEmail = document.getElementById("email");

function lerCategoriasSelecionadas() {
  return [...document.querySelectorAll('input[name="genero"]:checked')]
    .map(c => c.value);
}

// envia interesse de promocoes de categorias para o gateaway
async function enviarInteresse(email, categorias) {
  const resp = await fetch(`${baseUrl}/registro`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, categorias }),
  });
  if (!resp.ok) throw new Error(`Erro ${resp.status}`);
}

// cancela interesse
async function cancelaInteresse(email, categorias) {
    const resp = await fetch(`${baseUrl}/registro/cancela`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, categorias }),
  });
  if (!resp.ok) throw new Error(`Erro ${resp.status}`);
}

// botoes que enviam o POST do gateaway
botaoInteresse.addEventListener("click", async () => {
  if (!inputEmail.reportValidity()) return;   

  const categorias = lerCategoriasSelecionadas();
  if (categorias.length === 0) {
    alert("Escolha pelo menos uma categoria.");
    return;
  }

  botaoInteresse.disabled = true;   
  try {
    await enviarInteresse(inputEmail.value.trim(), categorias);
    alert("Inscrição feita!");
  } catch (erro) {
    console.error("Erro ao enviar:", erro);
    alert("Não foi possível concluir a inscrição. Tente novamente.");
  } finally {
    botaoInteresse.disabled = false;
  }
});

botaoCancelamento.addEventListener("click", async () => {
  if (!inputEmail.reportValidity()) return;   

  const categorias = lerCategoriasSelecionadas();
  if (categorias.length === 0) {
    alert("Escolha pelo menos uma categoria.");
    return;
  }

  botaoCancelamento.disabled = true;   
  try {
    await cancelaInteresse(inputEmail.value.trim(), categorias);
    alert("Cancelamento concluido :(");
  } catch (erro) {
    console.error("Erro ao enviar:", erro);
    alert("Não foi possível concluir o cancelamento. Tente novamente.");
  } finally {
    botaoCancelamento.disabled = false;
  }
});