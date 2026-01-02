// Configuração da URL da API via variável de ambiente
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadB3File(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/import/b3`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    // Tentar extrair mensagem de erro do backend
    const error = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(error.detail || "Erro ao importar arquivo");
  }

  return response.json();
}

export async function fetchOperations() {
  const response = await fetch(`${API_URL}/operations`);
  
  if (!response.ok) {
    throw new Error("Erro ao carregar operações");
  }
  
  return response.json();
}
