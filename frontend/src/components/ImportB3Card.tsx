import { useState } from "react";
import { DragAndDropArea } from "./DragAndDropArea";
import { uploadB3File, applyCorporateEvents } from "../api/client";
import "../styles/import.css";

type ImportState = "idle" | "ready" | "uploading" | "success" | "error" | "events-review";

type CorporateEvent = {
  type: string;
  ticker: string;
  quantity: number;
  date: string;
  description: string;
  skip?: boolean;
};

type ImportSummary = {
  total_rows: number;
  inserted: number;
  duplicated: number;
  unique_assets: number;
  imported_at: string;
  corporate_events?: CorporateEvent[];
  events_detected?: number;
};

export function ImportB3Card() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<ImportState>("idle");
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedEvents, setSelectedEvents] = useState<number[]>([]);
  const [applyingEvents, setApplyingEvents] = useState(false);

  async function handleImport() {
    if (!file) return;

    setState("uploading");
    setErrorMessage(null);
    
    try {
      const result = await uploadB3File(file);
      setSummary(result.summary);
      
      // Se detectou eventos, mostrar tela de revisão
      if (result.summary.events_detected && result.summary.events_detected > 0) {
        setState("events-review");
        // Selecionar todos por padrão (exceto os com skip)
        const autoSelect = result.summary.corporate_events
          ?.map((e: CorporateEvent, i: number) => e.skip ? -1 : i)
          .filter((i: number) => i >= 0) || [];
        setSelectedEvents(autoSelect);
      } else {
        setState("success");
      }
    } catch (error) {
      setState("error");
      setErrorMessage(
        error instanceof Error 
          ? error.message 
          : "Erro desconhecido ao importar arquivo"
      );
    }
  }

  async function handleApplyEvents() {
    if (!summary?.corporate_events) return;

    setApplyingEvents(true);
    setErrorMessage(null);

    try {
      const eventsToApply = summary.corporate_events.filter((_, i) => 
        selectedEvents.includes(i)
      );

      await applyCorporateEvents(eventsToApply);
      setState("success");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Erro ao aplicar eventos corporativos"
      );
    } finally {
      setApplyingEvents(false);
    }
  }

  function toggleEvent(index: number) {
    setSelectedEvents(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  }

  function getEventIcon(type: string): string {
    switch (type) {
      case "BONIFICACAO": return "🎁";
      case "DESDOBRO": return "🔀";
      case "SUBSCRICAO": return "📜";
      case "CORRECAO": return "⚙️";
      default: return "📊";
    }
  }

  function getEventLabel(type: string): string {
    switch (type) {
      case "BONIFICACAO": return "Bonificação";
      case "DESDOBRO": return "Desdobro";
      case "SUBSCRICAO": return "Subscrição";
      case "CORRECAO": return "Atualização";
      default: return type;
    }
  }

  return (
    <div className="import-container">
      <div className="import-card">
        <h2>Importar relatório da B3</h2>
        <p className="import-hint">
          Arraste o arquivo ou clique para selecionar.
        </p>

        {state !== "success" && state !== "events-review" && (
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

        {state === "events-review" && summary && (
          <div className="events-review">
            <h3>⚠️ Eventos Corporativos Detectados</h3>
            <p className="events-hint">
              {summary.events_detected} evento(s) corporativo(s) foram detectados no arquivo.
              Selecione quais você deseja aplicar:
            </p>

            <div className="events-list">
              {summary.corporate_events?.map((event, index) => (
                <div key={index} className={`event-item ${event.skip ? 'skip' : ''}`}>
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes(index)}
                    onChange={() => toggleEvent(index)}
                    disabled={event.skip}
                  />
                  <div className="event-details">
                    <div className="event-header">
                      <span className="event-icon">{getEventIcon(event.type)}</span>
                      <strong>{event.ticker}</strong>
                      <span className="event-type-badge">{getEventLabel(event.type)}</span>
                    </div>
                    <p className="event-description">{event.description}</p>
                    <div className="event-meta">
                      <span>Quantidade: {event.quantity > 0 ? '+' : ''}{event.quantity}</span>
                      <span>Data: {event.date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="events-actions">
              <button
                onClick={handleApplyEvents}
                disabled={applyingEvents || selectedEvents.length === 0}
                className="btn-primary"
              >
                {applyingEvents
                  ? "Aplicando..."
                  : `Aplicar ${selectedEvents.length} evento(s)`}
              </button>
              <button
                onClick={() => setState("success")}
                className="btn-secondary"
              >
                Pular por enquanto
              </button>
            </div>

            {errorMessage && (
              <div className="error-message">
                ❌ {errorMessage}
              </div>
            )}
          </div>
        )}

        {state === "success" && summary && (
          <div className="import-summary">
            <h3>✅ Resumo da importação</h3>
            <ul>
              <li>Total de linhas: {summary.total_rows}</li>
              <li>Novas operações inseridas: {summary.inserted}</li>
              <li>Operações duplicadas ignoradas: {summary.duplicated}</li>
              <li>Ativos únicos no arquivo: {summary.unique_assets}</li>
              {summary.events_detected && summary.events_detected > 0 && (
                <li>Eventos corporativos aplicados: {selectedEvents.length}/{summary.events_detected}</li>
              )}
            </ul>
            <button
              onClick={() => {
                setState("idle");
                setFile(null);
                setSummary(null);
                setSelectedEvents([]);
              }}
              className="btn-secondary"
            >
              Importar outro arquivo
            </button>
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
