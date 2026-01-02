import { useState, useEffect } from "react";
import {
  fetchOperations,
  createOperation,
  updateOperation,
  deleteOperation,
  type Operation,
  type OperationCreate,
} from "../api/client";
import { OperationForm } from "../components/OperationForm";
import "./Portfolio.css";

type ViewMode = "list" | "create" | "edit";

export default function Portfolio() {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  useEffect(() => {
    loadOperations();
  }, []);

  const loadOperations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchOperations();
      setOperations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar operações");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (operation: OperationCreate) => {
    try {
      await createOperation(operation);
      setSuccessMessage("Operação criada com sucesso!");
      setViewMode("list");
      await loadOperations();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar operação");
    }
  };

  const handleUpdate = async (operation: OperationCreate) => {
    if (!selectedOperation) return;
    
    try {
      await updateOperation(selectedOperation.id, operation);
      setSuccessMessage("Operação atualizada com sucesso!");
      setViewMode("list");
      setSelectedOperation(null);
      await loadOperations();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao atualizar operação");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteOperation(id);
      setSuccessMessage("Operação deletada com sucesso!");
      setDeleteConfirm(null);
      await loadOperations();
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao deletar operação");
    }
  };

  const handleEdit = (operation: Operation) => {
    setSelectedOperation(operation);
    setViewMode("edit");
  };

  const handleCancel = () => {
    setViewMode("list");
    setSelectedOperation(null);
    setError(null);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR");
  };

  if (isLoading) {
    return (
      <div className="portfolio-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Carregando operações...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-container">
      <div className="portfolio-header">
        <div>
          <h1>Carteira de Investimentos</h1>
          <p className="portfolio-subtitle">
            Gerencie suas operações de compra e venda
          </p>
        </div>
        {viewMode === "list" && (
          <button
            className="btn-primary"
            onClick={() => setViewMode("create")}
          >
            + Nova Operação
          </button>
        )}
      </div>

      {successMessage && (
        <div className="alert alert-success">
          <span>✓</span> {successMessage}
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <span>✗</span> {error}
          <button onClick={() => setError(null)} className="alert-close">
            ×
          </button>
        </div>
      )}

      {viewMode === "create" && (
        <div className="form-section">
          <h2>Nova Operação</h2>
          <OperationForm
            onSubmit={handleCreate}
            onCancel={handleCancel}
            submitLabel="Criar Operação"
          />
        </div>
      )}

      {viewMode === "edit" && selectedOperation && (
        <div className="form-section">
          <h2>Editar Operação</h2>
          <div className="edit-notice">
            <strong>Atenção:</strong> Editar uma operação criará uma nova entrada
            e marcará a antiga como cancelada, preservando o histórico.
          </div>
          <OperationForm
            initialData={{
              asset_class: selectedOperation.asset_class,
              asset_type: selectedOperation.asset_type,
              product_name: selectedOperation.product_name,
              ticker: selectedOperation.ticker,
              movement_type: selectedOperation.movement_type,
              quantity: selectedOperation.quantity,
              price: selectedOperation.price,
              trade_date: selectedOperation.trade_date,
              market: selectedOperation.market,
              institution: selectedOperation.institution,
            }}
            onSubmit={handleUpdate}
            onCancel={handleCancel}
            submitLabel="Atualizar Operação"
          />
        </div>
      )}

      {viewMode === "list" && (
        <>
          <div className="portfolio-stats">
            <div className="stat-card">
              <span className="stat-label">Total de Operações</span>
              <span className="stat-value">{operations.length}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Total Investido</span>
              <span className="stat-value">
                {formatCurrency(
                  operations
                    .filter((op) => op.movement_type === "COMPRA")
                    .reduce((sum, op) => sum + op.value, 0)
                )}
              </span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Ativos Únicos</span>
              <span className="stat-value">
                {new Set(operations.map((op) => op.ticker)).size}
              </span>
            </div>
          </div>

          {operations.length === 0 ? (
            <div className="empty-state">
              <p>Nenhuma operação registrada ainda.</p>
              <button
                className="btn-primary"
                onClick={() => setViewMode("create")}
              >
                Criar primeira operação
              </button>
            </div>
          ) : (
            <div className="operations-table-container">
              <table className="operations-table">
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Tipo</th>
                    <th>Ticker</th>
                    <th>Produto</th>
                    <th>Quantidade</th>
                    <th>Preço</th>
                    <th>Valor Total</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {operations.map((operation) => (
                    <tr key={operation.id}>
                      <td>{formatDate(operation.trade_date)}</td>
                      <td>
                        <span
                          className={`badge ${
                            operation.movement_type === "COMPRA"
                              ? "badge-buy"
                              : "badge-sell"
                          }`}
                        >
                          {operation.movement_type}
                        </span>
                      </td>
                      <td className="ticker-cell">{operation.ticker || "-"}</td>
                      <td>{operation.product_name}</td>
                      <td className="number-cell">{operation.quantity}</td>
                      <td className="number-cell">
                        {formatCurrency(operation.price)}
                      </td>
                      <td className="number-cell">
                        {formatCurrency(operation.value)}
                      </td>
                      <td className="actions-cell">
                        <button
                          className="btn-icon"
                          onClick={() => handleEdit(operation)}
                          title="Editar"
                        >
                          ✏️
                        </button>
                        <button
                          className="btn-icon btn-delete"
                          onClick={() => setDeleteConfirm(operation.id)}
                          title="Deletar"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {deleteConfirm !== null && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Confirmar Exclusão</h3>
            <p>
              Tem certeza que deseja deletar esta operação? Esta ação não pode
              ser desfeita.
            </p>
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => setDeleteConfirm(null)}
              >
                Cancelar
              </button>
              <button
                className="btn-danger"
                onClick={() => handleDelete(deleteConfirm)}
              >
                Deletar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

