import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

export async function uploadB3File(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/import/b3", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Erro ao importar arquivo");
  }

  return response.json();
}
