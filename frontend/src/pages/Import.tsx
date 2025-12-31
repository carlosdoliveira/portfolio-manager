import { ImportB3Card } from "../components/ImportB3Card";

export default function Import() {
  return (
    <div>
      <h1>Importar Dados</h1>
      <p>
        Envie o relatório de movimentações da B3 para atualizar sua carteira.
      </p>

      <ImportB3Card />
    </div>
  );
}
