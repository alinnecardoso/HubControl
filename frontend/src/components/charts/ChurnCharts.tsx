// src/components/charts/ChurnCharts.tsx
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  ScatterChart,
  Scatter,
  Area,
  AreaChart,
} from 'recharts';
import { Card, Typography, Space, Row, Col, Progress } from 'antd';

const { Title, Text } = Typography;

interface ChurnChartsProps {
  riskDistribution?: {
    baixo: number;
    medio: number;
    alto: number;
    critico: number;
  };
  predictions?: Record<string, number>;
  featuresImportance?: Record<string, number>;
  trends?: Array<{
    month: string;
    churnRate: number;
    predictions: number;
    accuracy: number;
  }>;
}

// Cores para diferentes níveis de risco
const RISK_COLORS = {
  baixo: '#52c41a',
  medio: '#faad14',
  alto: '#ff7875',
  critico: '#ff4d4f',
};

const MODEL_COLORS = {
  random_forest: '#1890ff',
  xgboost: '#722ed1',
  lightgbm: '#13c2c2',
  neural_network: '#eb2f96',
  ensemble: '#f5222d',
};

export const RiskDistributionChart: React.FC<{ data: ChurnChartsProps['riskDistribution'] }> = ({
  data,
}) => {
  if (!data) return null;

  const chartData = Object.entries(data).map(([risk, count]) => ({
    name: risk.charAt(0).toUpperCase() + risk.slice(1),
    value: count,
    color: RISK_COLORS[risk as keyof typeof RISK_COLORS],
  }));

  const renderCustomLabel = (entry: any) => {
    const percent = ((entry.value / Object.values(data).reduce((a, b) => a + b, 0)) * 100).toFixed(1);
    return `${entry.name}: ${percent}%`;
  };

  return (
    <Card title="Distribuição de Risco" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
};

export const ModelPredictionsChart: React.FC<{ data: ChurnChartsProps['predictions'] }> = ({
  data,
}) => {
  if (!data) return null;

  const chartData = Object.entries(data)
    .filter(([model]) => model !== 'ensemble') // Ensemble será mostrado separadamente
    .map(([model, score]) => ({
      model: model.replace('_', ' ').toUpperCase(),
      score: Math.round(score * 100),
      fill: MODEL_COLORS[model as keyof typeof MODEL_COLORS] || '#666',
    }));

  return (
    <Card title="Predições por Modelo" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model" angle={-45} textAnchor="end" height={80} />
          <YAxis domain={[0, 100]} />
          <Tooltip formatter={(value) => [`${value}%`, 'Probabilidade de Churn']} />
          <Bar dataKey="score" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export const FeatureImportanceChart: React.FC<{ data: ChurnChartsProps['featuresImportance'] }> = ({
  data,
}) => {
  if (!data) return null;

  // Pega as top 8 features mais importantes
  const sortedFeatures = Object.entries(data)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)
    .map(([feature, importance]) => ({
      feature: feature
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (l) => l.toUpperCase()),
      importance: Math.round(importance * 100),
    }));

  return (
    <Card title="Importância das Features" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={sortedFeatures}
          layout="horizontal"
          margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 100]} />
          <YAxis type="category" dataKey="feature" width={90} />
          <Tooltip formatter={(value) => [`${value}%`, 'Importância']} />
          <Bar dataKey="importance" fill="#1890ff" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export const ChurnTrendChart: React.FC<{ data: ChurnChartsProps['trends'] }> = ({ data }) => {
  if (!data) return null;

  return (
    <Card title="Tendência de Churn" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis domain={[0, 100]} />
          <Tooltip formatter={(value) => [`${value}%`, '']} />
          <Line
            type="monotone"
            dataKey="churnRate"
            stroke="#ff4d4f"
            strokeWidth={3}
            name="Taxa de Churn Atual"
          />
          <Line
            type="monotone"
            dataKey="predictions"
            stroke="#1890ff"
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Predições ML"
          />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke="#52c41a"
            strokeWidth={2}
            name="Acurácia do Modelo"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export const RiskScoreGauge: React.FC<{ score: number; level: string }> = ({ score, level }) => {
  const data = [
    {
      name: 'Risk Score',
      value: Math.round(score * 100),
      fill: RISK_COLORS[level as keyof typeof RISK_COLORS] || '#666',
    },
  ];

  return (
    <Card title="Score de Risco" style={{ height: 300 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="60%"
            outerRadius="90%"
            data={data}
            startAngle={180}
            endAngle={0}
          >
            <RadialBar dataKey="value" cornerRadius={10} />
            <text
              x="50%"
              y="50%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="progress-label"
              style={{ fontSize: '24px', fontWeight: 'bold' }}
            >
              {Math.round(score * 100)}%
            </text>
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ textAlign: 'center', marginTop: 16 }}>
        <Text strong style={{ color: RISK_COLORS[level as keyof typeof RISK_COLORS] }}>
          Risco {level.charAt(0).toUpperCase() + level.slice(1)}
        </Text>
      </div>
    </Card>
  );
};

export const ModelAccuracyChart: React.FC<{
  models: Array<{ name: string; accuracy: number; auc: number }>;
}> = ({ models }) => {
  if (!models || models.length === 0) return null;

  const data = models.map((model) => ({
    model: model.name.replace('_', ' ').toUpperCase(),
    accuracy: Math.round(model.accuracy * 100),
    auc: Math.round(model.auc * 100),
  }));

  return (
    <Card title="Performance dos Modelos" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model" angle={-45} textAnchor="end" height={80} />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Bar dataKey="accuracy" fill="#1890ff" name="Acurácia" />
          <Bar dataKey="auc" fill="#52c41a" name="AUC" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export const ClientRiskScatter: React.FC<{
  clients: Array<{
    name: string;
    healthScore: number;
    riskScore: number;
    daysToExpiry: number;
  }>;
}> = ({ clients }) => {
  if (!clients || clients.length === 0) return null;

  const data = clients.map((client) => ({
    x: client.healthScore,
    y: Math.round(client.riskScore * 100),
    z: client.daysToExpiry,
    name: client.name,
  }));

  return (
    <Card title="Análise de Risco por Health Score" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid />
          <XAxis type="number" dataKey="x" name="Health Score" domain={[0, 100]} />
          <YAxis type="number" dataKey="y" name="Risk Score" domain={[0, 100]} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter name="Clientes" data={data} fill="#1890ff" />
        </ScatterChart>
      </ResponsiveContainer>
    </Card>
  );
};

// Componente principal que combina todos os gráficos
export const ChurnDashboard: React.FC<ChurnChartsProps> = ({
  riskDistribution,
  predictions,
  featuresImportance,
  trends,
}) => {
  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <RiskDistributionChart data={riskDistribution} />
        </Col>
        <Col span={12}>
          <ModelPredictionsChart data={predictions} />
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <FeatureImportanceChart data={featuresImportance} />
        </Col>
      </Row>
      
      {trends && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col span={24}>
            <ChurnTrendChart data={trends} />
          </Col>
        </Row>
      )}
    </div>
  );
};

export default ChurnDashboard;