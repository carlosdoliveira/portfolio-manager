import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchAssets, createAsset, updateAsset, deleteAsset, Asset, AssetCreate } from "../api/client";
import "./Portfolio.css";

export default function Portfolio() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Estados para modal
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState<"create" | "edit">("create");
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  
  // Estados para confirmação de delete
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [assetToDelete, setAssetToDelete] = useState<Asset | null>(null);
  
  // Estados do formulário
  const [formData, setFormData] = useState<AssetCreate>({
    ticker: "",
    asset_class: "AÇÕES",
    asset_type: "ON",
    product_name: "",
  });

  const navigate = useNavigate();

  useEffect(() => {
    loadAssets();
  }, []);

  async function loadAssets() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAssets();
      setAssets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar ativos");
    } finally {
      setLoading(false);
    }
  }

  function handleOpenCreateModal() {
    setModalMode("create");
    setEditingAsset(null);
    setFormData({
      ticker: "",
      asset_class: "AÇÕES",
      asset_type: "ON",
      product_name: "",
    });
    setShowModal(true);
  }

  function handleOpenEditModal(asset: Asset) {
    setModalMode("edit");
    setEditingAsset(asset);
    setFormData({
      ticker: asset.ticker,
      asset_class: asset.asset_class,
      asset_type: asset.asset_type,
      product_name: asset.product_name,
    });
    setShowModal(true);
  }

  function handleCloseModal() {
    setShowModal(false);
    setEditingAsset(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      if (modalMode === "create") {
        await createAsset(formData);
        setSuccessMessage("Ativo criado com sucesso!");
      } else if (editingAsset) {
        await updateAsset(editingAsset.id, formData);
        setSuccessMessage("Ativo atualizado com sucesso!");
      }
      
      handleCloseModal();
      await loadAssets();
      
      // Limpar mensagem de sucesso após 3 segundos
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar ativo");
    } finally {
      setLoading(false);
    }
  }

  function handleOpenDeleteConfirm(asset: Asset) {
    setAssetToDelete(asset);
    setShowDeleteConfirm(true);
  }

  function handleCloseDeleteConfirm() {
    setShowDeleteConfirm(false);
    setAssetToDelete(null);
  }

  async function handleConfirmDelete() {
    if (!assetToDelete) return;
    
    try {
      setLoading(true);
      await deleteAsset(assetToDelete.id);
      setSuccessMessage("Ativo deletado com sucesso!");
      handleCloseDeleteConfirm();
      await loadAssets();
      
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao deletar ativo");
      handleCloseDeleteConfirm();
    } finally {
      setLoading(false);
    }
  }

  function handleViewAsset(assetId: number) {
    navigate(`/portfolio/${assetId}`);
  }

  // Função para formatar moeda brasileira
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  // Calcular totalizadores
  const totalAssets = assets.length;
  const totalBoughtValue = assets.reduce((sum, asset) => sum + (asset.total_bought_value || 0), 0);
  const totalSoldValue = assets.reduce((sum, asset) => sum + (asset.total_sold_value || 0), 0);
  
  // Total Investido = Compras - Vendas (quanto ainda está aplicado)
  const totalInvested = totalBoughtValue - totalSoldValue;
  
  // Valor Atual da Carteira = Preço de mercado D-1 * Posição atual (FUTURO)
  // Por enquanto é um placeholder até implementarmos integração com cotações
  const portfolioMarketValue = null; // Será: sum(preco_atual * posicao_atual)

  if (loading && assets.length === 0) {
    return (
      <div className="portfolio-container">
        <div className="loading-spinner">Carregando ativos...</div>
      </div>
    );
  }

  return (
    <div className="portfolio-container">
      <div className="portfolio-header">
        <h1>Carteira de Investimentos</h1>
        <button className="btn-primary" onClick={handleOpenCreateModal}>
          + Novo Ativo
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
          <div className="stat-label">Total de Ativos</div>
          <div className="stat-value">{totalAssets}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Valor Atual da Carteira</div>
          <div className="stat-value">
            {portfolioMarketValue !== null 
              ? formatCurrency(portfolioMarketValue)
              : '---'
            }
          </div>
          <div className="stat-sublabel" style={{ fontSize: '0.75rem', color: '#888', marginTop: '4px' }}>
            Aguardando integração com cotações
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Investido</div>
          <div className="stat-value">{formatCurrency(totalInvested)}</div>
          <div className="stat-sublabel" style={{ fontSize: '0.75rem', color: '#888', marginTop: '4px' }}>
            Compras - Vendas
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Resgatado</div>
          <div className="stat-value">{formatCurrency(totalSoldValue)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total de Operações</div>
          <div className="stat-value">
            {assets.reduce((sum, asset) => sum + asset.total_operations, 0)}
          </div>
        </div>
      </div>

      {/* Tabela de ativos */}
      <div className="portfolio-table-container">
        {assets.length === 0 ? (
          <div className="empty-state">
            <p>Nenhum ativo na carteira</p>
            <button className="btn-primary" onClick={handleOpenCreateModal}>
              Adicionar Primeiro Ativo
            </button>
          </div>
        ) : (
          <table className="portfolio-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Nome do Produto</th>
                <th>Classe</th>
                <th>Tipo</th>
                <th className="text-right">Posição Atual (qtd)</th>
                <th className="text-right">Total Comprado (R$)</th>
                <th className="text-right">Total Vendido (R$)</th>
                <th className="text-right">Operações</th>
                <th className="text-center">Ações</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id} className="asset-row">
                  <td>
                    <strong className="ticker-link" onClick={() => handleViewAsset(asset.id)}>
                      {asset.ticker}
                    </strong>
                  </td>
                  <td>{asset.product_name}</td>
                  <td>{asset.asset_class}</td>
                  <td>{asset.asset_type}</td>
                  <td className="text-right">{asset.current_position.toLocaleString('pt-BR')}</td>
                  <td className="text-right">{formatCurrency(asset.total_bought_value || 0)}</td>
                  <td className="text-right">{formatCurrency(asset.total_sold_value || 0)}</td>
                  <td className="text-right">{asset.total_operations}</td>
                  <td className="text-center">
                    <div className="action-buttons">
                      <button
                        className="btn-icon btn-view"
                        onClick={() => handleViewAsset(asset.id)}
                        title="Ver detalhes"
                      >
                        👁️
                      </button>
                      <button
                        className="btn-icon btn-edit"
                        onClick={() => handleOpenEditModal(asset)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon btn-delete"
                        onClick={() => handleOpenDeleteConfirm(asset)}
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
              <h2>{modalMode === "create" ? "Novo Ativo" : "Editar Ativo"}</h2>
              <button className="modal-close" onClick={handleCloseModal}>✕</button>
            </div>
            
            <form onSubmit={handleSubmit} className="asset-form">
              <div className="form-group">
                <label htmlFor="ticker">Ticker *</label>
                <input
                  id="ticker"
                  type="text"
                  value={formData.ticker}
                  onChange={(e) => setFormData({ ...formData, ticker: e.target.value.toUpperCase() })}
                  placeholder="Ex: PETR4"
                  required
                  maxLength={10}
                />
              </div>

              <div className="form-group">
                <label htmlFor="product_name">Nome do Produto *</label>
                <input
                  id="product_name"
                  type="text"
                  value={formData.product_name}
                  onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                  placeholder="Ex: Petrobras PN"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="asset_class">Classe *</label>
                  <select
                    id="asset_class"
                    value={formData.asset_class}
                    onChange={(e) => setFormData({ ...formData, asset_class: e.target.value })}
                    required
                  >
                    <option value="AÇÕES">Ações</option>
                    <option value="FII">Fundos Imobiliários</option>
                    <option value="ETF">ETFs</option>
                    <option value="BDR">BDRs</option>
                    <option value="RENDA_FIXA">Renda Fixa</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="asset_type">Tipo *</label>
                  <input
                    id="asset_type"
                    type="text"
                    value={formData.asset_type}
                    onChange={(e) => setFormData({ ...formData, asset_type: e.target.value.toUpperCase() })}
                    placeholder="Ex: ON, PN"
                    required
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={handleCloseModal}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? "Salvando..." : modalMode === "create" ? "Criar Ativo" : "Salvar Alterações"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de confirmação de delete */}
      {showDeleteConfirm && assetToDelete && (
        <div className="modal-overlay" onClick={handleCloseDeleteConfirm}>
          <div className="modal-content modal-small" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Confirmar Exclusão</h2>
              <button className="modal-close" onClick={handleCloseDeleteConfirm}>✕</button>
            </div>
            
            <div className="modal-body">
              <p>Tem certeza que deseja excluir o ativo <strong>{assetToDelete.ticker}</strong>?</p>
              <p className="warning-text">
                ⚠️ Esta ação só será permitida se o ativo não tiver operações ativas.
              </p>
            </div>

            <div className="form-actions">
              <button className="btn-secondary" onClick={handleCloseDeleteConfirm}>
                Cancelar
              </button>
              <button className="btn-danger" onClick={handleConfirmDelete} disabled={loading}>
                {loading ? "Deletando..." : "Confirmar Exclusão"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

