# Oportunidades de Melhoria — Frontend

Este documento descreve as principais oportunidades de melhoria identificadas no frontend do Portfolio Manager v2.

---

## 🔴 Críticas (Funcionalidade e UX)

### 1. **URL da API está hardcoded**
**Localização:** `frontend/src/api/client.ts`

```typescript
const response = await fetch("http://localhost:8000/import/b3", {
```

**Problema:**  
Não funciona em produção ou ambientes diferentes. Quebra ao fazer deploy.

**Solução:**  
Usar variáveis de ambiente do Vite:

```typescript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadB3File(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/import/b3`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || "Erro ao importar arquivo");
  }

  return response.json();
}
```

Criar `.env` e `.env.example`:

```bash
# .env.example
VITE_API_URL=http://localhost:8000
```

---

### 2. **Falta de tratamento de erro detalhado**
**Localização:** `frontend/src/components/ImportB3Card.tsx`

```typescript
} catch {
  setState("error");  // ❌ Erro genérico sem detalhes
}
```

**Problema:**  
Usuário não sabe o que causou o erro (arquivo inválido, servidor fora do ar, formato incorreto).

**Solução:**  

```typescript
const [errorMessage, setErrorMessage] = useState<string | null>(null);

try {
  const result = await uploadB3File(file);
  setSummary(result.summary);
  setState("success");
} catch (error) {
  setState("error");
  setErrorMessage(
    error instanceof Error 
      ? error.message 
      : "Erro desconhecido ao importar arquivo"
  );
}

// No JSX:
{state === "error" && (
  <div className="import-status error">
    <strong>Erro ao importar:</strong> {errorMessage}
  </div>
)}
```

---

### 3. **Páginas críticas estão vazias (Dashboard, Portfolio, Analysis)**
**Localização:** `frontend/src/pages/Dashboard.tsx`, `Portfolio.tsx`, `Analysis.tsx`

**Problema:**  
Usuário não consegue visualizar dados importados. A aplicação está incompleta.

**Solução:**  
Implementar ao menos visualizações básicas:

**Dashboard:**
- Total investido
- Número de ativos
- Última importação

**Portfolio:**
- Lista de operações (tabela)
- Filtros por ticker e data

**Analysis:**
- Gráfico de distribuição por ativo
- Performance acumulada (se houver vendas)

---

### 4. **Ausência de loading state global**
**Problema:**  
Durante upload de arquivo grande, a UI não indica progresso.

**Solução:**  
Adicionar indicador de progresso:

```typescript
const [uploadProgress, setUploadProgress] = useState(0);

async function handleImport() {
  if (!file) return;

  setState("uploading");
  
  // Usar XMLHttpRequest para capturar progresso
  const xhr = new XMLHttpRequest();
  
  xhr.upload.addEventListener("progress", (e) => {
    if (e.lengthComputable) {
      setUploadProgress((e.loaded / e.total) * 100);
    }
  });
  
  // ... resto da lógica
}
```

---

## 🟠 Importantes (Manutenibilidade e Qualidade)

### 5. **Falta de gerenciamento de estado global**
**Problema:**  
Não há contexto ou store para compartilhar dados entre páginas (ex: operações carregadas, configurações de usuário).

**Solução:**  
Usar Context API ou Zustand:

```typescript
// src/store/useOperationsStore.ts
import { create } from 'zustand';

interface Operation {
  id: number;
  ticker: string;
  movement_type: string;
  quantity: number;
  price: number;
  trade_date: string;
  // ...
}

interface OperationsStore {
  operations: Operation[];
  isLoading: boolean;
  fetchOperations: () => Promise<void>;
}

export const useOperationsStore = create<OperationsStore>((set) => ({
  operations: [],
  isLoading: false,
  fetchOperations: async () => {
    set({ isLoading: true });
    const response = await fetch(`${API_URL}/operations`);
    const data = await response.json();
    set({ operations: data, isLoading: false });
  },
}));
```

---

### 6. **Ausência de tratamento de tipos nas respostas da API**
**Localização:** `frontend/src/api/client.ts`, `ImportB3Card.tsx`

**Problema:**  
TypeScript não valida o formato das respostas do backend.

**Solução:**  
Criar interfaces e validar com Zod:

```typescript
import { z } from 'zod';

