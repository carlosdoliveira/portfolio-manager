import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  fetchAssetById,
  fetchAssetOperations,
  createOperation,
  updateOperation,
  deleteOperation,
  Asset,
  Operation,
  OperationCreate,
} from "../api/client";
import "./AssetDetail.css";

export default function AssetDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const assetId = Number(id);

  const [asset, setAsset] = useState<Asset | null>(null);
  const [operations, setOperations] = useState<Operation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Estados para modal
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [editingOperation, setEditingOperation] = useState<Operation | null>(null);

  // Estados para confirmação de delete
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [operationToDelete, setOperationToDelete] = useState<Operation | null>(null);

  // Estados do formulário
  const [formData, setFormData] = useState<OperationCreate>({
    asset_id: assetId,
    movement_type: "COMPRA",
    quantity: 0,
    price: 0,
    trade_date: new Date().toISOString().split("T")[0],
    market: "VISTA",
    institution: "",
  });

  useEffect(() => {
    loadAssetData();
  }, [assetId]);

  async function loadAssetData() {
    try {
      setLoading(true);
      setError(null);
      const [assetData, operationsData] = await Promise.all([
        fetchAssetById(assetId),
        fetchAssetOperations(assetId),
      ]);
      setAsset(assetData);
      setOperations(operationsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar dados do ativo");
    } finally {
      setLoading(false);
    }
  }

  function handleOpenCreateModal() {
    setModalMode("create");
    setEditingOperation(null);
    setFormData({
      asset_id: assetId,
      movement_type: "COMPRA",
      quantity: 0,
      price: 0,
      trade_date: new Date().toISOString().split("T")[0],
      market: "VISTA",
      institution: "",
    });
    setShowModal(true);
  }

  function handleOpenEditModal(operation: Operation) {
    setModalMode("edit");
    setEditingOperation(operation);
    setFormData({
      asset_id: assetId,
      movement_type: operation.movement_type,
      quantity: operation.quantity,
      price: operation.price,
      trade_date: operation.trade_date,
      market: operation.market || "",
      institution: operation.institution || "",
    });
    setShowModal(true);
  }

  function handleCloseModal() {
    setShowModal(false);
    setEditingOperation(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      setLoading(true);

      if (modalMode === "create") {
        await createOperation(formData);
        setSuccessMessage("Operação criada com sucesso!");
      } else if (editingOperation) {
        await updateOperation(editingOperation.id, formData);
        setSuccessMessage("Operação atualizada com sucesso!");
      }

      handleCloseModal();
      await loadAssetData();

      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar operação");
    } finally {
      setLoading(false);
    }
  }

  function handleOpenDeleteConfirm(operation: Operation) {
    setOperationToDelete(operation);
    setShowDeleteConfirm(true);
  }

  function handleCloseDeleteConfirm() {
    setShowDeleteConfirm(false);
    setOperationToDelete(null);
  }

  async function handleConfirmDelete() {
    if (!operationToDelete) return;

    try {
      setLoading(true);
      await deleteOperation(operationToDelete.id);
      setSuccessMessage("Operação deletada com sucesso!");
      handleCloseDeleteConfirm();
      await loadAssetData();

      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao deletar operação");
      handleCloseDeleteConfirm();
    } finally {
      setLoading(false);
    }
  }

  function formatCurrency(value: number) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString("pt-BR");
  }

  if (loading && !asset) {
    return (
      <div className="asset-detail-container">
        <div className="loading-spinner">Carregando...</div>
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="asset-detail-container">
        <div className="error-message">Ativo não encontrado</div>
        <button className="btn-primary" onClick={() => navigate("/portfolio")}>
          Voltar para Carteira
        </button>
      </div>
    );
  }

  // Usar métricas calculadas pelo backend (mais eficiente e consistente)
  const totalInvested = asset.total_invested || 0;
  const averagePrice = asset.average_price || 0;

  // Calcular resumo por mercado (para informação)
  const marketSummary = operations.reduce((acc, op) => {
    const market = op.market || "NÃO ESPECIFICADO";
    if (!acc[market]) {
      acc[market] = { bought: 0, sold: 0, operations: 0 };
    }
    if (op.movement_type === "COMPRA") {
      acc[market].bought += op.quantity;
    } else {
      acc[market].sold += op.quantity;
    }
    acc[market].operations += 1;
    return acc;
  }, {} as Record<string, { bought: number; sold: number; operations: number }>);

  return (
    <div className="asset-detail-container">
      <div className="asset-detail-header">
        <button className="btn-back" onClick={() => navigate("/portfolio")}>
          ← Voltar
        </button>
        <div className="asset-info">
          <h1>{asset.ticker}</h1>
          <p>{asset.product_name}</p>
          <span className="asset-badge">{asset.asset_class}</span>
          <span className="asset-badge">{asset.asset_type}</span>
        </div>
        <button className="btn-primary" onClick={handleOpenCreateModal}>
          + Nova Operação
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          <span>✓ {successMessage}</span>
          <button onClick={() => setSuccessMessage(null)}>✕</button>
        </div>
      )}

      {/* Cards de estatísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Posição Atual</div>
          <div className="stat-value">{asset.current_position}</div>
          <div className="stat-note">Consolidada (todos os mercados)</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Preço Médio</div>
          <div className="stat-value">{formatCurrency(averagePrice)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Investido</div>
          <div className="stat-value">{formatCurrency(totalInvested)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total de Operações</div>
          <div className="stat-value">{operations.length}</div>
        </div>
      </div>

      {/* Resumo por mercado */}
      {Object.keys(marketSummary).length > 1 && (
        <div className="market-summary-section">
          <h3>📊 Resumo por Mercado</h3>
          <p className="market-summary-note">
            ℹ️ A posição atual é <strong>consolidada</strong> automaticamente. Operações em mercado à vista e fracionário são somadas.
          </p>
          <div className="market-summary-grid">
            {Object.entries(marketSummary).map(([market, data]) => (
              <div key={market} className="market-summary-card">
                <div className="market-name">{market}</div>
                <div className="market-stats">
                  <div className="market-stat">
                    <span className="market-stat-label">Comprado:</span>
                    <span className="market-stat-value">{data.bought}</span>
                  </div>
                  <div className="market-stat">
                    <span className="market-stat-label">Vendido:</span>
                    <span className="market-stat-value">{data.sold}</span>
                  </div>
                  <div className="market-stat">
                    <span className="market-stat-label">Operações:</span>
                    <span className="market-stat-value">{data.operations}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabela de operações */}
      <div className="operations-section">
        <h2>Histórico de Operações</h2>

        {operations.length === 0 ? (
          <div className="empty-state">
            <p>Nenhuma operação registrada para este ativo</p>
            <button className="btn-primary" onClick={handleOpenCreateModal}>
              Adicionar Primeira Operação
            </button>
          </div>
        ) : (
          <table className="operations-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Tipo</th>
                <th className="text-right">Quantidade</th>
                <th className="text-right">Preço</th>
                <th className="text-right">Valor Total</th>
                <th>Mercado</th>
                <th>Instituição</th>
                <th>Origem</th>
                <th className="text-center">Ações</th>
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
                  <td className="text-right">{operation.quantity}</td>
                  <td className="text-right">{formatCurrency(operation.price)}</td>
                  <td className="text-right">{formatCurrency(operation.value)}</td>
                  <td>{operation.market || "-"}</td>
                  <td>{operation.institution || "-"}</td>
                  <td>
                    <span className={`badge badge-${operation.source.toLowerCase()}`}>
                      {operation.source}
                    </span>
                  </td>
                  <td className="text-center">
                    <div className="action-buttons">
                      <button
                        className="btn-icon btn-edit"
                        onClick={() => handleOpenEditModal(operation)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon btn-delete"
                        onClick={() => handleOpenDeleteConfirm(operation)}
                        title="Deletar"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal de criação/edição */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                {modalMode === "create" ? "Nova Operação" : "Editar Operação"}
              </h2>
              <button className="modal-close" onClick={handleCloseModal}>
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="operation-form">
              <div className="form-group">
                <label htmlFor="movement_type">Tipo de Operação *</label>
                <select
                  id="movement_type"
                  value={formData.movement_type}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      movement_type: e.target.value as "COMPRA" | "VENDA",
                    })
                  }
                  required
                >
                  <option value="COMPRA">Compra</option>
                  <option value="VENDA">Venda</option>
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="quantity">Quantidade *</label>
                  <input
                    id="quantity"
                    type="number"
                    value={formData.quantity}
                    onChange={(e) =>
                      setFormData({ ...formData, quantity: Number(e.target.value) })
                    }
                    min="1"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="price">Preço *</label>
                  <input
                    id="price"
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) =>
                      setFormData({ ...formData, price: Number(e.target.value) })
                    }
                    min="0.01"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="trade_date">Data da Operação *</label>
                <input
                  id="trade_date"
                  type="date"
                  value={formData.trade_date}
                  onChange={(e) =>
                    setFormData({ ...formData, trade_date: e.target.value })
                  }
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="market">Mercado</label>
                  <input
                    id="market"
                    type="text"
                    value={formData.market || ""}
                    onChange={(e) =>
                      setFormData({ ...formData, market: e.target.value })
                    }
                    placeholder="Ex: VISTA"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="institution">Instituição</label>
                  <input
                    id="institution"
                    type="text"
                    value={formData.institution || ""}
                    onChange={(e) =>
                      setFormData({ ...formData, institution: e.target.value })
                    }
                    placeholder="Ex: CLEAR"
                  />
                </div>
              </div>

              <div className="form-summary">
                <strong>Valor Total:</strong>{" "}
                {formatCurrency(formData.quantity * formData.price)}
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCloseModal}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={loading}
                >
                  {loading
                    ? "Salvando..."
                    : modalMode === "create"
                    ? "Criar Operação"
                    : "Salvar Alterações"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de confirmação de delete */}
      {showDeleteConfirm && operationToDelete && (
        <div className="modal-overlay" onClick={handleCloseDeleteConfirm}>
          <div
            className="modal-content modal-small"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>Confirmar Exclusão</h2>
              <button className="modal-close" onClick={handleCloseDeleteConfirm}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <p>Tem certeza que deseja excluir esta operação?</p>
              <p>
                <strong>Tipo:</strong> {operationToDelete.movement_type} <br />
                <strong>Quantidade:</strong> {operationToDelete.quantity} <br />
                <strong>Valor:</strong> {formatCurrency(operationToDelete.value)}
              </p>
            </div>

            <div className="form-actions">
              <button
                className="btn-secondary"
                onClick={handleCloseDeleteConfirm}
              >
                Cancelar
              </button>
              <button
                className="btn-danger"
                onClick={handleConfirmDelete}
                disabled={loading}
              >
                {loading ? "Deletando..." : "Confirmar Exclusão"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
