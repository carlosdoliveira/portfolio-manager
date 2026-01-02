import { useState } from "react";
import type { OperationCreate } from "../api/client";
import "./OperationForm.css";

interface OperationFormProps {
  initialData?: OperationCreate;
  onSubmit: (operation: OperationCreate) => Promise<void>;
  onCancel: () => void;
  submitLabel?: string;
}

export function OperationForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = "Salvar",
}: OperationFormProps) {
  const [formData, setFormData] = useState<OperationCreate>(
    initialData || {
      asset_class: "Renda Variável",
      asset_type: "Ações",
      product_name: "",
      ticker: "",
      movement_type: "COMPRA",
      quantity: 0,
      price: 0,
      trade_date: new Date().toISOString().split("T")[0],
      market: "MERCADO A VISTA",
      institution: "",
    }
  );

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "quantity"
          ? parseInt(value) || 0
          : name === "price"
          ? parseFloat(value) || 0
          : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="operation-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="asset_class">Classe do Ativo *</label>
          <select
            id="asset_class"
            name="asset_class"
            value={formData.asset_class}
            onChange={handleChange}
            required
          >
            <option value="Renda Variável">Renda Variável</option>
            <option value="Renda Fixa">Renda Fixa</option>
            <option value="FII">FII</option>
            <option value="BDR">BDR</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="asset_type">Tipo do Ativo *</label>
          <input
            type="text"
            id="asset_type"
            name="asset_type"
            value={formData.asset_type}
            onChange={handleChange}
            placeholder="Ex: Ações, Debêntures, etc."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="product_name">Nome do Produto *</label>
          <input
            type="text"
            id="product_name"
            name="product_name"
            value={formData.product_name}
            onChange={handleChange}
            placeholder="Ex: Petrobras PN"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="ticker">Ticker</label>
          <input
            type="text"
            id="ticker"
            name="ticker"
            value={formData.ticker || ""}
            onChange={handleChange}
            placeholder="Ex: PETR4"
          />
        </div>

        <div className="form-group">
          <label htmlFor="movement_type">Tipo de Movimentação *</label>
          <select
            id="movement_type"
            name="movement_type"
            value={formData.movement_type}
            onChange={handleChange}
            required
          >
            <option value="COMPRA">Compra</option>
            <option value="VENDA">Venda</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="quantity">Quantidade *</label>
          <input
            type="number"
            id="quantity"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            min="1"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="price">Preço Unitário (R$) *</label>
          <input
            type="number"
            id="price"
            name="price"
            value={formData.price}
            onChange={handleChange}
            step="0.01"
            min="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="trade_date">Data da Operação *</label>
          <input
            type="date"
            id="trade_date"
            name="trade_date"
            value={formData.trade_date}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="market">Mercado</label>
          <input
            type="text"
            id="market"
            name="market"
            value={formData.market || ""}
            onChange={handleChange}
            placeholder="Ex: MERCADO A VISTA"
          />
        </div>

        <div className="form-group">
          <label htmlFor="institution">Instituição</label>
          <input
            type="text"
            id="institution"
            name="institution"
            value={formData.institution || ""}
            onChange={handleChange}
            placeholder="Ex: Corretora XP"
          />
        </div>
      </div>

      <div className="form-summary">
        <strong>Valor Total:</strong>{" "}
        R$ {(formData.quantity * formData.price).toFixed(2)}
      </div>

      <div className="form-actions">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
          disabled={isSubmitting}
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Salvando..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
