import React from 'react';
import { Card, Typography, Spin, Space, Button } from 'antd';

const { Title, Text } = Typography;

interface ModelTrainingProps {
  status: 'idle' | 'training' | 'completed';
  onTrain: () => void;
  loading: boolean;
}

const ModelTraining: React.FC<ModelTrainingProps> = ({ status, onTrain, loading }) => {
  return (
    <Card title="Treinamento do Modelo">
      <Space direction="vertical">
        <Text>Status do Treinamento: </Text>
        <Text strong>{status.charAt(0).toUpperCase() + status.slice(1)}</Text>
        {loading && <Spin size="small" />}
        {status !== 'training' && (
           <Button type="primary" onClick={onTrain} loading={loading}>
             {status === 'completed' ? 'Retreinar Modelo' : 'Iniciar Treinamento'}
           </Button>
        )}
      </Space>
    </Card>
  );
};

export default ModelTraining;