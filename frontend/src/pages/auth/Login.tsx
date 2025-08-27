import React from 'react';
import { Form, Input, Button, Card, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';

const { Title } = Typography;

const Login: React.FC = () => {
  const onFinish = (values: any) => {
    console.log('Login values:', values);
  };

  return (
    <Card>
      <Title level={2} style={{ textAlign: 'center', marginBottom: '24px' }}>
        HubControl
      </Title>
      <Form
        name="login"
        onFinish={onFinish}
        autoComplete="off"
        layout="vertical"
      >
        <Form.Item
          name="email"
          rules={[{ required: true, message: 'Por favor, insira seu email!' }]}
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="Email" 
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[{ required: true, message: 'Por favor, insira sua senha!' }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Senha"
            size="large"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" size="large" block>
            Entrar
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default Login; 