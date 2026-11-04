# DataFlow

DataFlow é uma plataforma para criação, gerenciamento e execução de análises baseadas em grafos de operações sobre datasets. O projeto combina um backend em Python com FastAPI, um frontend em React + Vite e uma arquitetura em packages para separar domínio, execução, analytics, storage e infraestrutura.

## Visão Geral

A solução foi pensada para permitir que usuários:

- criem e gerenciem análises no estilo workspace;
- autentiquem-se em um sistema com registro e login;
- definam pipelines de processamento em um grafo de operações;
- executem transforms sobre datasets com suporte a engine analítica em Polars;
- visualizem resultados em gráficos e artefatos renderizados.

O projeto está estruturado em múltiplos pacotes Python, o que facilita a separação entre regras de negócio, execução, persistência e infraestrutura.

## Tecnologias

- Python 3.15
- FastAPI para a API REST
- React 19 + Vite + TypeScript para a interface web
- Tailwind CSS para estilização
- Polars para processamento analítico
- Hyperway para representação e planejamento dos grafos de execução
- Plotly para renderização de gráficos
- JWT para autenticação
- Turso Serverless para armazenamento persistente
- uv como gerenciador de workspace e dependências

## Estrutura do Projeto

```text
.
├── apps/
│   ├── api/
│   │   └── dataflow_api/
│   │       ├── dependencies.py
│   │       ├── main.py
│   │       ├── routers/
│   │       ├── schemas/
│   │       ├── security/
│   │       └── services/
│   └── web/
│       ├── package.json
│       ├── vite.config.ts
│       └── src/
├── packages/
│   ├── analytics/
│   ├── domain/
│   ├── execution/
│   ├── infrastructure/
│   └── storage/
├── tests/
├── pyproject.toml
├── README.md
├── vendas.csv
└── docs/
```

## Pré-requisitos

- Python 3.15+
- Node.js 18+ e npm
- uv instalado no ambiente
- Acesso a um banco Turso configurado

## Instalação

Clone o repositório e configure o ambiente do workspace:

```bash
git clone <url-do-repositorio>
cd dataflow
uv sync --group dev --group api
```

Para o frontend, instale as dependências do app web:

```bash
cd apps/web
npm install
```

## Configuração

Crie um arquivo `.env` com as variáveis de ambiente necessárias para o backend. O projeto espera as seguintes variáveis:

```env
JWT_SECRET_KEY=uma-chave-secreta-com-pelo-menos-32-caracteres
TURSO_DATABASE_URL=https://<database>.turso.io
TURSO_AUTH_TOKEN=<token-do-banco>
DATAFLOW_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

O backend usa `python-dotenv` para carregar essas variáveis e o serviço de autenticação exige que `JWT_SECRET_KEY` tenha pelo menos 32 bytes.

## Executando a Aplicação

### Backend

```bash
cd apps/api
uv run uvicorn dataflow_api.main:app --reload --host 0.0.0.0 --port 8000
```

Se você preferir iniciar a partir da raiz do workspace, também pode usar:

```bash
cd /home/abdiel/Documentos/Projetos/Websites/dataflow
uv run --project apps/api uvicorn dataflow_api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd apps/web
npm run dev
```

A interface normalmente fica disponível em `http://localhost:5173`.

## Scripts Disponíveis

### Backend

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

### Frontend

```bash
cd apps/web
npm run dev
npm run build
npm run lint
npm test
npm run preview
```

## Funcionalidades

- autenticação de usuários com registro e login;
- criação e listagem de análises por usuário;
- grafo de operações para modelar fluxos de processamento;
- execução de pipelines sobre datasets;
- suporte a renderização de artefatos e gráficos;
- interface visual para workspace de análises;
- arquitetura modular por domínio, execução e armazenamento.

## Fluxo de Uso

1. o usuário se registra ou faz login;
2. acessa o painel de análises;
3. cria uma nova análise com nome e dataset;
4. adiciona operações no editor visual;
5. executa o pipeline para transformar os dados;
6. visualiza os resultados e artefatos gerados.

## Arquitetura

O projeto segue uma separação em camadas:

- camada de domínio: modelos e regras de negócio em `packages/domain`;
- camada de analytics: motores de processamento e renderização em `packages/analytics`;
- camada de execução: converte as operações do domínio em `hyperway.Graph` e `Unit`, planeja estágios pelas conexões Hyperway e executa operações em `packages/execution`;
- camada de armazenamento: integração com banco e repositórios em `packages/storage`;
- camada de infraestrutura: suporte de persistência e serviços de infraestrutura em `packages/infrastructure`;
- camada de API: endpoints em `apps/api/dataflow_api`;
- camada de interface: app em React em `apps/web/src`.

A API expõe rotas de autenticação e análises, enquanto o frontend consome esses endpoints para criar, listar e abrir workflows de análise. As definições continuam trafegando como operações e arestas para manter compatibilidade com análises persistidas; `dataflow_execution` converte essa definição em unidades e conexões Hyperway antes da execução. O modelo principal inclui `Analysis`, `Dataset`, `Operation` e artefatos renderizados.

## Contribuição

Contribuições são bem-vindas. Para colaborar:

1. faça um fork do projeto;
2. crie uma branch para sua feature ou correção;
3. implemente e teste as mudanças;
4. abra um pull request com descrição clara do problema e da solução.

## Licença

Este projeto está em desenvolvimento e o arquivo de licença não foi definido explicitamente no repositório até o momento. Recomendase revisar a política de distribuição antes de uso em produção ou publicação pública.

## Contato

- Projeto: DataFlow
- Repositório: este workspace local
- Stack principal: backend Python + frontend React
