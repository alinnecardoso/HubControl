import React from 'react';
import { Card, Typography, Row, Col, Statistic } from 'antd';
import { Bar } from 'react-chartjs-2';
import { FallOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface RiskClient {
  cliente_id: string;
  nome: string;
  risk_level: string;
  risk_score: number;
  health_score: number;
  dias_vencimento: number;
  csat_medio: number;
  recommendations: string[];
}

interface ChurnRiskAnalysisProps {
  data?: {
    total_analyzed: number;
    high_risk_count: number;
    risk_threshold: number;
    high_risk_clients: RiskClient[];
    risk_distribution: Record<string, number>;
  };
  loading?: boolean;
}

const ChurnRiskAnalysis: React.FC<ChurnRiskAnalysisProps> = ({ data, loading }) => {
  // Gráfico de distribuição de risco
  const chartData = {
    labels: ['Baixo', 'Médio', 'Alto', 'Crítico'],
    datasets: [
      {
        label: 'Clientes',
        data: [
          data?.risk_distribution.baixo ?? 0,
          data?.risk_distribution.medio ?? 0,
          data?.risk_distribution.alto ?? 0,
          data?.risk_distribution.critico ?? 0,
        ],
        backgroundColor: ['#52c41a', '#faad14', '#ff4d4f', '#d4380d'],
      },
    ],
  };

  return (
    <Card style={{ background: '#141414', borderRadius: 16, boxShadow: '0 2px 8px #00000022', color: '#E6E8EA' }}>
      <Row gutter={[16, 16]} align="middle">
        <Col>
          <FallOutlined style={{ fontSize: 32, color: '#F22987', marginRight: 8 }} />
        </Col>
        <Col flex="auto">
          <Title level={4} style={{ color: '#F22987', marginBottom: 8 }}>Análise de Risco de Churn</Title>
        </Col>
      </Row>
      <Text type="secondary" style={{ color: '#A3A8AD' }}>
        Visualização dos clientes em risco, distribuição dos níveis e recomendações.
      </Text>
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Statistic title="Total Analisado" value={data?.total_analyzed ?? 0} />
          <Statistic title="Alto Risco" value={data?.high_risk_count ?? 0} valueStyle={{ color: '#ff4d4f' }} />
        </Col>
        <Col span={12}>
          <Bar data={chartData} options={{ plugins: { legend: { display: false } } }} />
        </Col>
      </Row>
      <div style={{ marginTop: 32 }}>
        <Title level={5} style={{ color: '#F22987' }}>Top Clientes de Alto Risco</Title>
        {data?.high_risk_clients?.length ? (
          <ul style={{ color: '#E6E8EA', fontSize: 15 }}>
            {data.high_risk_clients.slice(0, 5).map((c) => (
              <li key={c.cliente_id}>
                <b>{c.nome}</b> (Score: <span style={{ color: '#ff4d4f' }}>{Math.round(c.risk_score * 100)}%</span>) - Recomendações: {c.recommendations.join(', ')}
              </li>
            ))}
          </ul>
        ) : (
          <Text type="secondary">Nenhum cliente de alto risco encontrado.</Text>
        )}
      </div>
    </Card>
  );
};

export default ChurnRiskAnalysis;
