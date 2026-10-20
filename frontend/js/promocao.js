const botaoInteresse = document.querySelector(".botao-interesse");
const inputEmail = document.getElementById("email");






function lerCategoriasSelecionadas() {
  return [...document.querySelectorAll('input[name="genero"]:checked')]
    .map(c => c.value);
}

async function enviarInteresse(email, categorias) {
  for (const categoria of categorias) {
    const url = `${baseUrl}/registro/${encodeURIComponent(categoria)}/${encodeURIComponent(email)}`;
    const resp = await fetch(url, { method: "POST" });
    if (!resp.ok) throw new Error(`Erro ${resp.status}`);
  }
}

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
    alert("Inscrição realizada! Confira seu e-mail.");
  } catch (erro) {
    console.error("Erro ao enviar:", erro);
    alert("Não foi possível concluir a inscrição. Tente novamente.");
  } finally {
    botaoInteresse.disabled = false;
  }
});