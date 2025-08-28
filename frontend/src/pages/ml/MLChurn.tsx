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
  Spin,
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
import { ChurnPredictionForm } from './components/ChurnPredictionForm';
import { ChurnInsights as ChurnInsightsPanel } from './components/ChurnInsights';
import ModelTraining from './components/ModelTraining';
import ChurnRiskAnalysis from './components/ChurnRiskAnalysis';

// API Service
import { 
  mlChurnApi, 
  type ChurnInsights as ChurnInsightsData,
  type ChurnPredictionResponse,
  type TrainingStatus 
} from '../../services/mlApi';

const { Title, Text } = Typography;

interface ChurnPrediction extends ChurnPredictionResponse {
  timestamp: string; // ISO
}

const MLChurn: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [isTrained, setIsTrained] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState<'idle' | 'training' | 'completed'>('idle');
  const [predictions, setPredictions] = useState<ChurnPrediction[]>([]);
  const [insights, setInsights] = useState<ChurnInsightsData | null>(null);

  // Carrega status inicial dos modelos
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setInitialLoading(true);
        
        // Verifica status do treinamento
        const status = await mlChurnApi.getTrainingStatus();
        setIsTrained(status.is_trained);
        setTrainingStatus(status.status === 'trained' ? 'completed' : 'idle');
        
        // Se treinado, carrega insights
        if (status.is_trained) {
          try {
            const insightsData = await mlChurnApi.getChurnInsights();
            setInsights(insightsData);
          } catch (error) {
            console.warn('Erro ao carregar insights:', error);
          }
        }
      } catch (error) {
        console.error('Erro ao carregar status inicial:', error);
        message.error('Erro ao conectar com o serviço de ML');
      } finally {
        setInitialLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const handleTrainModels = async () => {
    setLoading(true);
    setTrainingStatus('training');
    try {
      const response = await mlChurnApi.trainModels({ force_retrain: true });
      
      if (response.status === 'training') {
        message.info(response.message);
        
        // Polling para verificar quando o treinamento termina
        const pollTrainingStatus = async () => {
          try {
            const status = await mlChurnApi.getTrainingStatus();
            
            if (status.is_trained) {
              setTrainingStatus('completed');
              setIsTrained(true);
              message.success('Modelos treinados com sucesso!');
              
              // Carrega insights atualizados
              const insightsData = await mlChurnApi.getChurnInsights();
              setInsights(insightsData);
              setLoading(false);
            } else {
              // Continua polling
              setTimeout(pollTrainingStatus, 5000);
            }
          } catch (error) {
            console.error('Erro no polling:', error);
            setTrainingStatus('idle');
            setLoading(false);
            message.error('Erro ao verificar status do treinamento');
          }
        };
        
        // Inicia polling após 5 segundos
        setTimeout(pollTrainingStatus, 5000);
      } else if (response.status === 'trained') {
        setTrainingStatus('completed');
        setIsTrained(true);
        message.success('Modelos já estão treinados!');
        setLoading(false);
      }
    } catch (error) {
      console.error('Erro ao treinar modelos:', error);
      setTrainingStatus('idle');
      message.error('Erro ao treinar modelos');
      setLoading(false);
    }
  };

  const handlePrediction = async (clienteId: string) => {
    setLoading(true);
    try {
      const predictionResponse = await mlChurnApi.predictChurn({ cliente_id: clienteId });
      
      const newPrediction: ChurnPrediction = {
        ...predictionResponse,
        timestamp: new Date().toISOString(),
      };
      
      setPredictions((prev) => [newPrediction, ...prev]);
      message.success('Previsão realizada com sucesso!');
    } catch (error) {
      console.error('Erro ao fazer previsão:', error);
      message.error('Erro ao fazer previsão. Verifique se o cliente existe e se os modelos estão treinados.');
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

  // Loading inicial
  if (initialLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '60vh',
        flexDirection: 'column',
        gap: 16
      }}>
        <Spin size="large" />
        <Text type="secondary">Carregando sistema de Machine Learning...</Text>
      </div>
    );
  }

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
                  styles={{ body: { background: '#141414', borderRadius: 20, padding: 32 } }}
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