const ImportSummarySchema = z.object({
  total_rows: z.number(),
  inserted: z.number(),
  duplicated: z.number(),
  unique_assets: z.number(),
  imported_at: z.string(),
});

type ImportSummary = z.infer<typeof ImportSummarySchema>;

export async function uploadB3File(file: File): Promise<ImportSummary> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/import/b3`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Erro ao importar arquivo");
  }

  const data = await response.json();
  return ImportSummarySchema.parse(data); // Valida estrutura
}
```

---

### 7. **Falta de testes (unitários e E2E)**
**Problema:**  
Nenhum teste foi implementado. Mudanças podem quebrar funcionalidades sem perceber.

**Solução:**  
Adicionar Vitest + Testing Library:

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

```typescript
// src/components/ImportB3Card.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ImportB3Card } from './ImportB3Card';

test('exibe mensagem inicial', () => {
  render(<ImportB3Card />);
  expect(screen.getByText(/Importar relatório da B3/i)).toBeInTheDocument();
});

test('permite arrastar arquivo', () => {
  render(<ImportB3Card />);
  const dropzone = screen.getByText(/Arraste o arquivo/i).closest('div');
  
  fireEvent.drop(dropzone!, {
    dataTransfer: { files: [new File([], 'test.xlsx')] },
  });
  
  expect(screen.getByText(/test.xlsx/i)).toBeInTheDocument();
});
```

---

### 8. **Falta de validação no cliente antes de enviar arquivo**
**Localização:** `frontend/src/components/DragAndDropArea.tsx`

**Problema:**  
Aceita arquivos `.csv` mas o backend só processa `.xlsx`. Causa erro tarde demais.

**Solução:**  

```typescript
function handleFiles(files: FileList | null) {
  if (!files || files.length === 0) return;
  
  const file = files[0];
  const validExtensions = ['.xlsx', '.xls'];
  const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
  
  if (!validExtensions.includes(extension)) {
    alert('Formato inválido. Envie um arquivo .xlsx');
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) { // 10MB
    alert('Arquivo muito grande. Limite: 10MB');
    return;
  }
  
  onFileSelected(file);
}
```

---

### 9. **CSS não está modular**
**Problema:**  
Estilos globais podem causar conflitos. Manutenção difícil em projetos maiores.

**Solução:**  
Usar CSS Modules ou Styled Components:

```typescript
// ImportB3Card.module.css
.container {
  max-width: 520px;
}

.card {
  border: 1px solid var(--color-border);
  /* ... */
}

// ImportB3Card.tsx
import styles from './ImportB3Card.module.css';

export function ImportB3Card() {
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* ... */}
      </div>
    </div>
  );
}
```

---

### 10. **Falta de acessibilidade (a11y)**
**Problemas identificados:**
- Botões sem `aria-label`
- Dropzone sem instruções para screen readers
- Falta de foco visível em elementos interativos

**Solução:**  

```typescript
<div
  role="button"
  tabIndex={0}
  aria-label="Área para upload de arquivo. Clique ou arraste um arquivo .xlsx"
  className={`dropzone ${isDragging ? "dragging" : ""}`}
  onClick={() => inputRef.current?.click()}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      inputRef.current?.click();
    }
  }}
  // ...
>
```

---

### 11. **Sidebar não indica rota ativa corretamente em mobile**
**Problema:**  
Layout não é responsivo. Sidebar ocupa espaço fixo.

**Solução:**  
Adicionar breakpoints e menu hamburguer:

```css
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -220px;
    transition: left 0.3s ease;
    z-index: 100;
  }

  .sidebar.open {
    left: 0;
  }
}
```

---

## 🟡 Boas Práticas (Nice to Have)

### 12. **Adicionar React Query para cache de requisições**
**Objetivo:**  
Evitar requisições duplicadas e melhorar performance.

**Solução:**  

