import { useState, useEffect } from 'react';
import {
  listFixedIncomeAssets,
  createFixedIncomeAsset,
  createFixedIncomeOperation,
  deleteFixedIncomeAsset,
  getFixedIncomeProjection,
  createAsset,
  type FixedIncomeAsset,
  type FixedIncomeAssetCreate,
  type FixedIncomeOperationCreate,
  type FixedIncomeProjection
} from '../api/client';
import './FixedIncome.css';

export default function FixedIncome() {
  const [assets, setAssets] = useState<FixedIncomeAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [showNewAssetModal, setShowNewAssetModal] = useState(false);
  const [showOperationModal, setShowOperationModal] = useState(false);
  const [showProjectionModal, setShowProjectionModal] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<FixedIncomeAsset | null>(null);
  const [projection, setProjection] = useState<FixedIncomeProjection | null>(null);

  // Form states
  const [formData, setFormData] = useState<{
    ticker: string;
    product_name: string;
    issuer: string;
    product_type: string;
    indexer: string;
    rate: string;
    maturity_date: string;
    issue_date: string;
    custody_fee: string;
  }>({
    ticker: '',
    product_name: '',
    issuer: '',
    product_type: 'CDB',
    indexer: 'CDI',
    rate: '',
    maturity_date: '',
    issue_date: '',
    custody_fee: '0'
  });

  const [operationData, setOperationData] = useState<{
    operation_type: 'APLICACAO' | 'RESGATE' | 'VENCIMENTO';
    amount: string;
    trade_date: string;
    net_amount: string;
    ir_amount: string;
  }>({
    operation_type: 'APLICACAO',
    amount: '',
    trade_date: new Date().toISOString().split('T')[0],
    net_amount: '',
    ir_amount: '0'
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const data = await listFixedIncomeAssets();
      setAssets(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar ativos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // Primeiro criar o asset base
      const assetResponse = await createAsset({
        ticker: formData.ticker,
        asset_class: 'RENDA FIXA',
        asset_type: formData.product_type,
        product_name: formData.product_name
      });

      // Depois criar as informações de RF
      await createFixedIncomeAsset({
        asset_id: assetResponse.asset_id,
        issuer: formData.issuer,
        product_type: formData.product_type,
        indexer: formData.indexer,
        rate: parseFloat(formData.rate),
        maturity_date: formData.maturity_date,
        issue_date: formData.issue_date,
        custody_fee: parseFloat(formData.custody_fee)
      });

      setSuccess('Ativo de Renda Fixa criado com sucesso!');
      setShowNewAssetModal(false);
      resetForm();
      fetchAssets();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar ativo');
    }
  };

  const handleCreateOperation = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedAsset) return;

    try {
      const opData: FixedIncomeOperationCreate = {
        asset_id: selectedAsset.asset_id,
        operation_type: operationData.operation_type,
        amount: parseFloat(operationData.amount),
        trade_date: operationData.trade_date,
        net_amount: operationData.net_amount ? parseFloat(operationData.net_amount) : null,
        ir_amount: parseFloat(operationData.ir_amount)
      };

      await createFixedIncomeOperation(opData);
      
      setSuccess(`${operationData.operation_type} registrada com sucesso!`);
      setShowOperationModal(false);
      resetOperationForm();
      fetchAssets();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar operação');
    }
  };

  const handleDelete = async (assetId: number, ticker: string) => {
    if (!confirm(`Tem certeza que deseja deletar ${ticker}?`)) return;

    try {
      await deleteFixedIncomeAsset(assetId);
      setSuccess('Ativo deletado com sucesso!');
      fetchAssets();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao deletar ativo');
    }
  };

  const handleShowProjection = async (asset: FixedIncomeAsset) => {
    try {
      setSelectedAsset(asset);
      const proj = await getFixedIncomeProjection(asset.asset_id);
      setProjection(proj);
      setShowProjectionModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao calcular projeção');
    }
  };

  const resetForm = () => {
    setFormData({
      ticker: '',
      product_name: '',
      issuer: '',
      product_type: 'CDB',
      indexer: 'CDI',
      rate: '',
      maturity_date: '',
      issue_date: '',
      custody_fee: '0'
    });
  };

  const resetOperationForm = () => {
    setOperationData({
      operation_type: 'APLICACAO',
      amount: '',
      trade_date: new Date().toISOString().split('T')[0],
      net_amount: '',
      ir_amount: '0'
    });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const calculateDaysToMaturity = (maturityDate: string) => {
    const today = new Date();
    const maturity = new Date(maturityDate);
    const diff = maturity.getTime() - today.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  const totalInvested = assets.reduce((sum, a) => sum + a.total_invested, 0);
  const totalRedeemed = assets.reduce((sum, a) => sum + a.total_redeemed, 0);
  const currentBalance = totalInvested - totalRedeemed;

  return (
    <div className="fixed-income-container">
      <div className="fixed-income-header">
        <h1>Renda Fixa</h1>
        <button className="btn-primary" onClick={() => setShowNewAssetModal(true)}>
          + Novo Investimento
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
          <button onClick={() => setSuccess(null)}>×</button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total de Ativos</div>
          <div className="stat-value">{assets.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Investido</div>
          <div className="stat-value">{formatCurrency(totalInvested)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Resgatado</div>
          <div className="stat-value">{formatCurrency(totalRedeemed)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Saldo Atual</div>
          <div className="stat-value">{formatCurrency(currentBalance)}</div>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">Carregando investimentos...</div>
      ) : assets.length === 0 ? (
        <div className="empty-state">
          <p>Nenhum investimento em Renda Fixa cadastrado</p>
          <button className="btn-primary" onClick={() => setShowNewAssetModal(true)}>
            Adicionar Primeiro Investimento
          </button>
        </div>
      ) : (
        <div className="fixed-income-table-container">
          <table className="fixed-income-table">
            <thead>
              <tr>
                <th>Produto</th>
                <th>Emissor</th>
                <th>Indexador</th>
                <th>Taxa</th>
                <th>Vencimento</th>
                <th className="text-right">Saldo Atual</th>
                <th className="text-center">Ações</th>
              </tr>
            </thead>
            <tbody>
              {assets.map(asset => {
                const daysToMaturity = calculateDaysToMaturity(asset.maturity_date);
                const isNearMaturity = daysToMaturity <= 30 && daysToMaturity > 0;
                const isMatured = daysToMaturity <= 0;

                return (
                  <tr key={asset.id}>
                    <td>
                      <div className="asset-info">
                        <strong>{asset.ticker}</strong>
                        <small>{asset.product_name}</small>
                      </div>
                    </td>
                    <td>{asset.issuer}</td>
                    <td>
                      {asset.indexer}
                      {asset.custody_fee > 0 && (
                        <small className="custody-fee"> (Custódia: {asset.custody_fee}%)</small>
                      )}
                    </td>
                    <td>{asset.rate}%</td>
                    <td>
                      <div className={`maturity-info ${isNearMaturity ? 'near-maturity' : ''} ${isMatured ? 'matured' : ''}`}>
                        {formatDate(asset.maturity_date)}
                        <small>
                          {isMatured ? 'Vencido' : `${daysToMaturity} dias`}
                        </small>
                      </div>
                    </td>
                    <td className="text-right">
                      <strong>{formatCurrency(asset.current_balance)}</strong>
                    </td>
                    <td className="text-center">
                      <div className="action-buttons">
                        <button
                          className="btn-icon btn-view"
                          title="Ver Projeção"
                          onClick={() => handleShowProjection(asset)}
                        >
                          📊
                        </button>
                        <button
                          className="btn-icon btn-edit"
                          title="Nova Operação"
                          onClick={() => {
                            setSelectedAsset(asset);
                            setShowOperationModal(true);
                          }}
                        >
                          💰
                        </button>
                        <button
                          className="btn-icon btn-delete"
                          title="Deletar"
                          onClick={() => handleDelete(asset.asset_id, asset.ticker)}
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal: Novo Ativo */}
      {showNewAssetModal && (
        <div className="modal-overlay" onClick={() => setShowNewAssetModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Novo Investimento em Renda Fixa</h2>
              <button className="modal-close" onClick={() => setShowNewAssetModal(false)}>×</button>
            </div>
            <form className="asset-form" onSubmit={handleCreateAsset}>
              <div className="form-group">
                <label>Código/Identificador *</label>
                <input
                  type="text"
                  value={formData.ticker}
                  onChange={e => setFormData({...formData, ticker: e.target.value})}
                  placeholder="Ex: CDB_BANCO_XYZ_2026"
                  required
                />
              </div>

              <div className="form-group">
                <label>Nome do Produto *</label>
                <input
                  type="text"
                  value={formData.product_name}
                  onChange={e => setFormData({...formData, product_name: e.target.value})}
                  placeholder="Ex: CDB Banco XYZ 110% CDI"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Emissor *</label>
                  <input
                    type="text"
                    value={formData.issuer}
                    onChange={e => setFormData({...formData, issuer: e.target.value})}
                    placeholder="Ex: Banco XYZ"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Tipo de Produto *</label>
                  <select
                    value={formData.product_type}
                    onChange={e => setFormData({...formData, product_type: e.target.value})}
                    required
                  >
                    <option value="CDB">CDB</option>
                    <option value="LCI">LCI (Isento de IR)</option>
                    <option value="LCA">LCA (Isento de IR)</option>
                    <option value="TESOURO_SELIC">Tesouro Selic</option>
                    <option value="TESOURO_IPCA">Tesouro IPCA+</option>
                    <option value="TESOURO_PREFIXADO">Tesouro Prefixado</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Indexador *</label>
                  <select
                    value={formData.indexer}
                    onChange={e => setFormData({...formData, indexer: e.target.value})}
                    required
                  >
                    <option value="CDI">CDI</option>
                    <option value="IPCA">IPCA</option>
                    <option value="PRE">Pré-fixado</option>
                    <option value="SELIC">Selic</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Taxa Contratada (%) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.rate}
                    onChange={e => setFormData({...formData, rate: e.target.value})}
                    placeholder="Ex: 110.00"
                    required
                  />
                  <small>Para CDI: 110 = 110% do CDI. Para IPCA+: taxa fixa acima da inflação.</small>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Data de Emissão *</label>
                  <input
                    type="date"
                    value={formData.issue_date}
                    onChange={e => setFormData({...formData, issue_date: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Data de Vencimento *</label>
                  <input
                    type="date"
                    value={formData.maturity_date}
                    onChange={e => setFormData({...formData, maturity_date: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Taxa de Custódia Anual (%) - Apenas Tesouro</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.custody_fee}
                  onChange={e => setFormData({...formData, custody_fee: e.target.value})}
                  placeholder="0.20"
                />
                <small>Tesouro Direto: 0.20% (exceto Selic até R$ 10k)</small>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowNewAssetModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Criar Investimento
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Nova Operação */}
      {showOperationModal && selectedAsset && (
        <div className="modal-overlay" onClick={() => setShowOperationModal(false)}>
          <div className="modal-content modal-small" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nova Operação - {selectedAsset.ticker}</h2>
              <button className="modal-close" onClick={() => setShowOperationModal(false)}>×</button>
            </div>
            <form className="asset-form" onSubmit={handleCreateOperation}>
              <div className="form-group">
                <label>Tipo de Operação *</label>
                <select
                  value={operationData.operation_type}
                  onChange={e => setOperationData({...operationData, operation_type: e.target.value as any})}
                  required
                >
                  <option value="APLICACAO">Aplicação</option>
                  <option value="RESGATE">Resgate</option>
                  <option value="VENCIMENTO">Vencimento</option>
                </select>
              </div>

              <div className="form-group">
                <label>Valor Bruto (R$) *</label>
                <input
                  type="number"
                  step="0.01"
                  value={operationData.amount}
                  onChange={e => setOperationData({...operationData, amount: e.target.value})}
                  placeholder="10000.00"
                  required
                />
              </div>

              <div className="form-group">
                <label>Data da Operação *</label>
                <input
                  type="date"
                  value={operationData.trade_date}
                  onChange={e => setOperationData({...operationData, trade_date: e.target.value})}
                  required
                />
              </div>

              {(operationData.operation_type === 'RESGATE' || operationData.operation_type === 'VENCIMENTO') && (
                <>
                  <div className="form-group">
                    <label>Valor Líquido (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={operationData.net_amount}
                      onChange={e => setOperationData({...operationData, net_amount: e.target.value})}
                      placeholder="Após IR"
                    />
                  </div>

                  <div className="form-group">
                    <label>IR Retido (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={operationData.ir_amount}
                      onChange={e => setOperationData({...operationData, ir_amount: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                </>
              )}

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowOperationModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Registrar Operação
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Projeção */}
      {showProjectionModal && projection && (
        <div className="modal-overlay" onClick={() => setShowProjectionModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Projeção de Rendimento - {projection.ticker}</h2>
              <button className="modal-close" onClick={() => setShowProjectionModal(false)}>×</button>
            </div>
            <div className="projection-content">
              <div className="projection-info">
                <div className="info-row">
                  <span>Tipo:</span>
                  <strong>{projection.product_type}</strong>
                </div>
                <div className="info-row">
                  <span>Indexador:</span>
                  <strong>{projection.indexer} {projection.rate_contracted}%</strong>
                </div>
                <div className="info-row">
                  <span>Vencimento:</span>
                  <strong>{formatDate(projection.maturity_date)} ({projection.days_to_maturity} dias)</strong>
                </div>
                <div className="info-row">
                  <span>Taxa Anual Usada:</span>
                  <strong>{projection.annual_rate_used.toFixed(2)}%</strong>
                </div>
              </div>

              <div className="projection-values">
                <div className="value-card">
                  <div className="value-label">Saldo Atual</div>
                  <div className="value-amount">{formatCurrency(projection.current_balance)}</div>
                </div>

                <div className="value-card">
                  <div className="value-label">Projeção Bruta (no vencimento)</div>
                  <div className="value-amount">{formatCurrency(projection.gross_projection)}</div>
                  <div className="value-gain positive">+{formatCurrency(projection.gross_gain)}</div>
                </div>

                <div className="value-card">
                  <div className="value-label">IR {projection.ir_rate}%</div>
                  <div className="value-amount negative">-{formatCurrency(projection.ir_amount)}</div>
                </div>

                {projection.custody_fee_amount > 0 && (
                  <div className="value-card">
                    <div className="value-label">Taxa de Custódia</div>
                    <div className="value-amount negative">-{formatCurrency(projection.custody_fee_amount)}</div>
                  </div>
                )}

                <div className="value-card highlight">
                  <div className="value-label">Valor Líquido Projetado</div>
                  <div className="value-amount">{formatCurrency(projection.net_projection)}</div>
                  <div className="value-gain positive">Ganho: +{formatCurrency(projection.net_gain)}</div>
                  <div className="value-percentage">
                    +{((projection.net_gain / projection.current_balance) * 100).toFixed(2)}%
                  </div>
                </div>
              </div>

              <div className="projection-disclaimer">
                ⚠️ Esta é uma projeção baseada nas taxas atuais de mercado (CDI {13.75}%, IPCA {4.5}%). 
                O valor real pode variar conforme as oscilações do indexador.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
