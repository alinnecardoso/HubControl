// src/pages/ml/MLChurn.tsx
import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Space,
  Typography,
  Alert,
  Tabs,
  Table,
  Tag,
  Progress,
  Statistic,
  message,
} from 'antd';
import {
  RobotOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  EyeOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FallOutlined,
} from '@ant-design/icons';
// Local Component Imports
import { ChurnPredictionForm } from './components/ChurnPredictionForm.tsx';
import { ChurnInsights as ChurnInsightsPanel } from './components/ChurnInsights.tsx';
import ModelTraining from './components/ModelTraining.tsx';
import ChurnRiskAnalysis from './components/ChurnRiskAnalysis.tsx';

const { Title, Text } = Typography;

interface ChurnPrediction {
  cliente_id: string;
  risk_level: 'baixo' | 'medio' | 'alto' | 'critico';
  risk_score: number; // 0..1
  predictions: Record<string, number>;
  features_importance: Record<string, number>;
  recommendations: string[];
  timestamp: string; // ISO
}

// Renomeado para evitar conflito com o componente ChurnInsights
interface ChurnInsightsData {
  total_clientes: number;
  clientes_churn: number;
  clientes_ativos: number;
  taxa_churn_atual: number;
  clientes_risco_alto: number;
  clientes_risco_medio: number;
  clientes_risco_baixo: number;
}

