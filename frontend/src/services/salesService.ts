/**
 * Serviço de Vendas Frontend
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8004/api/v1/sales';

export interface Cliente {
  id?: number;
  cust_id?: string;
  nickname: string;
  nome_principal?: string;
  status: string;
  tempo_ativo?: number;
  data_inicio?: string;
  jornada_iniciada?: string;
  ltv_meses?: number;
  ltv_valor?: number;
  observacoes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface MetricasVendas {
  total_clientes: number;
  clientes_ativos: number;
  clientes_novos_mes: number;
  clientes_churn_mes: number;
  receita_recorrente: number;
  ltv_medio: number;
  ticket_medio: number;
  taxa_churn: number;
}

export interface ImportResult {
  success: boolean;
  total_rows: number;
  success_rows: number;
  error_rows: number;
  errors: string[];
  import_id?: number;
}

class SalesService {
  // Clientes
  async listarClientes(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    search?: string;
  }): Promise<Cliente[]> {
    const response = await axios.get('/clientes', { 
      baseURL: API_BASE_URL,
      params 
    });
    return response.data;
  }

  async obterCliente(clienteId: number): Promise<Cliente> {
    const response = await axios.get(`/clientes/${clienteId}`, {
      baseURL: API_BASE_URL
    });
    return response.data;
  }

  async criarCliente(cliente: Omit<Cliente, 'id' | 'created_at' | 'updated_at'>): Promise<Cliente> {
    const response = await axios.post('/clientes', cliente, {
      baseURL: API_BASE_URL
    });
    return response.data;
  }

  async atualizarCliente(clienteId: number, cliente: Partial<Cliente>): Promise<Cliente> {
    const response = await axios.put(`/clientes/${clienteId}`, cliente, {
      baseURL: API_BASE_URL
    });
    return response.data;
  }

  async deletarCliente(clienteId: number): Promise<{ message: string }> {
    const response = await axios.delete(`/clientes/${clienteId}`, {
      baseURL: API_BASE_URL
    });
    return response.data;
  }

  // Métricas
  async obterMetricas(periodo?: string): Promise<MetricasVendas> {
    const response = await axios.get('/metricas', {
      baseURL: API_BASE_URL,
      params: { periodo }
    });
    return response.data;
  }

  // Importação/Exportação
  async importarPlanilha(arquivo: File): Promise<ImportResult> {
    const formData = new FormData();
    formData.append('file', arquivo);

    const response = await axios.post('/import', formData, {
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async exportarPlanilha(filtros?: {
    status?: string;
    data_inicio?: string;
    data_final?: string;
  }): Promise<Blob> {
    const response = await axios.get('/export', {
      baseURL: API_BASE_URL,
      params: filtros,
      responseType: 'blob',
    });
    return response.data;
  }

  async listarLogsImportacao(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const response = await axios.get('/import-logs', {
      baseURL: API_BASE_URL,
      params
    });
    return response.data;
  }

  // Utilitários
  formatarMoeda(valor: number): string {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  }

  formatarData(data: string): string {
    return new Date(data).toLocaleDateString('pt-BR');
  }

  obterStatusColor(status: string): string {
    const colors: { [key: string]: string } = {
      'Ativo ML': 'green',
      'Ativo': 'green',
      'Churn': 'red',
      'Pausado': 'orange',
      'Não é MAIS cliente': 'red',
      'Novo Cliente': 'blue'
    };
    return colors[status] || 'default';
  }

  downloadArquivo(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);
  }
}

export const salesService = new SalesService();