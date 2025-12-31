// frontend/src/components/layout/Layout.tsx
import { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import "./layout.css";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="layout-root">
      <Header />

      <div className="layout-body">
        <Sidebar />
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
