import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { fetchDashboardSummary, DashboardSummary } from "../api/client";
import "./Dashboard.css";

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchDashboardSummary();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar dashboard");
    } finally {
      setLoading(false);
    }
  }

  function formatCurrency(value: number): string {
    return value.toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR");
  }

  if (loading) {
    return (
      <div className="dashboard dashboard--loading">
        <p>Carregando dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard__error">
          <strong>Erro:</strong> {error}
        </div>
        <button onClick={loadDashboard}>Tentar novamente</button>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="dashboard">
        <p>Nenhum dado disponível</p>
      </div>
    );
  }

  // Cores para alocação de ativos
  const allocationColors = [
    "#4A90E2", // Azul
    "#50E3C2", // Verde água
    "#F5A623", // Laranja
    "#BD10E0", // Roxo
    "#7ED321", // Verde
  ];

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <h1 className="dashboard__title">Dashboard</h1>
        <p className="dashboard__subtitle">Visão geral da sua carteira de investimentos</p>
      </div>

      {/* Cards de Estatísticas */}
      <div className="dashboard__stats">
        <div className="stat-card">
          <div className="stat-card__label">Total de Ativos</div>
          <div className="stat-card__value">{summary.total_assets}</div>
          <div className="stat-card__sublabel">com posição ativa</div>
        </div>

        <div className="stat-card">
          <div className="stat-card__label">Total Investido</div>
          <div className="stat-card__value stat-card__value--currency">
            {formatCurrency(summary.total_invested)}
          </div>
          <div className="stat-card__sublabel">Compras - Vendas</div>
        </div>

        <div className="stat-card">
          <div className="stat-card__label">Valor Atual</div>
          <div className="stat-card__value stat-card__value--currency">
            {formatCurrency(summary.current_value)}
          </div>
          <div className="stat-card__sublabel">Com cotações atuais</div>
        </div>

        <div className="stat-card">
          <div className="stat-card__label">Lucro/Prejuízo</div>
          <div className={`stat-card__value ${
            summary.daily_change_percent > 0 
              ? "stat-card__value--positive" 
              : "stat-card__value--negative"
          }`}>
            {summary.daily_change_percent > 0 ? "+" : ""}
            {summary.daily_change_percent.toFixed(2)}%
          </div>
          <div className={`stat-card__change ${
            summary.daily_change > 0 
              ? "stat-card__change--positive" 
              : "stat-card__change--negative"
          }`}>
            {summary.daily_change >= 0 ? "▲" : "▼"} R$ {formatCurrency(Math.abs(summary.daily_change))}
          </div>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="dashboard__content">
        {/* Top Posições */}
        <div className="section-card">
          <div className="section-card__header">
            <h2 className="section-card__title">Top 5 Posições</h2>
            <a 
              className="section-card__action" 
              onClick={() => navigate("/portfolio")}
            >
              Ver todas →
            </a>
          </div>

          {summary.top_positions.length === 0 ? (
            <p style={{ color: "var(--text-secondary)", textAlign: "center", padding: "2rem 0" }}>
              Nenhuma posição ativa
            </p>
          ) : (
            <table className="positions-table">
              <thead>
                <tr>
                  <th>Ativo</th>
                  <th style={{ textAlign: "right" }}>Quantidade</th>
                  <th style={{ textAlign: "right" }}>Preço Médio</th>
                  <th style={{ textAlign: "right" }}>Valor Investido</th>
                </tr>
              </thead>
              <tbody>
                {summary.top_positions.map((position) => (
                  <tr 
                    key={position.id}
                    onClick={() => navigate(`/portfolio/${position.id}`)}
                    style={{ cursor: "pointer" }}
                  >
                    <td>
                      <div className="positions-table__ticker">{position.ticker}</div>
                      <div className="positions-table__name">{position.product_name}</div>
                    </td>
                    <td className="positions-table__value">{position.quantity}</td>
                    <td className="positions-table__value">
                      R$ {formatCurrency(position.average_price)}
                    </td>
                    <td className="positions-table__value">
                      R$ {formatCurrency(position.invested_value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Alocação */}
        <div className="section-card">
          <div className="section-card__header">
            <h2 className="section-card__title">Alocação</h2>
          </div>

          {summary.asset_allocation.length === 0 ? (
            <p style={{ color: "var(--text-secondary)", textAlign: "center", padding: "2rem 0" }}>
              Sem dados de alocação
            </p>
          ) : (
            <div className="allocation-container">
              {/* Gráfico de Pizza */}
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={summary.asset_allocation.map((allocation, index) => ({
                      name: allocation.asset_class,
                      value: allocation.value,
                      percentage: allocation.percentage
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ percentage }) => `${percentage.toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {summary.asset_allocation.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={allocationColors[index % allocationColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                  />
                </PieChart>
              </ResponsiveContainer>

              {/* Legenda */}
              <div className="allocation-legend">
                {summary.asset_allocation.map((allocation, index) => (
                  <div key={allocation.asset_class} className="allocation-item">
                    <div 
                      className="allocation-item__color"
                      style={{ backgroundColor: allocationColors[index % allocationColors.length] }}
                    />
                    <div className="allocation-item__label">{allocation.asset_class}</div>
                    <div className="allocation-item__value">
                      R$ {formatCurrency(allocation.value)}
                    </div>
                    <div className="allocation-item__percentage">{allocation.percentage.toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Operações Recentes */}
      <div className="section-card">
        <div className="section-card__header">
          <h2 className="section-card__title">Operações Recentes</h2>
          <a 
            className="section-card__action" 
            onClick={() => navigate("/portfolio")}
          >
            Ver todas →
          </a>
        </div>

        {summary.recent_operations.length === 0 ? (
          <p style={{ color: "var(--text-secondary)", textAlign: "center", padding: "2rem 0" }}>
            Nenhuma operação registrada
          </p>
        ) : (
          <div className="operations-list">
            {summary.recent_operations.map((operation) => (
              <div key={operation.id} className="operation-item">
                <div className="operation-item__main">
                  <div className="operation-item__ticker">
                    {operation.ticker}
                    <span className={`operation-item__badge operation-item__badge--${
                      operation.movement_type.toUpperCase() === "COMPRA" ? "buy" : "sell"
                    }`}>
                      {operation.movement_type}
                    </span>
                  </div>
                  <div className="operation-item__details">
                    {operation.quantity} un × R$ {formatCurrency(operation.price)}
                    {operation.market && ` • ${operation.market}`}
                  </div>
                </div>
                <div className="operation-item__value">
                  <div>R$ {formatCurrency(operation.value)}</div>
                  <div className="operation-item__date">{formatDate(operation.trade_date)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

