import { useState } from "react";
import { DragAndDropArea } from "./DragAndDropArea";
import { uploadB3File } from "../api/client";

export function ImportB3Card() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<"idle" | "ready" | "uploading" | "success" | "error">("idle");

  async function handleImport() {
    if (!file) return;

    setState("uploading");
    try {
      await uploadB3File(file);
      setState("success");
    } catch {
      setState("error");
    }
  }

  return (
    <div className="import-container">
      <div className="import-card">
        <h2>Importar relatório da B3</h2>
        <p className="import-hint">
          Arraste o arquivo ou clique na área abaixo para selecionar.
        </p>

        {state !== "success" && (
          <DragAndDropArea
            onFileSelected={(file) => {
              setFile(file);
              setState("ready");
            }}
          />
        )}

        {state === "ready" && file && (
          <div className="file-preview">
            <span>{file.name}</span>
            <button onClick={handleImport}>
              Importar arquivo
            </button>
          </div>
        )}

        {state === "uploading" && (
          <p className="import-status">
            Processando arquivo, aguarde…
          </p>
        )}

        {state === "success" && (
          <p className="import-status success">
            Importação concluída com sucesso 🎉
          </p>
        )}

        {state === "error" && (
          <p className="import-status error">
            Erro ao importar o arquivo. Verifique o formato.
          </p>
        )}
      </div>
    </div>
  );
}
