import React, { useState, useEffect } from 'react';
import { Pie } from 'react-chartjs-2';
import axios from 'axios';
import styles from '../../styles/Employee/EmployeeDashboard.module.css';
import Sidebar from './EmployeeSidebar';

const EmployeeDashboard = ({ employeeId }) => {
  const [data, setData] = useState({
    name: "",
    role: "",
    department: "",
    basicSalary: 0,
    netSalary: 0,
    bonus: 0,
    taxDeduction: 0,
    otherDeductions: 0,
    isPayslipGenerated: false,
    payslipUrl: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPayrollData = async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://localhost:5000/api/employee/dashboard', {
          withCredentials: true,
        });
        
        if (response.data && response.data.length > 0) {
          const payroll = response.data[0];
          setData({
            name: payroll.employee_name,  // Add name
            role: payroll.role,           // Add role
            department: payroll.department, // Add department
            basicSalary: payroll.basic_salary || 0,
            netSalary: payroll.net_salary || 0,
            bonus: payroll.bonus || 0,
            taxDeduction: payroll.tax_deduction || 0,
            otherDeductions: payroll.deductions || 0,
            isPayslipGenerated: payroll.payslip_generated || false,
            payslipUrl: payroll.payslip_pdf || null,
          });
          
        }
      } catch (error) {
        setError('Error fetching payroll data');
      } finally {
        setLoading(false);
      }
    };

    fetchPayrollData();
  }, [employeeId]);

  const handlePayslipDownload = async () => {
    if (data.isPayslipGenerated && data.payslipUrl) {
      try {
        const response = await axios.get(`http://localhost:5000${data.payslipUrl}`, {
          responseType: 'blob',
        });
        
        // Create a URL for the blob object and download the file
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Payslip_${employeeId}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
      } catch (error) {
        console.error("Error downloading payslip:", error);
        alert("Failed to download payslip");
      }
    } else {
      alert("Payslip not generated yet.");
    }
  };

  const dataPie = {
    labels: ['Basic Salary', 'Bonus', 'Tax Deduction', 'Other Deductions'],
    datasets: [
      {
        data: [data.basicSalary, data.bonus, data.taxDeduction, data.otherDeductions],
        backgroundColor: ['#55A8CB', '#FF6392', '#FFE45E', '#741C79', '#FF5647'],
        hoverBackgroundColor: ['#6AC9F2', '#FF7BA3', '#FFEA82', '#CB3CD2', '#FC8479'],
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  
  return (
    <div className={styles.employeeDashboard}>
      <Sidebar />
      <main className={styles.dashboardContent}>
        <div className={styles.welcomeWrapper}>
        <h3>Welcome {data.name},</h3>
        <h3>You work at the {data.department} Department as a {data.role}</h3>
        </div>
        <div className={styles.gridLayout}>
          {/* Salary Cards */}
          {[
            { label: "Basic Salary", value: data.basicSalary },
            { label: "Net Salary", value: data.netSalary },
            { label: "Bonus", value: data.bonus },
            { label: "Tax Deduction", value: data.taxDeduction },
            { label: "Other Deductions", value: data.otherDeductions }
          ].map((item, index) => (
            <div key={index} className={styles.metricsContainer}>
              <div className={styles.metricCard}>
                <div className={styles.cardContent}>
                  <div>
                    <div className={styles.metricLabel}>{item.label}</div>
                    <div className={styles.metricNumber}>
                      ${item.value ? item.value.toLocaleString() : '0.00'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Payslip Card with Download Button */}
          <div className={styles.metricsContainer}>
            <div
              className={`${styles.metricCard} ${data.isPayslipGenerated ? styles.payslipAvailable : styles.payslipNotAvailable}`}
              onClick={data.isPayslipGenerated ? handlePayslipDownload : null}
            >
              <div className={styles.cardContent}>
                <div className={styles.metricLabel}>
                  {data.isPayslipGenerated ? 'Payslip Available' : 'Payslip Not Generated Yet'}
                </div>
                <div className={styles.metricNumber}>
                  {data.isPayslipGenerated ? 'Download' : 'Not Available'}
                </div>
              </div>
            </div>
          </div>
          <div className={styles.Chart}>
            <h3>Payroll</h3>
            <div className={styles.pieWrapper}>
              <Pie data={dataPie} options={options}/>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
};  

export default EmployeeDashboard;
