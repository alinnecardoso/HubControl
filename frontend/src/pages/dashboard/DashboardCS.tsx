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
  Alert,
  Tooltip
} from 'antd';
import { 
  HeartOutlined, 
  UserOutlined, 
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  FallOutlined,
  CustomerServiceOutlined,
  StarOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { Line, Column, Gauge, Liquid, Pie } from '@ant-design/plots';
import type { ColumnsType } from 'antd/es/table';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

interface ClienteCS {
  id: number;
  nome_principal: string;
  health_score: number;
  status_cliente: string;
  days_to_churn: number;
  last_interaction: string;
  csat_score: number;
  contract_value: number;
  renewal_probability: number;
}

interface MetricaCS {
  total_clientes: number;
  health_score_medio: number;
  churn_risk: number;
  csat_medio: number;
  renovacoes_periodo: number;
  retention_rate: number;
}

const DashboardCS: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [metricas, setMetricas] = useState<MetricaCS | null>(null);
  const [clientes, setClientes] = useState<ClienteCS[]>([]);
  const [filtros, setFiltros] = useState({
    dataInicio: null as any,
    dataFim: null as any,
    assessor: null as string | null,
  });

  // Dados mockados para demonstração
  const mockMetricas: MetricaCS = {
    total_clientes: 48,
    health_score_medio: 72,
    churn_risk: 8,
    csat_medio: 4.2,
    renovacoes_periodo: 12,
    retention_rate: 92.3
  };

  const mockClientes: ClienteCS[] = [
    {
      id: 1,
      nome_principal: "DENNIS",
      health_score: 85,
      status_cliente: "ativo",
      days_to_churn: 45,
      last_interaction: "2025-06-15",
      csat_score: 4.5,
      contract_value: 31200,
      renewal_probability: 0.85
    },
    {
      id: 2,
      nome_principal: "DANILLO",
      health_score: 32,
      status_cliente: "churn_risk",
      days_to_churn: 7,
      last_interaction: "2025-05-20",
      csat_score: 2.8,
      contract_value: 36000,
      renewal_probability: 0.25
    },
    {
      id: 3,
      nome_principal: "Gabriel Morais",
      health_score: 78,
      status_cliente: "ativo",
      days_to_churn: 60,
      last_interaction: "2025-06-18",
      csat_score: 4.8,
      contract_value: 60000,
      renewal_probability: 0.90
    }
  ];

  useEffect(() => {
    carregarDados();
  }, [filtros]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      // Em produção, chamadas reais para API
      setTimeout(() => {
        setMetricas(mockMetricas);
        setClientes(mockClientes);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setLoading(false);
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    if (score >= 40) return '#fa8c16';
    return '#f5222d';
  };

  const getHealthScoreStatus = (score: number) => {
    if (score >= 80) return { text: 'Excelente', color: 'success' };
    if (score >= 60) return { text: 'Bom', color: 'warning' };
    if (score >= 40) return { text: 'Atenção', color: 'error' };
    return { text: 'Crítico', color: 'error' };
  };

  const getChurnRiskLevel = (days: number) => {
    if (days <= 7) return { text: 'Alto Risco', color: 'red' };
    if (days <= 15) return { text: 'Risco Médio', color: 'orange' };
    if (days <= 30) return { text: 'Risco Baixo', color: 'yellow' };
    return { text: 'Seguro', color: 'green' };
  };

  const colunas: ColumnsType<ClienteCS> = [
    {
      title: 'Cliente',
      dataIndex: 'nome_principal',
      key: 'nome_principal',
      render: (nome) => <Text strong>{nome}</Text>
    },
    {
      title: 'Health Score',
      dataIndex: 'health_score',
      key: 'health_score',
      render: (score) => {
        const status = getHealthScoreStatus(score);
        return (
          <div>
            <Progress
              percent={score}
              size="small"
              strokeColor={getHealthScoreColor(score)}
              format={() => `${score}`}
            />
            <Tag color={status.color} style={{ marginTop: 4 }}>
              {status.text}
            </Tag>
          </div>
        );
      },
      sorter: (a, b) => a.health_score - b.health_score,
    },
    {
      title: 'Risco Churn',
      dataIndex: 'days_to_churn',
      key: 'days_to_churn',
      render: (days) => {
        const risk = getChurnRiskLevel(days);
        return (
          <Tag color={risk.color}>
            {risk.text} ({days}d)
          </Tag>
        );
      },
      sorter: (a, b) => a.days_to_churn - b.days_to_churn,
    },
    {
      title: 'CSAT',
      dataIndex: 'csat_score',
      key: 'csat_score',
      render: (score) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <StarOutlined style={{ color: '#fadb14', marginRight: 4 }} />
          <Text>{score.toFixed(1)}</Text>
        </div>
      ),
      sorter: (a, b) => a.csat_score - b.csat_score,
    },
    {
      title: 'Valor Contrato',
      dataIndex: 'contract_value',
      key: 'contract_value',
      render: (value) => `R$ ${value.toLocaleString('pt-BR')}`,
      sorter: (a, b) => a.contract_value - b.contract_value,
    },
    {
      title: 'Prob. Renovação',
      dataIndex: 'renewal_probability',
      key: 'renewal_probability',
      render: (prob) => (
        <Progress
          percent={Math.round(prob * 100)}
          size="small"
          strokeColor={prob >= 0.7 ? '#52c41a' : prob >= 0.4 ? '#faad14' : '#f5222d'}
        />
      ),
      sorter: (a, b) => a.renewal_probability - b.renewal_probability,
    },
    {
      title: 'Última Interação',
      dataIndex: 'last_interaction',
      key: 'last_interaction',
      render: (date) => {
        const daysSince = Math.floor((new Date().getTime() - new Date(date).getTime()) / (1000 * 60 * 60 * 24));
        return (
          <div>
            <div>{new Date(date).toLocaleDateString('pt-BR')}</div>
            <Text type="secondary">{daysSince} dias atrás</Text>
          </div>
        );
      }
    }
  ];

  const dadosHealthScore = [
    { mes: 'Jan', score: 68 },
    { mes: 'Fev', score: 71 },
    { mes: 'Mar', score: 69 },
    { mes: 'Abr', score: 74 },
    { mes: 'Mai', score: 73 },
    { mes: 'Jun', score: 72 }
  ];

  const configHealthScore = {
    data: dadosHealthScore,
    xField: 'mes',
    yField: 'score',
    smooth: true,
    color: '#52c41a',
    point: {
      size: 5,
      shape: 'diamond',
    },
  };

  const dadosChurn = [
    { status: 'Seguro', quantidade: 32, cor: '#52c41a' },
    { status: 'Risco Baixo', quantidade: 8, cor: '#fadb14' },
    { status: 'Risco Médio', quantidade: 5, cor: '#fa8c16' },
    { status: 'Alto Risco', quantidade: 3, cor: '#f5222d' }
  ];

  const configChurn = {
    data: dadosChurn,
    angleField: 'quantidade',
    colorField: 'status',
    radius: 0.8,
    color: dadosChurn.map(item => item.cor),
    label: {
      type: 'outer',
      content: '{name} {percentage}',
    },
    interactions: [{ type: 'element-active' }],
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <CustomerServiceOutlined /> Dashboard Customer Success
        </Title>
        <Text type="secondary">
          Monitore a saúde dos clientes e previna churn
        </Text>
      </div>

      {/* Filtros */}
      <Card style={{ marginBottom: '24px' }}>
        <Space wrap>
          <RangePicker
            placeholder={['Data início', 'Data fim']}
            format="DD/MM/YYYY"
          />
          <Select
            placeholder="Assessor CS"
            allowClear
            style={{ width: 150 }}
          >
            <Option value="1">Ana Silva</Option>
            <Option value="2">João Santos</Option>
            <Option value="3">Maria Costa</Option>
          </Select>
          <Button type="primary" onClick={carregarDados} loading={loading}>
            Aplicar Filtros
          </Button>
        </Space>
      </Card>

      {/* Cards de Métricas Principais */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Clientes"
              value={metricas?.total_clientes || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Health Score Médio"
              value={metricas?.health_score_medio || 0}
              suffix="/100"
              prefix={<HeartOutlined />}
              valueStyle={{ color: getHealthScoreColor(metricas?.health_score_medio || 0) }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Clientes em Risco"
              value={metricas?.churn_risk || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="CSAT Médio"
              value={metricas?.csat_medio || 0}
              precision={1}
              suffix="/5.0"
              prefix={<StarOutlined />}
              valueStyle={{ color: '#fadb14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Segunda linha de métricas */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card title="Taxa de Retenção">
            <Liquid
              percent={metricas?.retention_rate ? metricas.retention_rate / 100 : 0}
              height={150}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card title="Renovações no Período">
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#1890ff' }}>
                {metricas?.renovacoes_periodo || 0}
              </div>
              <div style={{ fontSize: '16px', color: '#666' }}>
                contratos renovados
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card title="Alertas Ativos">
            <List
              size="small"
              dataSource={[
                { tipo: 'Churn Alto Risco', quantidade: 3, cor: 'red' },
                { tipo: 'Health Score Baixo', quantidade: 5, cor: 'orange' },
                { tipo: 'CSAT Baixo', quantidade: 2, cor: 'yellow' },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <Space>
                    <WarningOutlined style={{ color: item.cor }} />
                    <Text>{item.tipo}</Text>
                    <Tag color={item.cor}>{item.quantidade}</Tag>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* Gráficos */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Evolução Health Score Médio" loading={loading}>
            <Line {...configHealthScore} height={250} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Distribuição Risco de Churn" loading={loading}>
            <Pie {...configChurn} height={250} />
          </Card>
        </Col>
      </Row>

      {/* Ações Recomendadas */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="🚨 Ações Prioritárias">
            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                <Alert
                  message="3 Clientes Alto Risco"
                  description="Danillo, Erik e Rodrigo precisam de atenção imediata"
                  type="error"
                  showIcon
                  action={
                    <Button size="small" danger>
                      Ver Detalhes
                    </Button>
                  }
                />
              </Col>
              <Col xs={24} md={8}>
                <Alert
                  message="5 Health Scores Baixos"
                  description="Clientes com score abaixo de 40 precisam de intervenção"
                  type="warning"
                  showIcon
                  action={
                    <Button size="small">
                      Criar Plano
                    </Button>
                  }
                />
              </Col>
              <Col xs={24} md={8}>
                <Alert
                  message="12 Renovações Próximas"
                  description="Contratos vencendo nos próximos 30 dias"
                  type="info"
                  showIcon
                  action={
                    <Button size="small" type="primary">
                      Preparar Renovação
                    </Button>
                  }
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Tabela de Clientes */}
      <Card title="Monitoramento de Clientes" loading={loading}>
        <Table
          columns={colunas}
          dataSource={clientes}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} de ${total} clientes`
          }}
          rowClassName={(record) => {
            if (record.health_score < 40) return 'row-critical';
            if (record.days_to_churn <= 7) return 'row-high-risk';
            return '';
          }}
        />
      </Card>

      <style>{`
        .row-critical {
          background-color: #fff2f0;
        }
        .row-high-risk {
          background-color: #fff7e6;
        }
      `}</style>
    </div>
  );
};

export default DashboardCS;