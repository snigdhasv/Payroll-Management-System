// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import EmployeeDashboard from './pages/EmployeeDashboard';
import AdminDashboard from './pages/AdminDashboard';
import EmployeePage from './pages/Employee';
import PayrollList from './pages/PayrollList';
import LeavesList from './pages/LeavesList';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/employee_dashboard" element={<EmployeeDashboard/>} />
        <Route path="/admin_dashboard" element={<AdminDashboard/>} />
        <Route path="/employees" element={<EmployeePage />} />
        <Route path="/payroll" element={<PayrollList />} />
        <Route path="/leaves" element={<LeavesList/>} />
      </Routes>
    </Router>
  </React.StrictMode>
);
