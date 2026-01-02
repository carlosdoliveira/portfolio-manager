import { useState } from "react";
import { DragAndDropArea } from "./DragAndDropArea";
import { uploadB3File } from "../api/client";
import "../styles/import.css";

type ImportState = "idle" | "ready" | "uploading" | "success" | "error";

type ImportSummary = {
  total_rows: number;
  inserted: number;
  duplicated: number;
  unique_assets: number;
  imported_at: string;
};

export function ImportB3Card() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<ImportState>("idle");
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleImport() {
    if (!file) return;

    setState("uploading");
    setErrorMessage(null);
    
    try {
      const result = await uploadB3File(file);
      setSummary(result.summary);
      setState("success");
    } catch (error) {
      setState("error");
      setErrorMessage(
        error instanceof Error 
          ? error.message 
          : "Erro desconhecido ao importar arquivo"
      );
    }
  }

  return (
    <div className="import-container">
      <div className="import-card">
        <h2>Importar relatório da B3</h2>
        <p className="import-hint">
          Arraste o arquivo ou clique para selecionar.
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
            Processando arquivo…
          </p>
        )}

        {state === "success" && summary && (
          <div className="import-summary">
            <h3>Resumo da importação</h3>
            <ul>
              <li>Total de linhas: {summary.total_rows}</li>
              <li>Novas operações inseridas: {summary.inserted}</li>
              <li>Operações duplicadas ignoradas: {summary.duplicated}</li>
              <li>Ativos únicos no arquivo: {summary.unique_assets}</li>
            </ul>
          </div>
        )}

        {state === "error" && (
          <div className="import-status error">
            <strong>❌ Erro ao importar:</strong>
            <p>{errorMessage}</p>
            <button 
              onClick={() => {
                setState("idle");
                setFile(null);
                setErrorMessage(null);
              }}
            >
              Tentar novamente
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
