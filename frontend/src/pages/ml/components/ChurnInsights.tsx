import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Divider,
  Progress,
  Alert,
} from 'antd';
import { Pie, Column, Line } from '@ant-design/plots';
import {
  UserOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  FallOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface ChurnInsightsProps {
  insights: any;
}

export const ChurnInsights: React.FC<ChurnInsightsProps> = ({ insights }) => {
  if (!insights) {
    return (
      <Alert
        message="Dados não disponíveis"
        description="Execute o treinamento dos modelos para ver os insights."
        type="info"
        showIcon
      />
    );
  }

  // Dados para gráficos
  const riskDistributionData = [
    { type: 'Baixo Risco', value: insights.clientes_risco_baixo, color: '#52c41a' },
    { type: 'Médio Risco', value: insights.clientes_risco_medio, color: '#faad14' },
    { type: 'Alto Risco', value: insights.clientes_risco_alto, color: '#ff4d4f' },
  ];

  const churnTrendData = [
    { month: 'Jan', churn_rate: 5.2, predicted: 5.8 },
    { month: 'Fev', churn_rate: 4.8, predicted: 5.1 },
    { month: 'Mar', churn_rate: 6.1, predicted: 6.3 },
    { month: 'Abr', churn_rate: 5.9, predicted: 6.0 },
    { month: 'Mai', churn_rate: 6.5, predicted: 6.7 },
    { month: 'Jun', churn_rate: 6.9, predicted: 7.2 },
  ];

  const topFactorsData = [
    { factor: 'Health Score Baixo', impact: 35, count: 156 },
    { factor: 'Contrato Vencendo', impact: 28, count: 123 },
    { factor: 'CSAT Baixo', impact: 22, count: 98 },
    { factor: 'Sem Interação', impact: 15, count: 67 },
  ];

  return (
    <div>
      {/* Métricas Principais */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total de Clientes"
              value={insights.total_clientes}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Taxa de Churn Atual"
              value={insights.taxa_churn_atual}
 suffix="%"
 prefix={<FallOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Clientes de Alto Risco"
              value={insights.clientes_risco_alto}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Clientes Estáveis"
              value={insights.clientes_risco_baixo}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Distribuição de Risco */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="Distribuição de Risco por Cliente">
            <Pie
              data={riskDistributionData}
              angleField="value"
              colorField="type"
              radius={0.8}
              label={{
                type: 'outer',
                content: '{name}: {percentage}',
              }}
              interactions={[
                {
                  type: 'element-active',
                },
              ]}
              height={300}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Análise de Risco Detalhada">
            <div style={{ padding: '20px 0' }}>
              <div style={{ marginBottom: 16 }}>
                <Text strong>Baixo Risco</Text>
                <Progress
                  percent={Math.round((insights.clientes_risco_baixo / insights.total_clientes) * 100)}
                  status="success"
                  strokeColor="#52c41a"
                />
                <Text type="secondary">{insights.clientes_risco_baixo} clientes</Text>
              </div>
              
              <div style={{ marginBottom: 16 }}>
                <Text strong>Médio Risco</Text>
                <Progress
                  percent={Math.round((insights.clientes_risco_medio / insights.total_clientes) * 100)}
                  strokeColor="#faad14"
                />
                <Text type="secondary">{insights.clientes_risco_medio} clientes</Text>
              </div>
              
              <div style={{ marginBottom: 16 }}>
                <Text strong>Alto Risco</Text>
                <Progress
                  percent={Math.round((insights.clientes_risco_alto / insights.total_clientes) * 100)}
                  status="exception"
                  strokeColor="#ff4d4f"
                />
                <Text type="secondary">{insights.clientes_risco_alto} clientes</Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Tendência de Churn */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Tendência de Churn (Últimos 6 Meses)">
            <Line
              data={churnTrendData}
              xField="month"
              yField="churn_rate"
              seriesField="type"
              yAxis={{
                label: {
                  formatter: (v) => `${v}%`,
                },
              }}
              legend={{
                position: 'top',
              }}
              height={300}
              color={['#ff4d4f', '#1890ff']}
            />
          </Card>
        </Col>
      </Row>

      {/* Fatores de Churn */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Principais Fatores de Churn">
            <Column
              data={topFactorsData}
              xField="factor"
              yField="impact"
              label={{
                position: 'middle',
                style: { 
                  fill: '#FFFFFF',
                  opacity: 0.6,
                },
              }}
              xAxis={{
                label: {
                  autoRotate: false,
                  autoHide: true,
                  autoEllipsis: true,
                },
              }}
              height={300}
              color="#ff4d4f"
            />
          </Card>
        </Col>
      </Row>

      {/* Alertas e Recomendações */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="Alertas Críticos" style={{ borderColor: '#ff4d4f' }}>
            <Alert
              message="Taxa de Churn em Aumento"
              description={`A taxa de churn aumentou ${((insights.taxa_churn_atual - 5.0) / 5.0 * 100).toFixed(1)}% em relação ao mês anterior.`}
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Alert
              message="Clientes de Alto Risco"
              description={`${insights.clientes_risco_alto} clientes identificados com alto risco de churn. Ação imediata necessária.`}
              type="warning"
              showIcon
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Recomendações de Ação">
            <div style={{ padding: '16px 0' }}>
              <div style={{ marginBottom: 12 }}>
                <Text strong>• Priorizar Atendimento</Text>
                <br />
                <Text type="secondary">Focar nos {insights.clientes_risco_alto} clientes de alto risco</Text>
              </div>
              
              <div style={{ marginBottom: 12 }}>
                <Text strong>• Melhorar Health Score</Text>
                <br />
                <Text type="secondary">Implementar ações para clientes com score baixo</Text>
              </div>
              
              <div style={{ marginBottom: 12 }}>
                <Text strong>• Renovação Antecipada</Text>
                <br />
                <Text type="secondary">Contatar clientes com contratos vencendo</Text>
              </div>
              
              <div>
                <Text strong>• Monitoramento CSAT</Text>
                <br />
                <Text type="secondary">Acompanhar satisfação dos clientes</Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}; 