const MLChurn: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [isTrained, setIsTrained] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState<'idle' | 'training' | 'completed'>('idle');
  const [predictions, setPredictions] = useState<ChurnPrediction[]>([]);
  const [insights, setInsights] = useState<ChurnInsightsData | null>(null);

  useEffect(() => {
    // Simula checagem inicial do status do modelo
    const t = setTimeout(() => {
      setIsTrained(true);
      setTrainingStatus('completed');
    }, 1000);
    return () => clearTimeout(t);
  }, []);

  const handleTrainModels = async () => {
    setLoading(true);
    setTrainingStatus('training');
    try {
      // Simulação de treino
      await new Promise((r) => setTimeout(r, 2000));
      setTrainingStatus('completed');
      setIsTrained(true);
      message.success('Modelos treinados com sucesso!');
      // Simula insights
      setInsights({
        total_clientes: 1250,
        clientes_churn: 87,
        clientes_ativos: 1163,
        taxa_churn_atual: 6.96,
        clientes_risco_alto: 45,
        clientes_risco_medio: 123,
        clientes_risco_baixo: 995,
      });
    } catch {
      message.error('Erro ao treinar modelos');
    } finally {
      setLoading(false);
    }
  };

  const handlePrediction = async (clienteId: string) => {
    setLoading(true);
    try {
      await new Promise((r) => setTimeout(r, 800));
      const now = new Date().toISOString();
      const newPrediction: ChurnPrediction = {
        cliente_id: clienteId,
        risk_level: Math.random() > 0.7 ? 'alto' : Math.random() > 0.4 ? 'medio' : 'baixo',
        risk_score: Math.random(),
        predictions: {
          random_forest: Math.random(),
          xgboost: Math.random(),
          lightgbm: Math.random(),
          neural_network: Math.random(),
          ensemble: Math.random(),
        },
        features_importance: {
          health_score_atual: Math.random(),
          dias_vencimento_proximo: Math.random(),
          csat_medio: Math.random(),
          dias_ultima_interacao: Math.random(),
          ltv_valor: Math.random(),
        },
        recommendations: [
          'Monitorar Health Score',
          'Verificar renovação de contrato',
          'Acompanhar satisfação do cliente',
        ],
        timestamp: now,
      };
      setPredictions((prev) => [newPrediction, ...prev]);
      message.success('Previsão realizada com sucesso!');
    } catch {
      message.error('Erro ao fazer previsão');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: ChurnPrediction['risk_level']) => {
    switch (level) {
      case 'baixo':
        return 'green';
      case 'medio':
        return 'orange';
      case 'alto':
        return 'red';
      case 'critico':
        return 'volcano';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      title: 'Cliente ID',
      dataIndex: 'cliente_id',
      key: 'cliente_id',
    },
    {
      title: 'Nível de Risco',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level: ChurnPrediction['risk_level']) => (
        <Tag color={getRiskLevelColor(level)}>{String(level).toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Score de Risco',
      dataIndex: 'risk_score',
      key: 'risk_score',
      render: (score: number) => (
        <Progress
          percent={Math.round(score * 100)}
          size="small"
          status={score > 0.7 ? 'exception' : score > 0.4 ? 'normal' : 'success'}
        />
      ),
    },
    {
      title: 'Previsão Ensemble',
      dataIndex: 'predictions',
      key: 'ensemble',
      render: (p: Record<string, number>) => <Text strong>{Math.round((p?.ensemble ?? 0) * 100)}%</Text>,
    },
    {
      title: 'Recomendações',
      dataIndex: 'recommendations',
      key: 'recommendations',
      render: (recs: string[]) => (
        <Space direction="vertical" size="small">
          {(recs || []).slice(0, 2).map((rec, i) => (
            <Text key={i} type="secondary" style={{ fontSize: 12 }}>
              • {rec}
            </Text>
          ))}
        </Space>
      ),
    },
    {
      title: 'Data',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (ts: string) => new Date(ts).toLocaleDateString('pt-BR'),
    },
  ];

  return (
    <div>
      {/* Header */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card>
            <Row gutter={16} align="middle">
              <Col>
                <RobotOutlined style={{ fontSize: 32, color: '#1890ff' }} />
              </Col>
              <Col flex="auto">
                <Title level={3} style={{ margin: 0 }}>
                  Machine Learning - Previsão de Churn
                </Title>
                <Text type="secondary">Sistema para identificar clientes em risco de churn</Text>
              </Col>
              <Col>
                <Space>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={handleTrainModels}
                    loading={trainingStatus === 'training'}
                    disabled={trainingStatus === 'training'}
                  >
                    {trainingStatus === 'training' ? 'Treinando...' : 'Treinar Modelos'}
                  </Button>
                  <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>
                    Atualizar
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* KPIs */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Status dos Modelos"
              value={isTrained ? 'Treinados' : 'Não Treinados'}
              prefix={
                isTrained ? (
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                ) : (
                  <ClockCircleOutlined style={{ color: '#faad14' }} />
                )
              }
              valueStyle={{ color: isTrained ? '#52c41a' : '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Total de Previsões" value={predictions.length} prefix={<EyeOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Clientes de Alto Risco"
              value={insights?.clientes_risco_alto ?? 0}
              prefix={<AlertOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Taxa de Churn Atual"
              value={insights?.taxa_churn_atual ?? 0}
              suffix="%"
              precision={2}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Aviso */}
      {!isTrained && (
        <Row style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Alert
              message="Modelos não treinados"
              description="É necessário treinar os modelos antes de fazer previsões. Clique em 'Treinar Modelos' para começar."
              type="warning"
              showIcon
              action={
                <Button size="small" type="primary" onClick={handleTrainModels}>
                  Treinar Agora
                </Button>
              }
            />
          </Col>
        </Row>
      )}

      {/* Conteúdo principal - Tabs v5 */}
      <Tabs
        defaultActiveKey="prediction"
        size="large"
        items={[
          {
            key: 'prediction',
            label: 'Previsão Individual',
            children: (
              <ChurnPredictionForm onPrediction={handlePrediction} loading={loading} isTrained={isTrained} />
            ),
          },
          {
            key: 'insights',
            label: 'Insights Gerais',
            children: (
              <>
                <Card
                  bodyStyle={{ background: '#141414', borderRadius: 20, padding: 32 }}
                  style={{ boxShadow: '0 4px 24px #00000033', border: 'none', marginBottom: 16 }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                    <FallOutlined style={{ fontSize: 32, color: '#F22987', marginRight: 16 }} />
                    <Title level={4} style={{ color: '#F22987', margin: 0 }}>Como interpretar as métricas de Churn</Title>
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 24, color: '#E6E8EA', fontSize: 16, lineHeight: 2 }}>
                    <li><b style={{ color: '#F22987' }}>Status dos Modelos:</b> Indica se os modelos de ML já foram treinados e estão prontos para uso.</li>
                    <li><b style={{ color: '#F22987' }}>Total de Previsões:</b> Quantidade de previsões realizadas até o momento.</li>
                    <li><b style={{ color: '#F22987' }}>Clientes de Alto Risco:</b> Número de clientes identificados com alto risco de churn.</li>
                    <li><b style={{ color: '#F22987' }}>Taxa de Churn Atual:</b> Percentual de clientes que cancelaram em relação ao total.</li>
                    <li><b style={{ color: '#F22987' }}>Previsão Individual:</b> Análise detalhada para um cliente específico, incluindo nível de risco, score, recomendações e fatores de influência.</li>
                    <li><b style={{ color: '#F22987' }}>Previsões por Modelo:</b> Resultados dos diferentes algoritmos usados (Random Forest, XGBoost, etc).</li>
                    <li><b style={{ color: '#F22987' }}>Fatores de Influência:</b> Principais variáveis que impactaram a previsão (ex: dias para vencimento, última interação, health score, CSAT).</li>
                    <li><b style={{ color: '#F22987' }}>Recomendações de Ação:</b> Sugestões práticas para reduzir o risco de churn do cliente.</li>
                  </ul>
                </Card>
                <ChurnInsightsPanel insights={insights} />
                <div style={{ marginTop: 24 }}>
                  <ChurnRiskAnalysis />
                </div>
              </>
            ),
          },
          {
            key: 'risk',
            label: 'Análise de Risco',
            children: <ChurnRiskAnalysis />,
          },
          {
            key: 'history',
            label: 'Histórico de Previsões',
            children: (
              <Card title="Previsões Realizadas">
                <Table
                  columns={columns}
                  dataSource={predictions}
                  rowKey={(r) => `${r.cliente_id}-${r.timestamp}`} // evita conflito se tiver previsões repetidas
                  pagination={{ pageSize: 10 }}
                  loading={loading}
                />
              </Card>
            ),
          },
          {
            key: 'training',
            label: 'Treinamento',
            children: <ModelTraining status={trainingStatus} onTrain={handleTrainModels} loading={loading} />,
          },
        ]}
      />
    </div>
  );
};

export default MLChurn;
