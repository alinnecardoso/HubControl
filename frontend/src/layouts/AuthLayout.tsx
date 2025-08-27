import React from 'react';
import { Layout, Row, Col } from 'antd';
import { Outlet } from 'react-router-dom';

const { Content } = Layout;

const AuthLayout: React.FC = () => {
  return (
    <Layout className="min-h-screen flex justify-center items-center bg-gradient-to-br from-blue-200 via-purple-200 to-pink-200">
      <Content style={{ padding: '24px', width: '100%' }}>
        <Row justify="center">
          <Col
            xs={{ span: 24 }}
            sm={{ span: 24 }}
            md={{ span: 12 }}
            lg={{ span: 8 }}
            xl={{ span: 6 }}
            style={{
              background: 'white',
              padding: '32px',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <Outlet />
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default AuthLayout; 