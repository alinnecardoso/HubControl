import React from 'react';
import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';

const { Content } = Layout;

const AuthLayout: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh'}}>
      <Content style={{ padding: '24px' }}>
        <div style={{ 
          maxWidth: '600px', 
          margin: '0 auto',  
          padding: '32px',
          borderRadius: '8px',
        }}>
          <Outlet />
        </div>
      </Content>
    </Layout>
  );
};

export default AuthLayout; 