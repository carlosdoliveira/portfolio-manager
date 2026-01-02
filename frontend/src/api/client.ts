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
