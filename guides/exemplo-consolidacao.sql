-- Exemplo de Consolidação de Mercados
-- Este script demonstra como operações em mercado à vista e fracionário são consolidadas

-- 1. Inserir ativo de exemplo
INSERT INTO assets (ticker, asset_class, asset_type, product_name, created_at, status)
VALUES ('PETR4', 'AÇÕES', 'PN', 'PETROBRAS PN', datetime('now'), 'ACTIVE');

-- 2. Simular operações em diferentes mercados
-- Compra no mercado à vista
INSERT INTO operations (
    asset_id,
    trade_date,
    movement_type,
    market,
    institution,
    quantity,
    price,
    value,
    created_at,
    source,
    status
) VALUES (
    (SELECT id FROM assets WHERE ticker = 'PETR4'),
    '2026-01-01',
    'COMPRA',
    'MERCADO A VISTA',
    'XP INVESTIMENTOS',
    100,
    30.00,
    3000.00,
    datetime('now'),
    'B3',
    'ACTIVE'
);

-- Compra no mercado fracionário
INSERT INTO operations (
    asset_id,
    trade_date,
    movement_type,
    market,
    institution,
    quantity,
    price,
    value,
    created_at,
    source,
    status
) VALUES (
    (SELECT id FROM assets WHERE ticker = 'PETR4'),
    '2026-01-05',
    'COMPRA',
    'MERCADO FRACIONARIO',
    'XP INVESTIMENTOS',
    5,
    31.00,
    155.00,
    datetime('now'),
    'MANUAL',
    'ACTIVE'
);

-- 3. Consultar posição consolidada (como o sistema faz)
SELECT 
    a.ticker,
    a.asset_class,
    a.asset_type,
    -- Total comprado (TODOS os mercados)
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) as total_bought,
    -- Total vendido (TODOS os mercados)
    SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END) as total_sold,
    -- Posição atual CONSOLIDADA
    (SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END) - 
     SUM(CASE WHEN o.movement_type = 'VENDA' THEN o.quantity ELSE 0 END)) as current_position,
    -- Valor total investido (CONSOLIDADO)
    SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) as total_invested,
    -- Preço médio (valor investido / quantidade comprada)
    ROUND(SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.value ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN o.movement_type = 'COMPRA' THEN o.quantity ELSE 0 END), 0), 2) as average_price
FROM assets a
LEFT JOIN operations o ON a.id = o.asset_id AND o.status = 'ACTIVE'
WHERE a.ticker = 'PETR4' AND a.status = 'ACTIVE'
GROUP BY a.id;

-- Resultado esperado:
-- ticker | asset_class | asset_type | total_bought | total_sold | current_position | total_invested | average_price
-- PETR4  | AÇÕES      | PN         | 105          | 0          | 105              | 3155.00        | 30.05

-- 4. Consultar detalhamento por mercado (para visualização)
SELECT 
    o.market,
    o.movement_type,
    COUNT(*) as num_operations,
    SUM(o.quantity) as total_quantity,
    SUM(o.value) as total_value,
    ROUND(AVG(o.price), 2) as avg_price
FROM operations o
INNER JOIN assets a ON o.asset_id = a.id
WHERE a.ticker = 'PETR4' AND o.status = 'ACTIVE'
GROUP BY o.market, o.movement_type
ORDER BY o.market, o.movement_type;

-- Resultado esperado:
-- market              | movement_type | num_operations | total_quantity | total_value | avg_price
-- MERCADO A VISTA     | COMPRA       | 1              | 100            | 3000.00     | 30.00
-- MERCADO FRACIONARIO | COMPRA       | 1              | 5              | 155.00      | 31.00

-- 5. Limpar dados de teste (opcional)
-- DELETE FROM operations WHERE asset_id = (SELECT id FROM assets WHERE ticker = 'PETR4');
-- DELETE FROM assets WHERE ticker = 'PETR4';
