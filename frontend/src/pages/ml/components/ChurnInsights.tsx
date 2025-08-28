import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Progress,
  Alert,
} from 'antd';
import {
  UserOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  FallOutlined,
} from '@ant-design/icons';
import { RiskDistributionChart, ChurnTrendChart } from '../../../components/charts/ChurnCharts';

const { Text } = Typography;

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
  const riskDistributionData = {
    baixo: insights.clientes_risco_baixo,
    medio: insights.clientes_risco_medio,
    alto: insights.clientes_risco_alto,
    critico: insights.clientes_risco_critico || 0,
  };

  const churnTrendData = [
    { month: 'Jan', churnRate: 5.2, predictions: 5.8, accuracy: 92 },
    { month: 'Fev', churnRate: 4.8, predictions: 5.1, accuracy: 94 },
    { month: 'Mar', churnRate: 6.1, predictions: 6.3, accuracy: 91 },
    { month: 'Abr', churnRate: 5.9, predictions: 6.0, accuracy: 93 },
    { month: 'Mai', churnRate: 6.5, predictions: 6.7, accuracy: 90 },
    { month: 'Jun', churnRate: insights.taxa_churn_atual, predictions: insights.taxa_churn_atual + 0.3, accuracy: 89 },
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
              prefix={<FallOutlined />} // Corrigido para ícone existente
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
          <RiskDistributionChart data={riskDistributionData} />
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
          <ChurnTrendChart data={churnTrendData} />
        </Col>
      </Row>

      {/* Fatores de Churn */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Principais Fatores de Churn">
            <div style={{ padding: '16px 0' }}>
              {topFactorsData.map((factor, index) => (
                <div key={index} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text strong>{factor.factor}</Text>
                    <Text>{factor.impact}% de impacto</Text>
                  </div>
                  <Progress
                    percent={factor.impact}
                    strokeColor="#ff4d4f"
                    showInfo={false}
                  />
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {factor.count} clientes afetados
                  </Text>
                </div>
              ))}
            </div>
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