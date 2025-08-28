import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Tag,
  Space,
  Typography
} from 'antd';
import {
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  MailOutlined,
  LockOutlined
} from '@ant-design/icons';
import { authService, User, SignUpData } from '../../services/authService';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;
const { Option } = Select;

interface CreateUserFormData extends SignUpData {
  confirmPassword: string;
}

const Usuarios: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  const roles = [
    { value: 'admin', label: 'Administrador', color: 'red' },
    { value: 'diretoria', label: 'Diretoria', color: 'purple' },
    { value: 'cs_cx', label: 'CS/CX', color: 'blue' },
    { value: 'financeiro', label: 'Financeiro', color: 'green' },
    { value: 'vendas', label: 'Vendas', color: 'orange' },
    { value: 'dataops', label: 'DataOps', color: 'cyan' }
  ];

  // Carregar usuários
  const loadUsers = async () => {
    setLoading(true);
    try {
      const usersList = await authService.listUsers();
      setUsers(usersList);
    } catch (error: any) {
      message.error('Erro ao carregar usuários: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // Criar ou atualizar usuário
  const handleSubmit = async (values: CreateUserFormData) => {
    try {
      if (editingUser) {
        // Atualizar papel do usuário existente
        await authService.updateUserRole(editingUser.id, values.role || 'cs_cx');
        message.success('Usuário atualizado com sucesso!');
      } else {
        // Criar novo usuário
        const { confirmPassword, ...userData } = values;
        await authService.signUp(userData);
        message.success('Usuário criado com sucesso!');
      }
      
      setModalVisible(false);
      setEditingUser(null);
      form.resetFields();
      loadUsers();
    } catch (error: any) {
      message.error('Erro ao salvar usuário: ' + error.message);
    }
  };

  // Desativar usuário
  const handleDeactivateUser = async (userId: string) => {
    try {
      await authService.deactivateUser(userId);
      message.success('Usuário desativado com sucesso!');
      loadUsers();
    } catch (error: any) {
      message.error('Erro ao desativar usuário: ' + error.message);
    }
  };

  // Abrir modal para criação
  const handleCreate = () => {
    setEditingUser(null);
    setModalVisible(true);
    form.resetFields();
  };

  // Abrir modal para edição
  const handleEdit = (user: User) => {
    setEditingUser(user);
    setModalVisible(true);
    form.setFieldsValue({
      full_name: user.full_name,
      email: user.email,
      role: user.role
    });
  };

  // Obter cor da tag baseada no papel
  const getRoleColor = (role: string): string => {
    const roleInfo = roles.find(r => r.value === role);
    return roleInfo?.color || 'default';
  };

  // Obter nome amigável do papel
  const getRoleLabel = (role: string): string => {
    const roleInfo = roles.find(r => r.value === role);
    return roleInfo?.label || role;
  };

  const columns: ColumnsType<User> = [
    {
      title: 'Nome',
      dataIndex: 'full_name',
      key: 'full_name',
      sorter: (a, b) => a.full_name.localeCompare(b.full_name),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      sorter: (a, b) => a.email.localeCompare(b.email),
    },
    {
      title: 'Papel',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={getRoleColor(role)}>
          {getRoleLabel(role)}
        </Tag>
      ),
      filters: roles.map(role => ({
        text: role.label,
        value: role.value
      })),
      onFilter: (value: any, record: User) => record.role === value,
    },
    {
      title: 'Módulos de Acesso',
      key: 'modules',
      render: (_, record: User) => (
        <div style={{ maxWidth: 200 }}>
          {record.permissions.modules.map((module: string) => (
            <Tag key={module} style={{ margin: '1px', fontSize: '11px' }}>
              {module}
            </Tag>
          ))}
        </div>
      ),
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 150,
      render: (_, record: User) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          />
          <Popconfirm
            title="Desativar usuário"
            description="Tem certeza que deseja desativar este usuário?"
            onConfirm={() => handleDeactivateUser(record.id)}
            okText="Sim"
            cancelText="Não"
          >
            <Button
              type="text"
              icon={<DeleteOutlined />}
              danger
              size="small"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={2} style={{ margin: 0, color: '#E6E8EA' }}>
            Gerenciamento de Usuários
          </Title>
          <Button
            type="primary"
            icon={<UserAddOutlined />}
            onClick={handleCreate}
          >
            Novo Usuário
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} de ${total} usuários`
          }}
        />
      </Card>

      <Modal
        title={editingUser ? 'Editar Usuário' : 'Criar Novo Usuário'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingUser(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          size="large"
        >
          <Form.Item
            name="full_name"
            label="Nome Completo"
            rules={[
              { required: true, message: 'Nome completo é obrigatório!' },
              { min: 2, message: 'Nome deve ter pelo menos 2 caracteres!' }
            ]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="Nome completo do usuário"
            />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Email é obrigatório!' },
              { type: 'email', message: 'Email inválido!' }
            ]}
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="email@empresa.com"
              disabled={!!editingUser}
            />
          </Form.Item>

          <Form.Item
            name="role"
            label="Papel/Função"
            rules={[{ required: true, message: 'Selecione um papel!' }]}
          >
            <Select placeholder="Selecione o papel do usuário">
              {roles.map(role => (
                <Option key={role.value} value={role.value}>
                  <Tag color={role.color} style={{ marginRight: 8 }}>
                    {role.label}
                  </Tag>
                </Option>
              ))}
            </Select>
          </Form.Item>

          {!editingUser && (
            <>
              <Form.Item
                name="password"
                label="Senha"
                rules={[
                  { required: true, message: 'Senha é obrigatória!' },
                  { min: 6, message: 'Senha deve ter pelo menos 6 caracteres!' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="Senha do usuário"
                />
              </Form.Item>

              <Form.Item
                name="confirmPassword"
                label="Confirmar Senha"
                dependencies={['password']}
                rules={[
                  { required: true, message: 'Confirmação de senha é obrigatória!' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('As senhas não conferem!'));
                    },
                  }),
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="Confirme a senha"
                />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default Usuarios; 