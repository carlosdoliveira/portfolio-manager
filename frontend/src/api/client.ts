// Configuração da URL da API via variável de ambiente
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ========== INTERFACES DE ATIVOS ==========

export interface Asset {
  id: number;
  ticker: string;
  asset_class: string;
  asset_type: string;
  product_name: string;
  created_at: string;
  status: string;
  total_operations: number;
  total_bought: number;
  total_sold: number;
  current_position: number;
  total_bought_value: number;
  total_sold_value: number;
  average_price?: number;  // Preço médio de compra (backend calcula)
  total_invested?: number; // Total investido em compras (alias de total_bought_value)
}

export interface AssetCreate {
  ticker: string;
  asset_class: string;
  asset_type: string;
  product_name: string;
}

export interface AssetUpdate {
  ticker: string;
  asset_class: string;
  asset_type: string;
  product_name: string;
}

// ========== INTERFACES DE OPERAÇÕES ==========

export interface Operation {
  id: number;
  asset_id: number;
  ticker: string;
  asset_class: string;
  asset_type: string;
  product_name: string;
  movement_type: "COMPRA" | "VENDA";
  quantity: number;
  price: number;
  value: number;
  trade_date: string;
  source: string;
  created_at: string;
  status: string;
  market?: string | null;
  institution?: string | null;
}

export interface OperationCreate {
  asset_id: number;
  movement_type: "COMPRA" | "VENDA";
  quantity: number;
  price: number;
  trade_date: string;
  market?: string | null;
  institution?: string | null;
}

// ========== FUNÇÕES DE IMPORTAÇÃO ==========

export async function uploadB3File(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/import/b3`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    // Tentar extrair mensagem de erro do backend
    const error = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(error.detail || "Erro ao importar arquivo");
  }

  return response.json();
}

// ========== FUNÇÕES DE ATIVOS ==========

export async function fetchAssets(): Promise<Asset[]> {
  const response = await fetch(`${API_URL}/assets`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao carregar ativos" }));
    throw new Error(error.detail || "Erro ao carregar ativos");
  }
  
  return response.json();
}

export async function fetchAssetById(id: number): Promise<Asset> {
  const response = await fetch(`${API_URL}/assets/${id}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao buscar ativo" }));
    throw new Error(error.detail || "Erro ao buscar ativo");
  }
  
  return response.json();
}

export async function createAsset(asset: AssetCreate): Promise<{ status: string; asset_id: number }> {
  const response = await fetch(`${API_URL}/assets`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(asset),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao criar ativo" }));
    throw new Error(error.detail || "Erro ao criar ativo");
  }
  
  return response.json();
}

export async function updateAsset(id: number, asset: AssetUpdate): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_URL}/assets/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(asset),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao atualizar ativo" }));
    throw new Error(error.detail || "Erro ao atualizar ativo");
  }
  
  return response.json();
}

export async function deleteAsset(id: number): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_URL}/assets/${id}`, {
    method: "DELETE",
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao deletar ativo" }));
    throw new Error(error.detail || "Erro ao deletar ativo");
  }
  
  return response.json();
}

export async function fetchAssetOperations(assetId: number): Promise<Operation[]> {
  const response = await fetch(`${API_URL}/assets/${assetId}/operations`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao carregar operações do ativo" }));
    throw new Error(error.detail || "Erro ao carregar operações do ativo");
  }
  
  return response.json();
}

// ========== FUNÇÕES DE OPERAÇÕES ==========

export async function fetchOperations(): Promise<Operation[]> {
  const response = await fetch(`${API_URL}/operations`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao carregar operações" }));
    throw new Error(error.detail || "Erro ao carregar operações");
  }
  
  return response.json();
}

export async function fetchOperationById(id: number): Promise<Operation> {
  const response = await fetch(`${API_URL}/operations/${id}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao buscar operação" }));
    throw new Error(error.detail || "Erro ao buscar operação");
  }
  
  return response.json();
}

export async function createOperation(operation: OperationCreate): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/operations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(operation),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao criar operação" }));
    throw new Error(error.detail || "Erro ao criar operação");
  }

  return response.json();
}

