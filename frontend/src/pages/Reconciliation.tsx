import { useState, useEffect } from "react";
import { fetchAssets, Asset, createPositionAdjustment, PositionAdjustment } from "../api/client";
import "./Reconciliation.css";

export default function Reconciliation() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Estados do formulário
  const [formData, setFormData] = useState<PositionAdjustment>({
    asset_id: 0,
    adjustment_type: "BONIFICACAO",
    quantity: 0,
    event_date: new Date().toISOString().split('T')[0],
    description: "",
  });

  // Estado para exibir cálculo da diferença
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [expectedPosition, setExpectedPosition] = useState<number>(0);

  useEffect(() => {
    loadAssets();
  }, []);

  useEffect(() => {
    if (formData.asset_id > 0) {
      const asset = assets.find(a => a.id === formData.asset_id);
      setSelectedAsset(asset || null);
    } else {
      setSelectedAsset(null);
    }
  }, [formData.asset_id, assets]);

  async function loadAssets() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAssets();
      // Filtrar apenas ativos com posição
      const withPosition = data.filter(a => a.current_position && a.current_position > 0);
      setAssets(withPosition);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar ativos");
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(field: keyof PositionAdjustment, value: any) {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }

  function calculateDifference(): number {
    if (!selectedAsset || expectedPosition === 0) return 0;
    return expectedPosition - (selectedAsset.current_position || 0);
  }

  function getAdjustmentSuggestion(): string {
    const diff = calculateDifference();
    if (diff === 0) return "";
    if (diff > 0) return `Registrar bonificação de +${diff} ações`;
    return `Corrigir posição com ajuste de ${diff} ações`;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    if (!selectedAsset) {
      setError("Selecione um ativo");
      return;
    }

    if (!formData.description.trim()) {
      setError("Descrição é obrigatória");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccessMessage(null);

      await createPositionAdjustment(formData);

      setSuccessMessage(
        `Ajuste registrado com sucesso! Posição de ${selectedAsset.ticker} atualizada.`
      );

      // Limpar formulário
      setFormData({
        asset_id: 0,
        adjustment_type: "BONIFICACAO",
        quantity: 0,
        event_date: new Date().toISOString().split('T')[0],
        description: "",
      });
      setExpectedPosition(0);

      // Recarregar ativos
      await loadAssets();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao registrar ajuste");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="reconciliation-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Carregando ativos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reconciliation-page">
      <header className="page-header">
        <h1>🔍 Reconciliação de Posição</h1>
        <p className="subtitle">
          Ajuste manual de posições para eventos corporativos (bonificações, desdobros, etc)
        </p>
      </header>

      {error && (
        <div className="alert alert-error">
          ❌ {error}
          <button onClick={() => setError(null)} className="alert-close">×</button>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success">
          ✅ {successMessage}
          <button onClick={() => setSuccessMessage(null)} className="alert-close">×</button>
        </div>
      )}

      <div className="reconciliation-content">
        <div className="info-card">
          <h3>ℹ️ Quando usar esta ferramenta?</h3>
          <ul>
            <li><strong>Bonificações:</strong> A empresa distribuiu ações gratuitas</li>
            <li><strong>Desdobros:</strong> Cada ação virou N ações (split)</li>
            <li><strong>Grupamentos:</strong> N ações viraram 1 (reverse split)</li>
            <li><strong>Subscrições:</strong> Você exerceu direitos de subscrição</li>
            <li><strong>Correções:</strong> Erro de importação ou digitação</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="reconciliation-form">
          <div className="form-section">
            <h3>1. Selecione o Ativo</h3>
            
            <div className="form-group">
              <label htmlFor="asset_id">Ativo *</label>
              <select
                id="asset_id"
                value={formData.asset_id}
                onChange={(e) => handleInputChange("asset_id", parseInt(e.target.value))}
                required
                className="form-control"
              >
                <option value={0}>Selecione um ativo...</option>
                {assets.map((asset) => (
                  <option key={asset.id} value={asset.id}>
                    {asset.ticker} - {asset.product_name} (Posição: {asset.current_position})
                  </option>
                ))}
              </select>
            </div>

            {selectedAsset && (
              <div className="position-info">
                <div className="info-row">
                  <span className="label">Posição calculada:</span>
                  <span className="value">{selectedAsset.current_position} ações</span>
                </div>
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>2. Informe a Posição Real (B3)</h3>
            
            <div className="form-group">
              <label htmlFor="expected_position">
                Posição real na B3 *
                <span className="hint">Digite a quantidade que aparece no extrato da B3</span>
              </label>
              <input
                type="number"
                id="expected_position"
                value={expectedPosition}
                onChange={(e) => setExpectedPosition(parseFloat(e.target.value) || 0)}
                min="0"
                step="0.01"
                required
                className="form-control"
                placeholder="Ex: 1058"
              />
            </div>

            {selectedAsset && expectedPosition > 0 && (
              <div className={`difference-info ${calculateDifference() !== 0 ? 'has-difference' : 'no-difference'}`}>
                <div className="info-row">
                  <span className="label">Diferença:</span>
                  <span className={`value ${calculateDifference() > 0 ? 'positive' : calculateDifference() < 0 ? 'negative' : ''}`}>
                    {calculateDifference() > 0 ? '+' : ''}{calculateDifference()} ações
                    {calculateDifference() !== 0 && (
                      <span className="percentage">
                        ({((Math.abs(calculateDifference()) / (selectedAsset.current_position || 1)) * 100).toFixed(2)}%)
                      </span>
                    )}
                  </span>
                </div>
                
                {calculateDifference() !== 0 && (
                  <div className="suggestion">
                    <strong>💡 Sugestão:</strong> {getAdjustmentSuggestion()}
                  </div>
                )}
              </div>
            )}
          </div>

          {calculateDifference() !== 0 && (
            <div className="form-section">
              <h3>3. Registre o Ajuste</h3>
              
              <div className="form-group">
                <label htmlFor="adjustment_type">Tipo de Evento *</label>
                <select
                  id="adjustment_type"
                  value={formData.adjustment_type}
                  onChange={(e) => handleInputChange("adjustment_type", e.target.value)}
                  required
                  className="form-control"
                >
                  <option value="BONIFICACAO">Bonificação (ações gratuitas)</option>
                  <option value="DESDOBRO">Desdobro (split)</option>
                  <option value="GRUPAMENTO">Grupamento (reverse split)</option>
                  <option value="SUBSCRICAO">Subscrição (direitos exercidos)</option>
                  <option value="CORRECAO">Correção manual</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="quantity">
                  Quantidade a Ajustar *
                  <span className="hint">Automático baseado na diferença calculada</span>
                </label>
                <input
                  type="number"
                  id="quantity"
                  value={formData.quantity || calculateDifference()}
                  onChange={(e) => handleInputChange("quantity", parseFloat(e.target.value) || 0)}
                  step="0.01"
                  required
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label htmlFor="event_date">Data do Evento *</label>
                <input
                  type="date"
                  id="event_date"
                  value={formData.event_date}
                  onChange={(e) => handleInputChange("event_date", e.target.value)}
                  required
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">
                  Descrição *
                  <span className="hint">Ex: "Bonificação 10% dezembro/2025"</span>
                </label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange("description", e.target.value)}
                  required
                  className="form-control"
                  rows={3}
                  placeholder="Descreva o motivo do ajuste..."
                />
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary"
                >
                  {submitting ? "Salvando..." : "💾 Salvar Ajuste"}
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setFormData({
                      asset_id: 0,
                      adjustment_type: "BONIFICACAO",
                      quantity: 0,
                      event_date: new Date().toISOString().split('T')[0],
                      description: "",
                    });
                    setExpectedPosition(0);
                  }}
                  className="btn btn-secondary"
                >
                  Limpar
                </button>
              </div>
            </div>
          )}

          {calculateDifference() === 0 && expectedPosition > 0 && (
            <div className="alert alert-info">
              ✅ Posições estão corretas! Não há necessidade de ajuste.
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
