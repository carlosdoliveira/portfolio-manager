import { NavLink } from "react-router-dom";

export function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <NavLink to="/" end className="nav-item">
          Dashboard
        </NavLink>

        <NavLink to="/import" className="nav-item">
          Importar Dados
        </NavLink>

        <NavLink to="/portfolio" className="nav-item">
          Carteira
        </NavLink>

        <NavLink to="/fixed-income" className="nav-item">
          Renda Fixa
        </NavLink>

        <NavLink to="/analysis" className="nav-item">
          Análises
        </NavLink>

        <div className="nav-divider"></div>

        <NavLink to="/admin/reconciliation" className="nav-item">
          🔍 Reconciliação
        </NavLink>

        <NavLink to="/settings" className="nav-item">
          Configurações
        </NavLink>
      </nav>
    </aside>
  );
}
