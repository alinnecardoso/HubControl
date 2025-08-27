import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  Typography,
  Alert,
  Divider,
  Row,
  Col,
  Statistic,
  Progress,
  Tag,
  List,
} from 'antd';
import {
  SearchOutlined,
  RobotOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface ChurnPredictionFormProps {
  onPrediction: (clienteId: string) => Promise<void>;
  loading: boolean;
  isTrained: boolean;
}

export const ChurnPredictionForm: React.FC<ChurnPredictionFormProps> = ({
  onPrediction,
  loading,
  isTrained,
}) => {
  const [form] = Form.useForm();
  const [predictionResult, setPredictionResult] = useState<any>(null);

  const handleSubmit = async (values: { cliente_id: string }) => {
    try {
      await onPrediction(values.cliente_id);
      // Simula resultado da previsão
      setPredictionResult({
        cliente_id: values.cliente_id,
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
          'Monitorar Health Score regularmente',
          'Verificar renovação de contrato nos próximos 30 dias',
          'Acompanhar satisfação do cliente via CSAT',
          'Agendar follow-up para próxima semana',
        ],
      });
    } catch (error) {
      console.error('Erro na previsão:', error);
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

  const getRiskLevelIcon = (level: string) => {
    switch (level) {
      case 'baixo': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'medio': return <InfoCircleOutlined style={{ color: '#faad14' }} />;
      case 'alto': return <AlertOutlined style={{ color: '#ff4d4f' }} />;
      case 'critico': return <AlertOutlined style={{ color: '#d32029' }} />;
      default: return <InfoCircleOutlined />;
    }
  };

  return (
    <div>
      <Card title="Previsão de Churn - Cliente Individual">
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          disabled={!isTrained || loading}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="cliente_id"
                label="ID do Cliente"
                rules={[
                  { required: true, message: 'Por favor, insira o ID do cliente' },
                ]}
              >
                <Input
                  placeholder="Ex: CL001"
                  prefix={<SearchOutlined />}
                  size="large"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label=" " style={{ marginBottom: 0 }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<RobotOutlined />}
                  size="large"
                  block
                >
                  {loading ? 'Analisando...' : 'Analisar Cliente'}
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>

        {!isTrained && (
          <Alert
            message="Modelos não treinados"
            description="É necessário treinar os modelos antes de fazer previsões."
            type="warning"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>

      {/* Resultado da Previsão */}
      {predictionResult && (
        <Card 
          title="Resultado da Análise" 
          style={{ marginTop: 16 }}
          extra={
            <Tag color={getRiskLevelColor(predictionResult.risk_level)} size="large">
              {predictionResult.risk_level.toUpperCase()}
            </Tag>
          }
        >
          <Row gutter={[24, 16]}>
            <Col span={8}>
              <Statistic
                title="Score de Risco"
                value={Math.round(predictionResult.risk_score * 100)}
                suffix="%"
                valueStyle={{ 
                  color: predictionResult.risk_score > 0.7 ? '#ff4d4f' : 
                         predictionResult.risk_score > 0.4 ? '#faad14' : '#52c41a' 
                }}
              />
              <Progress
                percent={Math.round(predictionResult.risk_score * 100)}
                status={predictionResult.risk_score > 0.7 ? 'exception' : 'normal'}
                style={{ marginTop: 8 }}
              />
            </Col>
            
            <Col span={8}>
              <Statistic
                title="Previsão Ensemble"
                value={Math.round(predictionResult.predictions.ensemble * 100)}
                suffix="%"
                prefix={getRiskLevelIcon(predictionResult.risk_level)}
              />
            </Col>
            
            <Col span={8}>
              <Statistic
                title="Confiança"
                value={Math.round((1 - Math.abs(predictionResult.predictions.ensemble - predictionResult.predictions.random_forest)) * 100)}
                suffix="%"
              />
            </Col>
          </Row>

          <Divider />

          {/* Previsões dos Modelos Individuais */}
          <Title level={5}>Previsões por Modelo</Title>
          <Row gutter={[16, 16]}>
            {Object.entries(predictionResult.predictions).map(([model, score]) => (
              <Col span={4} key={model}>
                <Card size="small">
                  <Statistic
                    title={model.replace('_', ' ').toUpperCase()}
                    value={Math.round(Number(score) * 100)}
                    suffix="%"
                    valueStyle={{ fontSize: '16px' }}
                  />
                </Card>
              </Col>
            ))}
          </Row>

          <Divider />

          {/* Importância das Features */}
          <Title level={5}>Fatores de Influência</Title>
          <Row gutter={[16, 16]}>
            {Object.entries(predictionResult.features_importance)
              .sort(([,a], [,b]) => Number(b) - Number(a))
              .slice(0, 5)
              .map(([feature, importance]) => (
                <Col span={8} key={feature}>
                  <Card size="small">
                    <Statistic
                      title={feature.replace(/_/g, ' ').toUpperCase()}
                      value={Math.round(Number(importance) * 100)}
                      suffix="%"
                      valueStyle={{ fontSize: '14px' }}
                    />
                  </Card>
                </Col>
              ))}
          </Row>

          <Divider />

          {/* Recomendações */}
          <Title level={5}>Recomendações de Ação</Title>
          <List
            dataSource={predictionResult.recommendations}
            renderItem={(item, index) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<AlertOutlined style={{ color: '#1890ff' }} />}
                  title={`Ação ${index + 1}`}
                  description={item}
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
}; 