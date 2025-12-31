import { useState } from "react";
import { DragAndDropArea } from "./DragAndDropArea";
import { uploadB3File } from "../api/client";
import "../styles/import.css";

type ImportState = "idle" | "ready" | "uploading" | "success" | "error";

type ImportSummary = {
  total_operations: number;
  total_volume: number;
  total_compras: number;
  total_vendas: number;
  unique_assets: number;
  imported_at: string;
};

export function ImportB3Card() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<ImportState>("idle");
  const [summary, setSummary] = useState<ImportSummary | null>(null);

  async function handleImport() {
    if (!file) return;

    setState("uploading");
    try {
      const result = await uploadB3File(file);
      setSummary(result.summary);
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

        {state === "success" && summary && (
          <div className="import-summary">
            <h3>Resumo da importação</h3>
            <ul>
              <li>Total de operações: {summary.total_operations}</li>
              <li>
                Volume financeiro: R$ {summary.total_volume.toFixed(2)}
              </li>
              <li>
                Total comprado: R$ {summary.total_compras.toFixed(2)}
              </li>
              <li>
                Total vendido: R$ {summary.total_vendas.toFixed(2)}
              </li>
              <li>Ativos únicos: {summary.unique_assets}</li>
            </ul>
          </div>
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