```typescript
import { useQuery } from '@tanstack/react-query';

export function Portfolio() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['operations'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/operations`);
      return response.json();
    },
  });

  if (isLoading) return <p>Carregando...</p>;
  if (error) return <p>Erro ao carregar operações</p>;

  return (
    <div>
      <h1>Carteira</h1>
      {/* Renderizar operações */}
    </div>
  );
}
```

---

### 13. **Criar componente de tabela reutilizável**
**Objetivo:**  
Evitar duplicação ao listar operações em múltiplas páginas.

**Solução:**  

```typescript
interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
}

export function Table<T>({ data, columns }: TableProps<T>) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          {columns.map((col, i) => (
            <th key={i}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            {columns.map((col, j) => (
              <td key={j}>
                {typeof col.accessor === 'function'
                  ? col.accessor(row)
                  : String(row[col.accessor])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

### 14. **Adicionar modo escuro (dark mode)**
**Objetivo:**  
Melhorar UX para usuários que preferem temas escuros.

**Solução:**  

```typescript
// Adicionar tokens de tema escuro
:root[data-theme="dark"] {
  --color-bg-main: #0f172a;
  --color-bg-surface: #1e293b;
  --color-text-primary: #f1f5f9;
  --color-text-secondary: #cbd5e1;
  --color-border: #334155;
}

// Toggle no Header
export function Header() {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <header className="header">
      <strong>Portfolio Manager</strong>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
    </header>
  );
}
```

---

### 15. **Implementar toast notifications**
**Objetivo:**  
Feedback visual não-intrusivo para ações (importação bem-sucedida, erros).

**Solução:**  
Usar `react-hot-toast`:

```typescript
import toast, { Toaster } from 'react-hot-toast';

// No App.tsx
<Toaster position="top-right" />

// Nos componentes
async function handleImport() {
  try {
    const result = await uploadB3File(file);
    toast.success(`${result.summary.inserted} operações importadas!`);
  } catch (error) {
    toast.error('Erro ao importar arquivo');
  }
}
```

---

### 16. **Adicionar lazy loading para rotas**
**Objetivo:**  
Reduzir tamanho do bundle inicial.

**Solução:**  

```typescript
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Import = lazy(() => import('./pages/Import'));
const Portfolio = lazy(() => import('./pages/Portfolio'));

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<div>Carregando...</div>}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/import" element={<Import />} />
            <Route path="/portfolio" element={<Portfolio />} />
            {/* ... */}
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  );
}
```

---

### 17. **Adicionar ESLint e Prettier**
**Problema:**  
Código pode ter estilos inconsistentes.

**Solução:**  

```bash
npm install -D eslint @typescript-eslint/eslint-plugin prettier eslint-config-prettier
```

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "warn",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

---

### 18. **Dockerização melhorada**
**Problema:**  
Dockerfile do frontend executa `npm run build` mas depois roda `npm run dev`, que é inconsistente.

**Solução (Produção):**  

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Solução (Dev):**  

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

---

### 19. **Adicionar PWA (Progressive Web App)**
**Objetivo:**  
Permitir instalação como app nativo, funcionar offline.

**Solução:**  
Usar Vite PWA plugin:

```bash
npm install -D vite-plugin-pwa
```

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Portfolio Manager',
        short_name: 'Portfolio',
        theme_color: '#6366f1',
        icons: [
          {
            src: '/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
});
```

---

## 📋 Checklist de Prioridades

**Fazer primeiro:**
- [ ] Mover URL da API para variável de ambiente (item 1)
- [ ] Implementar tratamento de erro detalhado (item 2)
- [ ] Implementar Dashboard com dados reais (item 3)
- [ ] Adicionar validação de arquivo (item 8)

**Fazer em seguida:**
- [ ] Adicionar gerenciamento de estado (item 5)
- [ ] Criar tipos e validação de API (item 6)
- [ ] Implementar Portfolio (lista de operações) (item 3)
- [ ] Tornar layout responsivo (item 11)

**Nice to have:**
- [ ] Adicionar React Query (item 12)
- [ ] Implementar dark mode (item 14)
- [ ] Adicionar toast notifications (item 15)
- [ ] Configurar ESLint/Prettier (item 17)
- [ ] Adicionar testes (item 7)

---

**Total de melhorias identificadas:** 19  
**Estimativa de esforço:** 3-4 sprints (assumindo 1 sprint = 2 semanas)
