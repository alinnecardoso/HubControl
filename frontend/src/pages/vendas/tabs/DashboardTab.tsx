import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  DatePicker,
  Select,
  Space,
  Typography,
  message,
  Table,
  Tag,
  Spin
} from 'antd';
import {
  DollarOutlined,
  ShoppingOutlined,
  TrophyOutlined,
  UserOutlined
} from '@ant-design/icons';
import { salesService } from '../../../services/salesService';

const { Title } = Typography;
const { MonthPicker } = DatePicker;
const { Option } = Select;

interface DashboardVendas {
  total_vendas: number;
  valor_total: number;
  media_valor: number;
  top_produtos: Array<{
    produto: string;
    quantidade: number;
    valor_total: number;
  }>;
  top_vendedores: Array<{
    vendedor_id: number;
    nome: string;
    quantidade: number;
    valor_total: number;
  }>;
}

const DashboardTab: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState<DashboardVendas | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<number>();
  const [selectedYear, setSelectedYear] = useState<number>();

  const loadDashboard = async (mes?: number, ano?: number) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (mes) params.append('mes', mes.toString());
      if (ano) params.append('ano', ano.toString());

      const response = await fetch(`http://localhost:8004/api/v1/sales/dashboard?${params}`);
      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      } else {
        message.error('Erro ao carregar dashboard');
      }
    } catch (error) {
      message.error('Erro ao carregar dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleMonthChange = (date: any) => {
    if (date) {
      const mes = date.month() + 1;
      const ano = date.year();
      setSelectedMonth(mes);
      setSelectedYear(ano);
      loadDashboard(mes, ano);
    } else {
      setSelectedMonth(undefined);
      setSelectedYear(undefined);
      loadDashboard();
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const produtosColumns = [
    {
      title: 'Produto',
      dataIndex: 'produto',
      key: 'produto',
      ellipsis: true,
    },
    {
      title: 'Quantidade',
      dataIndex: 'quantidade',
      key: 'quantidade',
      width: 100,
      align: 'center' as const,
      render: (value: number) => <Tag color="blue">{value}</Tag>
    },
    {
      title: 'Valor Total',
      dataIndex: 'valor_total',
      key: 'valor_total',
      width: 120,
      align: 'right' as const,
      render: (value: number) => formatCurrency(value)
    }
  ];

  const vendedoresColumns = [
    {
      title: 'Vendedor',
      dataIndex: 'nome',
      key: 'nome',
      ellipsis: true,
    },
    {
      title: 'Quantidade',
      dataIndex: 'quantidade',
      key: 'quantidade',
      width: 100,
      align: 'center' as const,
      render: (value: number) => <Tag color="green">{value}</Tag>
    },
    {
      title: 'Valor Total',
      dataIndex: 'valor_total',
      key: 'valor_total',
      width: 120,
      align: 'right' as const,
      render: (value: number) => formatCurrency(value)
    }
  ];

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Space>
            <MonthPicker
              placeholder="Filtrar por mês"
              onChange={handleMonthChange}
              allowClear
            />
          </Space>
        </Col>
      </Row>

      {dashboard && (
        <>
          {/* Métricas principais */}
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Total de Vendas"
                  value={dashboard.total_vendas}
                  prefix={<ShoppingOutlined />}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Valor Total"
                  value={dashboard.valor_total}
                  formatter={(value) => formatCurrency(Number(value))}
                  prefix={<DollarOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Ticket Médio"
                  value={dashboard.media_valor}
                  formatter={(value) => formatCurrency(Number(value))}
                  prefix={<DollarOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Produtos Diferentes"
                  value={dashboard.top_produtos.length}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ color: '#eb2f96' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Top 5 Produtos e Vendedores */}
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card
                title={
                  <Space>
                    <TrophyOutlined />
                    Top 5 Produtos
                  </Space>
                }
              >
                <Table
                  dataSource={dashboard.top_produtos}
                  columns={produtosColumns}
                  rowKey="produto"
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card
                title={
                  <Space>
                    <UserOutlined />
                    Top 5 Vendedores
                  </Space>
                }
              >
                <Table
                  dataSource={dashboard.top_vendedores}
                  columns={vendedoresColumns}
                  rowKey="vendedor_id"
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {!dashboard && !loading && (
        <Card>
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Title level={4}>Nenhum dado encontrado</Title>
            <p>Não há vendas registradas para o período selecionado.</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default DashboardTab;