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

        <NavLink to="/analysis" className="nav-item">
          Análises
        </NavLink>

        <NavLink to="/settings" className="nav-item">
          Configurações
        </NavLink>
      </nav>
    </aside>
  );
}
