export type AnalysisStatus = "success" | "running" | "draft";

export interface Analysis {
  id: string;
  name: string;
  description: string;
  updatedAt: string;
  status: AnalysisStatus;
  operationsCount: number;
}

export const initialAnalyses: Analysis[] = [
  {
    id: "analysis-001",
    name: "Sales Performance",
    description: "Análise de vendas por região e período",
    updatedAt: "Há 10 minutos",
    status: "success",
    operationsCount: 5,
  },
  {
    id: "analysis-002",
    name: "Customer Segmentation",
    description: "Segmentação de clientes por comportamento",
    updatedAt: "Há 2 horas",
    status: "draft",
    operationsCount: 3,
  },
  {
    id: "analysis-003",
    name: "Monthly Revenue",
    description: "Consolidação mensal de receitas",
    updatedAt: "Ontem",
    status: "success",
    operationsCount: 7,
  },
];