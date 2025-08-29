import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Button, 
  DatePicker, 
  Select, 
  Space,
  Tag,
  Progress,
  Typography,
  Divider,
  Alert,
  Tooltip
} from 'antd';
import { 
  DollarCircleOutlined, 
  LineChartOutlined, 
  TeamOutlined,
  CrownOutlined,
  RiseOutlined,
  FallOutlined,
  ThunderboltOutlined,
  EyeOutlined,
  BarChartOutlined,
  PieChartOutlined
} from '@ant-design/icons';
import { Line, Column, Area, Pie, Gauge, DualAxes } from '@ant-design/plots';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

interface MetricaExecutiva {
  receita_recorrente_mensal: number;
  crescimento_mrr: number;
  lifetime_value: number;
  cac_medio: number;
  payback_period: number;
  churn_rate: number;
  expansion_revenue: number;
  nps_score: number;
  market_share: number;
}

const DashboardExecutivo: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [periodo, setPeriodo] = useState('12m');
  const [metricas, setMetricas] = useState<MetricaExecutiva | null>(null);

  // Dados mockados para demonstração
  const mockMetricas: MetricaExecutiva = {
    receita_recorrente_mensal: 450000,
    crescimento_mrr: 15.8,
    lifetime_value: 28500,
    cac_medio: 2800,
    payback_period: 8,
    churn_rate: 3.2,
    expansion_revenue: 85000,
    nps_score: 67,
    market_share: 12.5
  };

  useEffect(() => {
    carregarDados();
  }, [periodo]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      // Em produção, chamadas reais para API
      setTimeout(() => {
        setMetricas(mockMetricas);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setLoading(false);
    }
  };

  // Dados para gráficos
  const dadosMRR = [
    { mes: 'Jan', mrr: 320000, crescimento: 8.2 },
    { mes: 'Fev', mrr: 345000, crescimento: 7.8 },
    { mes: 'Mar', mrr: 375000, crescimento: 8.7 },
    { mes: 'Abr', mrr: 395000, crescimento: 5.3 },
    { mes: 'Mai', mrr: 425000, crescimento: 7.6 },
    { mes: 'Jun', mrr: 450000, crescimento: 5.9 }
  ];

  const configMRR = {
    data: dadosMRR,
    xField: 'mes',
    yField: ['mrr', 'crescimento'],
    geometryOptions: [
      {
        geometry: 'column',
        color: '#5B8FF9',
      },
      {
        geometry: 'line',
        color: '#E76C5E',
      },
    ],
    meta: {
      mrr: {
        alias: 'MRR (R$)',
        formatter: (v: number) => `R$ ${(v/1000).toFixed(0)}K`,
      },
      crescimento: {
        alias: 'Crescimento (%)',
        formatter: (v: number) => `${v}%`,
      },
    },
  };

  const dadosReceita = [
    { trimestre: 'Q1 2024', nova: 280000, expansao: 45000, churn: -35000 },
    { trimestre: 'Q2 2024', nova: 320000, expansao: 52000, churn: -28000 },
    { trimestre: 'Q3 2024', nova: 380000, expansao: 61000, churn: -42000 },
    { trimestre: 'Q4 2024', nova: 420000, expansao: 73000, churn: -38000 },
    { trimestre: 'Q1 2025', nova: 480000, expansao: 85000, churn: -32000 },
  ];

  const configReceita = {
    data: dadosReceita,
    xField: 'trimestre',
    yField: ['nova', 'expansao', 'churn'],
    isStack: true,
    seriesField: 'type',
    color: ['#52c41a', '#1890ff', '#f5222d'],
  };

  const dadosSegmentos = [
    { segmento: 'Enterprise', receita: 180000, porcentagem: 40 },
    { segmento: 'Mid Market', receita: 135000, porcentagem: 30 },
    { segmento: 'SMB', receita: 90000, porcentagem: 20 },
    { segmento: 'Startup', receita: 45000, porcentagem: 10 },
  ];

  const configSegmentos = {
    data: dadosSegmentos,
    angleField: 'receita',
    colorField: 'segmento',
    radius: 0.8,
    label: {
      type: 'inner',
      offset: '-50%',
      content: '{name} {percentage}',
      style: {
        textAlign: 'center',
        fontSize: 14,
      },
    },
    interactions: [{ type: 'element-active' }],
    color: ['#FF6B3B', '#C23531', '#2F4554', '#61A0A8'],
  };

  const kpis = [
    {
      title: 'MRR',
      value: metricas?.receita_recorrente_mensal || 0,
      prefix: <DollarCircleOutlined />,
      formatter: (value: any) => `R$ ${(Number(value)/1000).toLocaleString('pt-BR')}K`,
      color: '#3f8600',
      trend: 15.8,
      trendUp: true
    },
    {
      title: 'LTV',
      value: metricas?.lifetime_value || 0,
      prefix: <LineChartOutlined />,
      formatter: (value: any) => `R$ ${(Number(value)/1000).toLocaleString('pt-BR')}K`,
      color: '#1890ff',
      trend: 8.3,
      trendUp: true
    },
    {
      title: 'CAC',
      value: metricas?.cac_medio || 0,
      prefix: <TeamOutlined />,
      formatter: (value: any) => `R$ ${Number(value).toLocaleString('pt-BR')}`,
      color: '#722ed1',
      trend: -5.2,
      trendUp: false
    },
    {
      title: 'LTV/CAC',
      value: metricas ? Math.round(metricas.lifetime_value / metricas.cac_medio * 10) / 10 : 0,
      prefix: <CrownOutlined />,
      formatter: (value: any) => `${Number(value)}x`,
      color: '#fa8c16',
      trend: 12.1,
      trendUp: true
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2}>
            <BarChartOutlined /> Dashboard Executivo
          </Title>
          <Text type="secondary">
            Visão estratégica dos principais KPIs do negócio
          </Text>
        </div>
        <Space>
          <Select
            value={periodo}
            onChange={setPeriodo}
            style={{ width: 120 }}
          >
            <Option value="3m">3 Meses</Option>
            <Option value="6m">6 Meses</Option>
            <Option value="12m">12 Meses</Option>
            <Option value="24m">24 Meses</Option>
          </Select>
          <Button type="primary" onClick={carregarDados} loading={loading}>
            Atualizar
          </Button>
        </Space>
      </div>

      {/* KPIs Principais */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {kpis.map((kpi, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card>
              <Statistic
                title={kpi.title}
                value={kpi.value}
                prefix={kpi.prefix}
                formatter={kpi.formatter}
                valueStyle={{ color: kpi.color }}
              />
              <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center' }}>
                {kpi.trendUp ? (
                  <RiseOutlined style={{ color: '#3f8600', marginRight: '4px' }} />
                ) : (
                  <FallOutlined style={{ color: '#f5222d', marginRight: '4px' }} />
                )}
                <Text type={kpi.trendUp ? 'success' : 'danger'}>
                  {kpi.trend}% vs mês anterior
                </Text>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Métricas Secundárias */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card title="Health Score">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Gauge
                percent={metricas ? (100 - metricas.churn_rate) / 100 : 0}
                color={['#F4664A', '#FAAD14', '#30BF78']}
                height={120}
                innerRadius={0.75}
                statistic={{
                  content: {
                    style: {
                      fontSize: '16px',
                      lineHeight: '16px',
                    },
                    formatter: () => `${metricas ? (100 - metricas.churn_rate).toFixed(1) : 0}%`,
                  },
                }}
              />
            </div>
            <div style={{ textAlign: 'center', marginTop: '8px' }}>
              <Text type="secondary">Taxa de Retenção</Text>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={8}>
          <Card title="NPS Score">
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                fontSize: '48px', 
                fontWeight: 'bold', 
                color: metricas && metricas.nps_score >= 50 ? '#52c41a' : 
                       metricas && metricas.nps_score >= 0 ? '#faad14' : '#f5222d'
              }}>
                {metricas?.nps_score || 0}
              </div>
              <Progress 
                percent={metricas ? ((metricas.nps_score + 100) / 2) : 50} 
                strokeColor={{
                  from: '#f5222d',
                  to: '#52c41a',
                }}
                showInfo={false}
              />
              <Text type="secondary">Net Promoter Score</Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card title="Payback Period">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#1890ff' }}>
                {metricas?.payback_period || 0}
              </div>
              <div style={{ fontSize: '16px', color: '#666', marginBottom: '16px' }}>
                meses
              </div>
              <Tag color={metricas && metricas.payback_period <= 12 ? 'green' : metricas && metricas.payback_period <= 18 ? 'orange' : 'red'}>
                {metricas && metricas.payback_period <= 12 ? 'Excelente' : 
                 metricas && metricas.payback_period <= 18 ? 'Bom' : 'Atenção'}
              </Tag>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Gráficos Principais */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="MRR e Crescimento" loading={loading}>
            <DualAxes {...configMRR} height={300} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Receita por Segmento" loading={loading}>
            <Pie {...configSegmentos} height={300} />
          </Card>
        </Col>
      </Row>

      {/* Análise de Cohort e Projeções */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="Previsão de Receita">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Meta Trimestral:</Text>
                <Text strong>R$ 1.2M</Text>
              </div>
              <Progress percent={75} strokeColor="#52c41a" />
              
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Meta Anual:</Text>
                <Text strong>R$ 4.8M</Text>
              </div>
              <Progress percent={62} strokeColor="#1890ff" />
              
              <Divider />
              
              <Alert
                message="Projeção Otimista"
                description="Com a taxa de crescimento atual, expectativa de R$ 5.2M em 2025"
                type="success"
                showIcon
              />
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Indicadores de Eficiência">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Card size="small">
                    <Statistic
                      title="Magic Number"
                      value={1.3}
                      precision={1}
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small">
                    <Statistic
                      title="Rule of 40"
                      value={45}
                      suffix="%"
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={12}>
                  <Card size="small">
                    <Statistic
                      title="Gross Margin"
                      value={78}
                      suffix="%"
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small">
                    <Statistic
                      title="Burn Rate"
                      value={85000}
                      prefix="R$"
                      formatter={(value) => `${(Number(value)/1000).toFixed(0)}K`}
                      valueStyle={{ color: '#fa8c16' }}
                    />
                  </Card>
                </Col>
              </Row>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Alertas Estratégicos */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="🎯 Insights Estratégicos">
            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                <Alert
                  message="Oportunidade de Expansão"
                  description="Segmento Enterprise com 40% da receita, potencial para 50%"
                  type="info"
                  showIcon
                  action={
                    <Button size="small" type="primary">
                      Ver Plano
                    </Button>
                  }
                />
              </Col>
              <Col xs={24} md={8}>
                <Alert
                  message="Meta de CAC Atingida"
                  description="CAC reduziu 5.2%, próximo do target de R$ 2.500"
                  type="success"
                  showIcon
                />
              </Col>
              <Col xs={24} md={8}>
                <Alert
                  message="Churn Rate Estável"
                  description="Mantido em 3.2%, abaixo da meta de 5%"
                  type="success"
                  showIcon
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardExecutivo;