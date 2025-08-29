import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Table, 
  Button, 
  DatePicker, 
  Select, 
  Space,
  Tag,
  Progress,
  List,
  Avatar,
  Typography,
  Divider,
  Alert
} from 'antd';
import { 
  DollarCircleOutlined, 
  ShoppingCartOutlined, 
  TrophyOutlined,
  RiseOutlined,
  TeamOutlined,
  CalendarOutlined,
  FileTextOutlined,
  StarOutlined
} from '@ant-design/icons';
import { Line, Column, Pie } from '@ant-design/plots';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

interface VendaMetrica {
  periodo: {
    data_inicio: string | null;
    data_fim: string | null;
  };
  total_vendas: number;
  valor_total: number;
  media_valor: number;
  top_produtos: [string, any][];
  top_vendedores: [string, any][];
}

interface VendaItem {
  id: number;
  data: string;
  loja: string;
  produto: string;
  valor_mensal: number;
  vendedor: {
    nome: string;
  };
  cliente: {
    nome_principal: string;
  };
  forma_pagamento: string;
  canal_venda: string;
}

const DashboardVendas: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [metricas, setMetricas] = useState<VendaMetrica | null>(null);
  const [vendas, setVendas] = useState<VendaItem[]>([]);
  const [filtros, setFiltros] = useState({
    dataInicio: null as any,
    dataFim: null as any,
    vendedor: null as string | null,
  });

  // Dados mockados para demonstração
  const mockMetricas: VendaMetrica = {
    periodo: { data_inicio: null, data_fim: null },
    total_vendas: 10,
    valor_total: 29950.00,
    media_valor: 2995.00,
    top_produtos: [
      ["ASSESSORIA MASTER", { quantidade: 4, valor_total: 11400.00 }],
      ["ASSESSORIA FULL FUNNEL", { quantidade: 1, valor_total: 5000.00 }],
      ["ASSESSORIA START", { quantidade: 1, valor_total: 3800.00 }],
      ["ASSESSORIA PERFORMANCE", { quantidade: 1, valor_total: 3000.00 }],
      ["MENTORIA EDUCATIVA", { quantidade: 1, valor_total: 1750.00 }]
    ],
    top_vendedores: [
      ["1", { quantidade: 7, valor_total: 22150.00 }],
      ["2", { quantidade: 1, valor_total: 5000.00 }],
      ["3", { quantidade: 1, valor_total: 3000.00 }]
    ]
  };

  const mockVendas: VendaItem[] = [
    {
      id: 1,
      data: "2025-06-01",
      loja: "BMP SHOP",
      produto: "ASSESSORIA MASTER",
      valor_mensal: 2600.00,
      vendedor: { nome: "Isaac" },
      cliente: { nome_principal: "DENNIS" },
      forma_pagamento: "BOLETO",
      canal_venda: "Tráfego"
    },
    {
      id: 2,
      data: "2025-06-17",
      loja: "USEE BRASIL",
      produto: "ASSESSORIA FULL FUNNEL",
      valor_mensal: 5000.00,
      vendedor: { nome: "Lucas" },
      cliente: { nome_principal: "Gabriel Morais" },
      forma_pagamento: "BOLETO",
      canal_venda: "Orgânico"
    }
  ];

  useEffect(() => {
    carregarDados();
  }, [filtros]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      // Em produção, aqui faria as chamadas reais para a API
      // const response = await api.get('/api/v1/vendas/metricas/gerais', { params: filtros });
      
      // Por enquanto, usar dados mockados
      setTimeout(() => {
        setMetricas(mockMetricas);
        setVendas(mockVendas);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setLoading(false);
    }
  };

  const handleFiltroChange = (key: string, value: any) => {
    setFiltros(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const colunas: ColumnsType<VendaItem> = [
    {
      title: 'Data',
      dataIndex: 'data',
      key: 'data',
      render: (date) => new Date(date).toLocaleDateString('pt-BR'),
      sorter: (a, b) => new Date(a.data).getTime() - new Date(b.data).getTime(),
    },
    {
      title: 'Loja',
      dataIndex: 'loja',
      key: 'loja',
    },
    {
      title: 'Produto',
      dataIndex: 'produto',
      key: 'produto',
    },
    {
      title: 'Cliente',
      dataIndex: ['cliente', 'nome_principal'],
      key: 'cliente',
    },
    {
      title: 'Vendedor',
      dataIndex: ['vendedor', 'nome'],
      key: 'vendedor',
    },
    {
      title: 'Valor Mensal',
      dataIndex: 'valor_mensal',
      key: 'valor_mensal',
      render: (value) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
      sorter: (a, b) => a.valor_mensal - b.valor_mensal,
    },
    {
      title: 'Canal',
      dataIndex: 'canal_venda',
      key: 'canal_venda',
      render: (canal) => (
        <Tag color={
          canal === 'Orgânico' ? 'green' :
          canal === 'Tráfego' ? 'blue' :
          canal === 'Parceiro In' ? 'gold' :
          canal === 'Parceiro Out' ? 'purple' :
          'default'
        }>
          {canal}
        </Tag>
      ),
    },
    {
      title: 'Pagamento',
      dataIndex: 'forma_pagamento',
      key: 'forma_pagamento',
      render: (pagamento) => (
        <Tag color={
          pagamento === 'BOLETO' ? 'orange' :
          pagamento === 'PIX' ? 'green' :
          pagamento === 'CRÉDITO RECORRENTE' ? 'blue' :
          'default'
        }>
          {pagamento}
        </Tag>
      ),
    },
  ];

  const dadosGraficoTempo = [
    { mes: 'Jan', vendas: 8, valor: 24000 },
    { mes: 'Fev', vendas: 12, valor: 36000 },
    { mes: 'Mar', vendas: 15, valor: 45000 },
    { mes: 'Abr', vendas: 18, valor: 54000 },
    { mes: 'Mai', vendas: 22, valor: 66000 },
    { mes: 'Jun', vendas: 10, valor: 29950 },
  ];

  const configGraficoLinha = {
    data: dadosGraficoTempo,
    xField: 'mes',
    yField: 'valor',
    smooth: true,
    color: '#1890ff',
  };

  const dadosGraficoProdutos = metricas?.top_produtos.map(([produto, dados]) => ({
    produto: produto.substring(0, 20),
    valor: dados.valor_total,
    quantidade: dados.quantidade
  })) || [];

  const configGraficoProdutos = {
    data: dadosGraficoProdutos,
    xField: 'produto',
    yField: 'valor',
    color: '#52c41a',
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <TrophyOutlined /> Dashboard de Vendas
        </Title>
        <Text type="secondary">
          Acompanhe o desempenho das vendas em tempo real
        </Text>
      </div>

      {/* Filtros */}
      <Card style={{ marginBottom: '24px' }}>
        <Space wrap>
          <RangePicker
            placeholder={['Data início', 'Data fim']}
            format="DD/MM/YYYY"
            onChange={(dates) => {
              handleFiltroChange('dataInicio', dates?.[0]?.format('YYYY-MM-DD') || null);
              handleFiltroChange('dataFim', dates?.[1]?.format('YYYY-MM-DD') || null);
            }}
          />
          <Select
            placeholder="Vendedor"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => handleFiltroChange('vendedor', value)}
          >
            <Option value="1">Isaac</Option>
            <Option value="2">Lucas</Option>
            <Option value="3">Keysi</Option>
            <Option value="4">Rogério</Option>
          </Select>
          <Button type="primary" onClick={carregarDados} loading={loading}>
            Aplicar Filtros
          </Button>
        </Space>
      </Card>

      {/* Cards de Métricas */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total de Vendas"
              value={metricas?.total_vendas || 0}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Valor Total"
              value={metricas?.valor_total || 0}
              prefix={<DollarCircleOutlined />}
              precision={2}
              formatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Ticket Médio"
              value={metricas?.media_valor || 0}
              prefix={<RiseOutlined />}
              precision={2}
              formatter={(value) => `R$ ${value.toLocaleString('pt-BR')}`}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Meta do Mês"
              value={75}
              suffix="/ 100%"
              prefix={<StarOutlined />}
            />
            <Progress 
              percent={75} 
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              style={{ marginTop: '12px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Gráficos */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Evolução das Vendas" loading={loading}>
            <Line {...configGraficoLinha} height={250} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Top Vendedores" loading={loading}>
            <List
              itemLayout="horizontal"
              dataSource={metricas?.top_vendedores.slice(0, 3) || []}
              renderItem={([vendedorId, dados], index) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar style={{ backgroundColor: ['#f56a00', '#7265e6', '#00a2ae'][index] }}>{index + 1}</Avatar>}
                    title={`Vendedor ${vendedorId === '1' ? 'Isaac' : vendedorId === '2' ? 'Lucas' : 'Keysi'}`}
                    description={`${dados.quantidade} vendas • R$ ${dados.valor_total.toLocaleString('pt-BR')}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Top Produtos por Valor" loading={loading}>
            <Column {...configGraficoProdutos} height={250} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Canais de Venda" loading={loading}>
            <List
              size="small"
              dataSource={[
                { canal: 'Orgânico', vendas: 3, cor: 'green' },
                { canal: 'Tráfego', vendas: 2, cor: 'blue' },
                { canal: 'Parceiro In', vendas: 2, cor: 'gold' },
                { canal: 'Parceiro Out', vendas: 2, cor: 'purple' },
                { canal: 'Outbound', vendas: 1, cor: 'red' }
              ]}
              renderItem={(item) => (
                <List.Item>
                  <Space>
                    <Tag color={item.cor}>{item.canal}</Tag>
                    <Text>{item.vendas} vendas</Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* Tabela de Vendas Recentes */}
      <Card title="Vendas Recentes" loading={loading}>
        <Table
          columns={colunas}
          dataSource={vendas}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} de ${total} vendas`
          }}
        />
      </Card>
    </div>
  );
};

export default DashboardVendas;