export async function updateOperation(
  id: number,
  operation: OperationCreate
): Promise<{ status: string; message: string; old_id: number; new_id: number }> {
  const response = await fetch(`${API_URL}/operations/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(operation),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao atualizar operação" }));
    throw new Error(error.detail || "Erro ao atualizar operação");
  }

  return response.json();
}

export async function deleteOperation(id: number): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_URL}/operations/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao deletar operação" }));
    throw new Error(error.detail || "Erro ao deletar operação");
  }

  return response.json();
}

// ========== INTERFACES DE RENDA FIXA ==========

export interface FixedIncomeAsset {
  id: number;
  asset_id: number;
  ticker: string;
  product_name: string;
  issuer: string;
  product_type: string;
  indexer: string;
  rate: number;
  maturity_date: string;
  custody_fee: number;
  issue_date: string;
  created_at: string;
  status: string;
  total_invested: number;
  total_redeemed: number;
  current_balance: number;
  operations_count: number;
}

export interface FixedIncomeAssetCreate {
  asset_id: number;
  issuer: string;
  product_type: string;
  indexer: string;
  rate: number;
  maturity_date: string;
  issue_date: string;
  custody_fee?: number;
}

export interface FixedIncomeOperation {
  id: number;
  asset_id: number;
  operation_type: "APLICACAO" | "RESGATE" | "VENCIMENTO";
  amount: number;
  net_amount: number | null;
  ir_amount: number;
  trade_date: string;
  created_at: string;
  status: string;
}

export interface FixedIncomeOperationCreate {
  asset_id: number;
  operation_type: "APLICACAO" | "RESGATE" | "VENCIMENTO";
  amount: number;
  trade_date: string;
  net_amount?: number | null;
  ir_amount?: number;
}

export interface FixedIncomeProjection {
  asset_id: number;
  ticker: string;
  product_type: string;
  indexer: string;
  rate_contracted: number;
  maturity_date: string;
  days_to_maturity: number;
  current_balance: number;
  gross_projection: number;
  gross_gain: number;
  ir_rate: number;
  ir_amount: number;
  custody_fee_amount: number;
  net_projection: number;
  net_gain: number;
  annual_rate_used: number;
}

// ========== FUNÇÕES DE RENDA FIXA ==========

export async function createFixedIncomeAsset(data: FixedIncomeAssetCreate): Promise<{ status: string; fixed_income_id: number }> {
  const response = await fetch(`${API_URL}/fixed-income/assets`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao criar ativo de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao criar ativo de Renda Fixa");
  }

  return response.json();
}

export async function listFixedIncomeAssets(): Promise<FixedIncomeAsset[]> {
  const response = await fetch(`${API_URL}/fixed-income/assets`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao listar ativos de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao listar ativos de Renda Fixa");
  }

  return response.json();
}

export async function getFixedIncomeAsset(assetId: number): Promise<FixedIncomeAsset> {
  const response = await fetch(`${API_URL}/fixed-income/assets/${assetId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao buscar ativo de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao buscar ativo de Renda Fixa");
  }

  return response.json();
}

export async function updateFixedIncomeAsset(assetId: number, data: FixedIncomeAssetCreate): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_URL}/fixed-income/assets/${assetId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao atualizar ativo de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao atualizar ativo de Renda Fixa");
  }

  return response.json();
}

export async function deleteFixedIncomeAsset(assetId: number): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_URL}/fixed-income/assets/${assetId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao deletar ativo de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao deletar ativo de Renda Fixa");
  }

  return response.json();
}

export async function createFixedIncomeOperation(data: FixedIncomeOperationCreate): Promise<{ status: string; operation_id: number }> {
  const response = await fetch(`${API_URL}/fixed-income/operations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao criar operação de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao criar operação de Renda Fixa");
  }

  return response.json();
}

export async function listFixedIncomeOperations(assetId: number): Promise<FixedIncomeOperation[]> {
  const response = await fetch(`${API_URL}/fixed-income/operations/${assetId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao listar operações de Renda Fixa" }));
    throw new Error(error.detail || "Erro ao listar operações de Renda Fixa");
  }

  return response.json();
}

export async function getFixedIncomeProjection(
  assetId: number,
  cdiRate: number = 13.75,
  ipcaRate: number = 4.5
): Promise<FixedIncomeProjection> {
  const response = await fetch(
    `${API_URL}/fixed-income/projection/${assetId}?cdi_rate=${cdiRate}&ipca_rate=${ipcaRate}`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao calcular projeção" }));
    throw new Error(error.detail || "Erro ao calcular projeção");
  }

  return response.json();
}

// ========== INTERFACES DE COTAÇÕES ==========

export interface Quote {
  ticker: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  updated_at: string;
  source: string;
}

export interface QuotesMap {
  [ticker: string]: Quote | null;
}

// ========== FUNÇÕES DE COTAÇÕES ==========

export async function getQuote(ticker: string): Promise<Quote> {
  const response = await fetch(`${API_URL}/quotes/${ticker}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `Cotação não encontrada para ${ticker}` }));
    throw new Error(error.detail || `Cotação não encontrada para ${ticker}`);
  }

  return response.json();
}

export async function getBatchQuotes(tickers: string[]): Promise<QuotesMap> {
  const response = await fetch(`${API_URL}/quotes/batch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(tickers),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao buscar cotações" }));
    throw new Error(error.detail || "Erro ao buscar cotações");
  }

  return response.json();
}

export async function getPortfolioQuotes(): Promise<QuotesMap> {
  const response = await fetch(`${API_URL}/quotes/portfolio/current`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao buscar cotações do portfólio" }));
    throw new Error(error.detail || "Erro ao buscar cotações do portfólio");
  }

  return response.json();
}

export async function clearQuoteCache(ticker?: string): Promise<{ status: string; message: string }> {
  const url = ticker ? `${API_URL}/quotes/cache/${ticker}` : `${API_URL}/quotes/cache`;
  
  const response = await fetch(url, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erro ao limpar cache" }));
    throw new Error(error.detail || "Erro ao limpar cache");
  }

  return response.json();
}

