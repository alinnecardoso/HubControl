import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Table, 
  Button, 
  Switch, 
  Space,
  Tag,
  Progress,
  List,
  Avatar,
  Typography,
  Divider,
  Alert,
  Tooltip,
  Badge,
  Tabs
} from 'antd';
import { 
  SettingOutlined, 
  UserOutlined, 
  DatabaseOutlined,
  SafetyCertificateOutlined,
  MonitorOutlined,
  BugOutlined,
  ApiOutlined,
  CloudServerOutlined,
  LockOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { Line, Gauge } from '@ant-design/plots';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface UsuarioSistema {
  id: number;
  nome: string;
  email: string;
  role: string;
  status: string;
  ultimo_acesso: string;
  total_acessos: number;
}

interface LogSistema {
  id: number;
  timestamp: string;
  nivel: string;
  origem: string;
  mensagem: string;
  usuario?: string;
}

interface MetricasSistema {
  usuarios_ativos: number;
  total_usuarios: number;
  uptime: number;
  uso_cpu: number;
  uso_memoria: number;
  total_requests: number;
  response_time: number;
  errors_rate: number;
}

const DashboardAdmin: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [metricas, setMetricas] = useState<MetricasSistema | null>(null);
  const [usuarios, setUsuarios] = useState<UsuarioSistema[]>([]);
  const [logs, setLogs] = useState<LogSistema[]>([]);

  // Dados mockados para demonstração
  const mockMetricas: MetricasSistema = {
    usuarios_ativos: 23,
    total_usuarios: 45,
    uptime: 99.8,
    uso_cpu: 45,
    uso_memoria: 62,
    total_requests: 1847,
    response_time: 180,
    errors_rate: 0.3
  };

  const mockUsuarios: UsuarioSistema[] = [
    {
      id: 1,
      nome: "Isaac Silva",
      email: "isaac@hubcontrol.com",
      role: "VENDAS",
      status: "ativo",
      ultimo_acesso: "2025-06-20T09:15:00",
      total_acessos: 342
    },
    {
      id: 2,
      nome: "Lucas Santos",
      email: "lucas@hubcontrol.com",
      role: "VENDAS",
      status: "ativo",
      ultimo_acesso: "2025-06-19T16:30:00",
      total_acessos: 198
    },
    {
      id: 3,
      nome: "Ana Costa",
      email: "ana@hubcontrol.com",
      role: "CS_CX",
      status: "inativo",
      ultimo_acesso: "2025-06-15T11:22:00",
      total_acessos: 89
    }
  ];

  const mockLogs: LogSistema[] = [
    {
      id: 1,
      timestamp: "2025-06-20T10:15:32",
      nivel: "ERROR",
      origem: "API",
      mensagem: "Falha na conexão com Supabase - timeout após 30s",
      usuario: "sistema"
    },
    {
      id: 2,
      timestamp: "2025-06-20T10:12:18",
      nivel: "WARN",
      origem: "AUTH",
      mensagem: "Tentativa de login com credenciais inválidas",
      usuario: "isaac@hubcontrol.com"
    },
    {
      id: 3,
      timestamp: "2025-06-20T10:08:45",
      nivel: "INFO",
      origem: "SYSTEM",
      mensagem: "Backup automático executado com sucesso",
      usuario: "sistema"
    },
    {
      id: 4,
      timestamp: "2025-06-20T09:55:12",
      nivel: "ERROR",
      origem: "ML",
      mensagem: "Modelo de churn prediction falhou - dados insuficientes",
      usuario: "sistema"
    }
  ];

  useEffect(() => {
    carregarDados();
    const interval = setInterval(carregarDados, 30000); // Atualiza a cada 30s
    return () => clearInterval(interval);
  }, []);

  const carregarDados = async () => {
    setLoading(true);
    try {
      // Em produção, chamadas reais para API
      setTimeout(() => {
        setMetricas(mockMetricas);
        setUsuarios(mockUsuarios);
        setLogs(mockLogs);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setLoading(false);
    }
  };

  const colunasUsuarios: ColumnsType<UsuarioSistema> = [
    {
      title: 'Usuário',
      key: 'usuario',
      render: (_, record) => (
        <div>
          <div><Text strong>{record.nome}</Text></div>
          <div><Text type="secondary">{record.email}</Text></div>
        </div>
      )
    },
    {
      title: 'Função',
      dataIndex: 'role',
      key: 'role',
      render: (role) => {
        const roleColors: Record<string, string> = {
          'ADMIN': 'red',
          'VENDAS': 'blue',
          'CS_CX': 'green',
          'DIRETORIA': 'purple'
        };
        return <Tag color={roleColors[role] || 'default'}>{role}</Tag>;
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Badge 
          status={status === 'ativo' ? 'success' : 'default'} 
          text={status === 'ativo' ? 'Ativo' : 'Inativo'} 
        />
      )
    },
    {
      title: 'Último Acesso',
      dataIndex: 'ultimo_acesso',
      key: 'ultimo_acesso',
      render: (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
        return (
          <div>
            <div>{date.toLocaleDateString('pt-BR')}</div>
            <Text type="secondary">há {diffHours}h</Text>
          </div>
        );
      }
    },
    {
      title: 'Total Acessos',
      dataIndex: 'total_acessos',
      key: 'total_acessos',
      sorter: (a, b) => a.total_acessos - b.total_acessos
    },
    {
      title: 'Ações',
      key: 'acoes',
      render: (_, record) => (
        <Space>
          <Button size="small">Editar</Button>
          <Button size="small" danger={record.status === 'ativo'} type="link">
            {record.status === 'ativo' ? 'Desativar' : 'Ativar'}
          </Button>
        </Space>
      )
    }
  ];

  const colunasLogs: ColumnsType<LogSistema> = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 120,
      render: (timestamp) => new Date(timestamp).toLocaleTimeString('pt-BR')
    },
    {
      title: 'Nível',
      dataIndex: 'nivel',
      key: 'nivel',
      width: 80,
      render: (nivel) => {
        const colors: Record<string, string> = {
          'ERROR': 'red',
          'WARN': 'orange',
          'INFO': 'blue'
        };
        return <Tag color={colors[nivel]}>{nivel}</Tag>;
      }
    },
    {
      title: 'Origem',
      dataIndex: 'origem',
      key: 'origem',
      width: 80
    },
    {
      title: 'Mensagem',
      dataIndex: 'mensagem',
      key: 'mensagem'
    },
    {
      title: 'Usuário',
      dataIndex: 'usuario',
      key: 'usuario',
      width: 120
    }
  ];

  const dadosPerformance = [
    { time: '09:00', cpu: 35, memoria: 58, requests: 120 },
    { time: '09:30', cpu: 42, memoria: 61, requests: 145 },
    { time: '10:00', cpu: 45, memoria: 62, requests: 180 },
    { time: '10:30', cpu: 48, memoria: 64, requests: 165 },
    { time: '11:00', cpu: 52, memoria: 67, requests: 190 },
  ];

  const configPerformance = {
    data: dadosPerformance,
    xField: 'time',
    yField: 'cpu',
    smooth: true,
    color: '#1890ff',
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <SettingOutlined /> Dashboard Administrativo
        </Title>
        <Text type="secondary">
          Monitoramento e gestão do sistema HubControl
        </Text>
      </div>

      <Tabs defaultActiveKey="sistema" type="card">
        {/* Tab Sistema */}
        <TabPane tab="Sistema" key="sistema">
          {/* Métricas de Sistema */}
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Uptime"
                  value={metricas?.uptime || 0}
                  precision={1}
                  suffix="%"
                  prefix={<MonitorOutlined />}
                  valueStyle={{ color: metricas && metricas.uptime >= 99 ? '#52c41a' : '#f5222d' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Requests/h"
                  value={metricas?.total_requests || 0}
                  prefix={<ApiOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Tempo Resposta"
                  value={metricas?.response_time || 0}
                  suffix="ms"
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{ color: metricas && metricas.response_time < 200 ? '#52c41a' : '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Taxa de Erro"
                  value={metricas?.errors_rate || 0}
                  precision={1}
                  suffix="%"
                  prefix={<BugOutlined />}
                  valueStyle={{ color: metricas && metricas.errors_rate < 1 ? '#52c41a' : '#f5222d' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Recursos do Sistema */}
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={24} lg={8}>
              <Card title="CPU Usage">
                <Gauge
                  percent={metricas ? metricas.uso_cpu / 100 : 0}
                  color={['#30BF78', '#FAAD14', '#F4664A']}
                  height={160}
                  statistic={{
                    content: {
                      style: {
                        fontSize: '16px',
                        lineHeight: '16px',
                      },
                      formatter: () => `${metricas?.uso_cpu || 0}%`,
                    },
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title="Memória">
                <Gauge
                  percent={metricas ? metricas.uso_memoria / 100 : 0}
                  color={['#30BF78', '#FAAD14', '#F4664A']}
                  height={160}
                  statistic={{
                    content: {
                      style: {
                        fontSize: '16px',
                        lineHeight: '16px',
                      },
                      formatter: () => `${metricas?.uso_memoria || 0}%`,
                    },
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title="Serviços">
                <List
                  size="small"
                  dataSource={[
                    { nome: 'API Gateway', status: 'online', cor: 'success' },
                    { nome: 'Database', status: 'online', cor: 'success' },
                    { nome: 'Redis Cache', status: 'online', cor: 'success' },
                    { nome: 'ML Service', status: 'warning', cor: 'warning' },
                    { nome: 'Email Service', status: 'offline', cor: 'error' }
                  ]}
                  renderItem={(item) => (
                    <List.Item>
                      <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Text>{item.nome}</Text>
                        <Badge status={item.cor as any} text={item.status} />
                      </Space>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          </Row>

          {/* Performance Chart */}
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col span={24}>
              <Card title="Performance em Tempo Real" loading={loading}>
                <Line {...configPerformance} height={200} />
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* Tab Usuários */}
        <TabPane tab="Usuários" key="usuarios">
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Usuários Ativos"
                  value={metricas?.usuarios_ativos || 0}
                  prefix={<UserOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Total de Usuários"
                  value={metricas?.total_usuarios || 0}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Taxa de Atividade"
                  value={metricas ? Math.round((metricas.usuarios_ativos / metricas.total_usuarios) * 100) : 0}
                  suffix="%"
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Button type="primary" icon={<UserOutlined />}>
                  Novo Usuário
                </Button>
              </Card>
            </Col>
          </Row>

          <Card title="Gestão de Usuários" loading={loading}>
            <Table
              columns={colunasUsuarios}
              dataSource={usuarios}
              rowKey="id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
              }}
            />
          </Card>
        </TabPane>

        {/* Tab Logs */}
        <TabPane tab="Logs" key="logs">
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col xs={24} sm={8}>
              <Alert
                message="4 Erros"
                description="Nas últimas 2 horas"
                type="error"
                showIcon
                action={
                  <Button size="small" danger>
                    Ver Detalhes
                  </Button>
                }
              />
            </Col>
            <Col xs={24} sm={8}>
              <Alert
                message="12 Warnings"
                description="Nas últimas 24 horas"
                type="warning"
                showIcon
                action={
                  <Button size="small">
                    Revisar
                  </Button>
                }
              />
            </Col>
            <Col xs={24} sm={8}>
              <Alert
                message="Sistema Estável"
                description="Monitoramento ativo"
                type="success"
                showIcon
              />
            </Col>
          </Row>

          <Card title="Log de Sistema" loading={loading}>
            <Table
              columns={colunasLogs}
              dataSource={logs}
              rowKey="id"
              pagination={{
                pageSize: 15,
                showSizeChanger: true,
              }}
              size="small"
              rowClassName={(record) => {
                if (record.nivel === 'ERROR') return 'log-error';
                if (record.nivel === 'WARN') return 'log-warning';
                return '';
              }}
            />
          </Card>
        </TabPane>

        {/* Tab Configurações */}
        <TabPane tab="Configurações" key="configuracoes">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="Configurações Gerais">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>Modo de Manutenção</Text>
                      <br />
                      <Text type="secondary">Desabilita acesso dos usuários</Text>
                    </div>
                    <Switch />
                  </div>
                  
                  <Divider />
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>Backup Automático</Text>
                      <br />
                      <Text type="secondary">Backup diário às 02:00</Text>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <Divider />
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>Logs Detalhados</Text>
                      <br />
                      <Text type="secondary">Registra todas as ações</Text>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <Divider />
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>Notificações por Email</Text>
                      <br />
                      <Text type="secondary">Alertas para administradores</Text>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </Space>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="Ações do Sistema">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button 
                    icon={<DatabaseOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                  >
                    Executar Backup Manual
                  </Button>
                  
                  <Button 
                    icon={<SyncOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                  >
                    Sincronizar Dados
                  </Button>
                  
                  <Button 
                    icon={<FileTextOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                  >
                    Gerar Relatório Sistema
                  </Button>
                  
                  <Button 
                    icon={<SafetyCertificateOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                  >
                    Verificar Segurança
                  </Button>
                  
                  <Divider />
                  
                  <Button 
                    danger 
                    icon={<WarningOutlined />} 
                    style={{ width: '100%', textAlign: 'left' }}
                  >
                    Reiniciar Sistema
                  </Button>
                </Space>
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>

      <style>{`
        .log-error {
          background-color: #fff2f0;
        }
        .log-warning {
          background-color: #fff7e6;
        }
      `}</style>
    </div>
  );
};

export default DashboardAdmin;