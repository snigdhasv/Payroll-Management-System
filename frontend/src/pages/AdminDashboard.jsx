// src/components/AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import axios from 'axios';
import styles from '../styles/AdminDashboard.module.css';
import Sidebar from './Sidebar';
import totalEmployeesIcon from '../assets/totalEmployees.png';
import pendingLeavesIcon from '../assets/pendingLeaves.png';
import salaryIcon from '../assets/salary.png';
import bonusIcon from '../assets/bonus.png';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Tooltip
} from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip);

const AdminDashboard = () => {
  const [data, setData] = useState({
    totalEmployees: 0,
    avgSalary: 0,
    payrollExpenses: [],
    departmentData: {},
    turnoverRate: 0,
    employeeGrowth: [],
    departmentPayrollData: {},
    highestSalaryEmployees: [],
    bonusesIncentivesPaid: 0,
    pendingLeaves: 0
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/admin/dashboard');
        setData(response.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    fetchDashboardData();
  }, []);
  
  const departmentPayrollData = {
    labels: Object.keys(data.departmentPayrollData),
    datasets: [
      {
        label: 'Payroll by Department',
        data: Object.values(data.departmentPayrollData),
        backgroundColor: ['#55A8CB', '#FF6392', '#FFE45E', '#741C79', '#FF5647'],
      },
    ],
  };
  
   // Configuration for Payroll Expenses Data
   const payrollData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Payroll Expenses',
        data: data.payrollExpenses,
        backgroundColor: 'rgba(85, 168, 203, 0.2)', // Light fill for area chart
        borderColor: '#55A8CB',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Configuration for Employee Growth Data
  const employeeGrowthData = {
    labels: data.employeeGrowth.map(item => `${item.year}-${item.month}`),
    datasets: [
      {
        label: 'New Hires per Month',
        data: data.employeeGrowth.map(item => item.count),
        backgroundColor: 'rgba(116, 28, 121, 0.2)', // Light fill for area chart
        borderColor: '#741C79',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Gradient Function for Line Stroke
  const createGradient = (ctx, area, startColor, endColor) => {
    const gradient = ctx.createLinearGradient(0, 0, area.width, 0);
    gradient.addColorStop(0, startColor);
    gradient.addColorStop(1, endColor);
    return gradient;
  };

  // Chart Options for Both Charts
  const chartOptions = (startColor, endColor) => ({
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.raw.toLocaleString()}`, // Tooltip format
        },
      },
    },
    scales: {
      x: { beginAtZero: true },
      y: { beginAtZero: true },
    },
    elements: {
      line: {
        borderColor: (ctx) => createGradient(ctx.chart.ctx, ctx.chart.chartArea, startColor, endColor), // Gradient stroke
        backgroundColor: 'rgba(85, 168, 203, 0.2)', // Fill color
      },
      point: {
        radius: 5,
        hoverRadius: 8,
        hoverBackgroundColor: '#FF6392',
      },
    },
    animation: {
      duration: 2000,
      easing: 'easeInOutQuad',
    },
  });


  

  const departmentPayrollTooltipOptions = {
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.label}: $${context.raw.toLocaleString()}`;
          }
        }
      }
    }
  };


  return (
    <div className={styles.adminDashboard}>
      <Sidebar /> {/* Use Sidebar component here */}

      <main className={styles.dashboardContent}>
        <h1>Admin Dashboard</h1>
        
        <div className={styles.gridLayout}>
          {/* Top Row Cards */}
          <div className={styles.metricsContainer}>
            <div className={styles.metricCard}>
              <div className={styles.cardContent}>
                <img src={totalEmployeesIcon} alt="Total Employees Icon" className={styles.metricIcon} />
                <div>
                  <div className={styles.metricNumber}>{data.totalEmployees}</div>
                  <div className={styles.metricLabel}>Total Employees</div>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.metricsContainer}>
            <div className={styles.metricCard}>
              <div className={styles.cardContent}>
              <img src={pendingLeavesIcon} alt="Pending Leaves Icon" className={styles.metricIcon} />
                <div>
                <div className={styles.metricNumber}>{data.pendingLeaves}</div>
                <div className={styles.metricLabel}>Pending Leave Requests</div>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.metricsContainer}>
            <div className={styles.metricCard}>
              <div className={styles.cardContent}> 
              <img src={salaryIcon} alt="Average Salary Icon" className={styles.metricIcon} />
                <div>
                <div className={styles.metricNumber}>{data.avgSalary}</div>
                <div className={styles.metricLabel}>Average Salary</div>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.metricsContainer}>
            <div className={styles.metricCard}>
              <div className={styles.cardContent}>
              <img src={bonusIcon} alt="Bonus Icon" className={styles.metricIcon} />
                <div>
                <div className={styles.metricNumber}>{data.bonusesIncentivesPaid}</div>
                <div className={styles.metricLabel}>Bonuses & Incentives Paid in the Past Year</div>
                </div>
              </div>
            </div>
          </div>

          <div className={styles.deptPayrollChart}>
            <h3>Employees by Department Payroll</h3>
            <div className={styles.doughnutWrapper}>
              <Doughnut key="departmentPayroll" data={departmentPayrollData} options={departmentPayrollTooltipOptions} />
            </div>
          </div>

          {/* Payroll Expenses Chart */}
          <div className={styles.payrollChart}>
            <h3>Payroll Expenses</h3>
            <Line data={payrollData} options={chartOptions('#55A8CB', '#741C79')} />
          </div>

          {/* Employee Growth Chart */}
          <div className={styles.employeeGrowthChart}>
            <h3>Employee Growth (Monthly)</h3>
            <Line data={employeeGrowthData} options={chartOptions('#741C79', '#FF6392')} />
          </div>

          {/* Highest Salary Employees */}
          <div className={styles.highestSalarySection}>
            <h3>Top 5 Highest Salary Employees</h3>
            <ul>
              {data.highestSalaryEmployees.map((emp, index) => (
                <li key={index}>{emp.name}: ${emp.salary}</li>
              ))}
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
