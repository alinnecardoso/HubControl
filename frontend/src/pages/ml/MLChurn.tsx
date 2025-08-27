import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Space,
  Typography,
  Alert,
  Spin,
  Tabs,
  Table,
  Tag,
  Progress,
  Statistic,
  Divider,
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
} from '@ant-design/icons';
import { Line, Pie, Column } from '@ant-design/plots';
import { ChurnPredictionForm } from './components/ChurnPredictionForm.tsx';
import { ChurnInsights } from './components/ChurnInsights.tsx';
//import { ModelTraining } from './components/ModelTraining';
//import { ChurnRiskAnalysis } from './components/ChurnRiskAnalysis';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface ChurnPrediction {
  cliente_id: string;
  risk_level: string;
  risk_score: number;
  predictions: Record<string, number>;
  features_importance: Record<string, number>;
  recommendations: string[];
  timestamp: string;
}

interface ChurnInsights {
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
  const [insights, setInsights] = useState<ChurnInsights | null>(null);
  const [riskAnalysis, setRiskAnalysis] = useState<any[]>([]);

  // Simulação de dados para demonstração
  useEffect(() => {
    // Simula verificação de status dos modelos
    setTimeout(() => {
      setIsTrained(true);
      setTrainingStatus('completed');
    }, 1000);
  }, []);

  const handleTrainModels = async () => {
    setLoading(true);
    setTrainingStatus('training');
    
    try {
      // Simula treinamento
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      setTrainingStatus('completed');
      setIsTrained(true);
      message.success('Modelos treinados com sucesso!');
      
      // Simula insights após treinamento
      setInsights({
        total_clientes: 1250,
        clientes_churn: 87,
        clientes_ativos: 1163,
        taxa_churn_atual: 6.96,
        clientes_risco_alto: 45,
        clientes_risco_medio: 123,
        clientes_risco_baixo: 995,
      });
      
    } catch (error) {
      message.error('Erro ao treinar modelos');
    } finally {
      setLoading(false);
    }
  };

  const handlePrediction = async (clienteId: string) => {
    setLoading(true);
    
    try {
      // Simula previsão
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newPrediction: ChurnPrediction = {
        cliente_id: clienteId,
        risk_level: Math.random() > 0.7 ? 'alto' : Math.random() > 0.4 ? 'medio' : 'baixo',
        risk_score: Math.random(),
        predictions: {
          'random_forest': Math.random(),
          'xgboost': Math.random(),
          'lightgbm': Math.random(),
          'neural_network': Math.random(),
          'ensemble': Math.random(),
        },
        features_importance: {
          'health_score_atual': Math.random(),
          'dias_vencimento_proximo': Math.random(),
          'csat_medio': Math.random(),
          'dias_ultima_interacao': Math.random(),
          'ltv_valor': Math.random(),
        },
        recommendations: [
          'Monitorar Health Score',
          'Verificar renovação de contrato',
          'Acompanhar satisfação do cliente',
        ],
        timestamp: new Date().toISOString(),
      };
      
      setPredictions(prev => [newPrediction, ...prev]);
      message.success('Previsão realizada com sucesso!');
      
    } catch (error) {
      message.error('Erro ao fazer previsão');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'baixo': return 'green';
      case 'medio': return 'orange';
      case 'alto': return 'red';
      case 'critico': return 'volcano';
      default: return 'default';
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
      render: (level: string) => (
        <Tag color={getRiskLevelColor(level)}>
          {level.toUpperCase()}
        </Tag>
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
      render: (predictions: Record<string, number>) => (
        <Text strong>{Math.round(predictions.ensemble * 100)}%</Text>
      ),
    },
    {
      title: 'Recomendações',
      dataIndex: 'recommendations',
      key: 'recommendations',
      render: (recommendations: string[]) => (
        <Space direction="vertical" size="small">
          {recommendations.slice(0, 2).map((rec, index) => (
            <Text key={index} type="secondary" style={{ fontSize: '12px' }}>
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
      render: (timestamp: string) => new Date(timestamp).toLocaleDateString('pt-BR'),
    },
  ];

  return (
    <div>
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
                <Text type="secondary">
                  Sistema inteligente para identificar clientes em risco de churn
                </Text>
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
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => window.location.reload()}
                  >
                    Atualizar
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Status dos Modelos */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Status dos Modelos"
              value={isTrained ? 'Treinados' : 'Não Treinados'}
              prefix={isTrained ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <ClockCircleOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: isTrained ? '#52c41a' : '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total de Previsões"
              value={predictions.length}
              prefix={<EyeOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Clientes de Alto Risco"
              value={insights?.clientes_risco_alto || 0}
              prefix={<AlertOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Taxa de Churn Atual"
              value={insights?.taxa_churn_atual || 0}
              suffix="%"
              precision={2}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Alertas */}
      {!isTrained && (
        <Row style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Alert
              message="Modelos não treinados"
              description="É necessário treinar os modelos de Machine Learning antes de fazer previsões. Clique em 'Treinar Modelos' para começar."
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

      {/* Conteúdo Principal */}
      <Tabs defaultActiveKey="prediction" size="large">
        <TabPane tab="Previsão Individual" key="prediction">
          <ChurnPredictionForm 
            onPrediction={handlePrediction}
            loading={loading}
            isTrained={isTrained}
          />
        </TabPane>
        
        <TabPane tab="Insights Gerais" key="insights">
          <ChurnInsights insights={insights} />
        </TabPane>
        
        <TabPane tab="Análise de Risco" key="risk">
          <ChurnRiskAnalysis />
        </TabPane>
        
        <TabPane tab="Histórico de Previsões" key="history">
          <Card title="Previsões Realizadas">
            <Table
              columns={columns}
              dataSource={predictions}
              rowKey="cliente_id"
              pagination={{ pageSize: 10 }}
              loading={loading}
            />
          </Card>
        </TabPane>
        
        <TabPane tab="Treinamento" key="training">
          <ModelTraining 
            status={trainingStatus}
            onTrain={handleTrainModels}
            loading={loading}
          />
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MLChurn; 