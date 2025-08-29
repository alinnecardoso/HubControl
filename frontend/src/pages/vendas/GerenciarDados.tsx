import React, { useState, useEffect } from 'react';
import {
  Card, Table, Button, Space, Upload, message, Modal, Form,
  Input, Select, Tag, Tooltip, Popconfirm, Drawer, Typography,
  Row, Col, Statistic, Progress, Alert
} from 'antd';
import {
  UploadOutlined, DownloadOutlined, PlusOutlined,
  EditOutlined, DeleteOutlined, EyeOutlined, ReloadOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import { salesService, Cliente, MetricasVendas, ImportResult } from '../../services/salesService';

const { Title, Text } = Typography;
const { Option } = Select;

interface GerenciarDadosProps {}

const GerenciarDados: React.FC<GerenciarDadosProps> = () => {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [metricas, setMetricas] = useState<MetricasVendas | null>(null);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedCliente, setSelectedCliente] = useState<Cliente | null>(null);
  const [filtros, setFiltros] = useState({
    status: '',
    search: ''
  });
  const [importProgress, setImportProgress] = useState<ImportResult | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    carregarDados();
    carregarMetricas();
  }, [filtros]);

  const carregarDados = async () => {
    setLoading(true);
    try {
      const clientesData = await salesService.listarClientes({
        limit: 100,
        ...filtros
      });
      setClientes(clientesData);
    } catch (error: any) {
      message.error('Erro ao carregar dados: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const carregarMetricas = async () => {
    try {
      const metricasData = await salesService.obterMetricas();
      setMetricas(metricasData);
    } catch (error: any) {
      message.error('Erro ao carregar métricas: ' + error.message);
    }
  };

  const handleImport = async (file: File) => {
    setLoading(true);
    try {
      const result = await salesService.importarPlanilha(file);
      setImportProgress(result);
      
      if (result.success) {
        message.success(`Importação concluída! ${result.success_rows} linhas importadas com sucesso.`);
        carregarDados();
        carregarMetricas();
      } else {
        message.warning(`Importação com erros. ${result.success_rows} sucessos, ${result.error_rows} erros.`);
      }
    } catch (error: any) {
      message.error('Erro na importação: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await salesService.exportarPlanilha(filtros);
      salesService.downloadArquivo(blob, 'clientes_export.xlsx');
      message.success('Exportação realizada com sucesso!');
    } catch (error: any) {
      message.error('Erro na exportação: ' + error.message);
    }
  };

  const handleSave = async (values: any) => {
    try {
      if (selectedCliente?.id) {
        await salesService.atualizarCliente(selectedCliente.id, values);
        message.success('Cliente atualizado com sucesso!');
      } else {
        await salesService.criarCliente(values);
        message.success('Cliente criado com sucesso!');
      }
      
      setModalVisible(false);
      setSelectedCliente(null);
      form.resetFields();
      carregarDados();
      carregarMetricas();
    } catch (error: any) {
      message.error('Erro ao salvar: ' + error.message);
    }
  };

  const handleDelete = async (clienteId: number) => {
    try {
      await salesService.deletarCliente(clienteId);
      message.success('Cliente deletado com sucesso!');
      carregarDados();
      carregarMetricas();
    } catch (error: any) {
      message.error('Erro ao deletar: ' + error.message);
    }
  };

  const openEditModal = (cliente?: Cliente) => {
    setSelectedCliente(cliente || null);
    if (cliente) {
      form.setFieldsValue(cliente);
    } else {
      form.resetFields();
    }
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'CustId',
      dataIndex: 'cust_id',
      key: 'cust_id',
      width: 120,
    },
    {
      title: 'Nickname',
      dataIndex: 'nickname',
      key: 'nickname',
      width: 150,
      render: (text: string) => <strong>{text}</strong>
    },
    {
      title: 'Nome Principal',
      dataIndex: 'nome_principal',
      key: 'nome_principal',
      width: 200,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={salesService.obterStatusColor(status)}>
          {status}
        </Tag>
      )
    },
    {
      title: 'LTV',
      dataIndex: 'ltv_valor',
      key: 'ltv_valor',
      width: 100,
      render: (valor: number) => valor ? salesService.formatarMoeda(valor) : '-'
    },
    {
      title: 'Data Início',
      dataIndex: 'data_inicio',
      key: 'data_inicio',
      width: 120,
      render: (data: string) => data ? salesService.formatarData(data) : '-'
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 150,
      render: (_: any, record: Cliente) => (
        <Space>
          <Tooltip title="Visualizar">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => {
                setSelectedCliente(record);
                setDrawerVisible(true);
              }}
            />
          </Tooltip>
          <Tooltip title="Editar">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Tem certeza que deseja deletar?"
            onConfirm={() => record.id && handleDelete(record.id)}
            okText="Sim"
            cancelText="Não"
          >
            <Tooltip title="Deletar">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2} style={{ marginBottom: '24px', color: 'var(--text-primary)' }}>
        <DatabaseOutlined /> Importar/Exportar Dados
      </Title>

      {/* Métricas */}
      {metricas && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Total de Clientes"
                value={metricas.total_clientes}
                prefix={<EyeOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Clientes Ativos"
                value={metricas.clientes_ativos}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Receita Recorrente"
                value={metricas.receita_recorrente}
                formatter={(value) => salesService.formatarMoeda(Number(value))}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Taxa de Churn"
                value={metricas.taxa_churn}
                precision={1}
                suffix="%"
                valueStyle={{ color: metricas.taxa_churn > 5 ? '#cf1322' : '#3f8600' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Progress da Importação */}
      {importProgress && (
        <Alert
          message="Resultado da Importação"
          description={
            <div>
              <Progress 
                percent={Math.round((importProgress.success_rows / importProgress.total_rows) * 100)}
                status={importProgress.error_rows > 0 ? 'exception' : 'success'}
              />
              <Text>
                Total: {importProgress.total_rows} | 
                Sucessos: {importProgress.success_rows} | 
                Erros: {importProgress.error_rows}
              </Text>
              {importProgress.errors.length > 0 && (
                <details style={{ marginTop: '8px' }}>
                  <summary>Ver erros</summary>
                  <ul>
                    {importProgress.errors.slice(0, 10).map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          }
          type={importProgress.error_rows > 0 ? "warning" : "success"}
          closable
          onClose={() => setImportProgress(null)}
          style={{ marginBottom: '16px' }}
        />
      )}

      <Card>
        {/* Barra de Ferramentas */}
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <Space wrap>
            <Input.Search
              placeholder="Buscar por nickname, nome ou CustId"
              value={filtros.search}
              onChange={(e) => setFiltros(prev => ({ ...prev, search: e.target.value }))}
              style={{ width: 300 }}
            />
            <Select
              placeholder="Filtrar por status"
              value={filtros.status}
              onChange={(value) => setFiltros(prev => ({ ...prev, status: value }))}
              style={{ width: 150 }}
              allowClear
            >
              <Option value="Ativo ML">Ativo ML</Option>
              <Option value="Ativo">Ativo</Option>
              <Option value="Churn">Churn</Option>
              <Option value="Pausado">Pausado</Option>
              <Option value="Não é MAIS cliente">Não é MAIS cliente</Option>
            </Select>
          </Space>

          <Space wrap>
            <Button
              icon={<ReloadOutlined />}
              onClick={carregarDados}
              loading={loading}
            >
              Atualizar
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openEditModal()}
            >
              Novo Cliente
            </Button>
            <Upload
              accept=".xlsx,.xls,.csv"
              beforeUpload={(file) => {
                handleImport(file);
                return false;
              }}
              showUploadList={false}
            >
              <Button icon={<UploadOutlined />} loading={loading}>
                Importar Planilha
              </Button>
            </Upload>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              Exportar Dados
            </Button>
          </Space>
        </div>

        {/* Tabela */}
        <Table
          columns={columns}
          dataSource={clientes}
          rowKey="id"
          loading={loading}
          pagination={{
            total: clientes.length,
            pageSize: 50,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} itens`,
          }}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* Modal de Edição */}
      <Modal
        title={selectedCliente ? 'Editar Cliente' : 'Novo Cliente'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false);
          setSelectedCliente(null);
          form.resetFields();
        }}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="cust_id" label="CustId">
                <Input placeholder="ID do cliente" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                name="nickname" 
                label="Nickname"
                rules={[{ required: true, message: 'Nickname é obrigatório' }]}
              >
                <Input placeholder="Nome da loja/conta" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="nome_principal" label="Nome Principal">
            <Input placeholder="Nome principal do cliente" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="status" 
                label="Status"
                rules={[{ required: true, message: 'Status é obrigatório' }]}
              >
                <Select placeholder="Selecione o status">
                  <Option value="Ativo ML">Ativo ML</Option>
                  <Option value="Ativo">Ativo</Option>
                  <Option value="Churn">Churn</Option>
                  <Option value="Pausado">Pausado</Option>
                  <Option value="Não é MAIS cliente">Não é MAIS cliente</Option>
                  <Option value="Novo Cliente">Novo Cliente</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="tempo_ativo" label="Tempo Ativo (meses)">
                <Input type="number" placeholder="Tempo em meses" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="data_inicio" label="Data de Início">
                <Input type="date" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="jornada_iniciada" label="Jornada Iniciada">
                <Input type="date" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="ltv_meses" label="LTV (meses)">
                <Input type="number" placeholder="Lifetime Value em meses" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="ltv_valor" label="LTV (valor)">
                <Input type="number" placeholder="Valor em reais" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="observacoes" label="Observações">
            <Input.TextArea rows={3} placeholder="Observações adicionais" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Drawer de Visualização */}
      <Drawer
        title="Detalhes do Cliente"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={400}
      >
        {selectedCliente && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>CustId: </Text>
              <Text>{selectedCliente.cust_id || '-'}</Text>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Nickname: </Text>
              <Text>{selectedCliente.nickname}</Text>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Nome Principal: </Text>
              <Text>{selectedCliente.nome_principal || '-'}</Text>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Status: </Text>
              <Tag color={salesService.obterStatusColor(selectedCliente.status)}>
                {selectedCliente.status}
              </Tag>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Tempo Ativo: </Text>
              <Text>{selectedCliente.tempo_ativo || '-'} meses</Text>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>LTV: </Text>
              <Text>
                {selectedCliente.ltv_meses || '-'} meses | {' '}
                {selectedCliente.ltv_valor ? salesService.formatarMoeda(selectedCliente.ltv_valor) : '-'}
              </Text>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Data de Início: </Text>
              <Text>
                {selectedCliente.data_inicio ? salesService.formatarData(selectedCliente.data_inicio) : '-'}
              </Text>
            </div>
            {selectedCliente.observacoes && (
              <div style={{ marginBottom: '16px' }}>
                <Text strong>Observações: </Text>
                <Text>{selectedCliente.observacoes}</Text>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default GerenciarDados;