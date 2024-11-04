// src/pages/PayrollList.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from '../styles/PayrollList.module.css';
import Sidebar from './Sidebar';

const PayrollList = () => {
  const [payrollData, setPayrollData] = useState([]);

  useEffect(() => {
    const fetchPayrollData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/payroll');
        setPayrollData(response.data);
      } catch (error) {
        console.error("Error fetching payroll data:", error);
      }
    };
    fetchPayrollData();
  }, []);

  const handlePayslipAction = async (payrollId, isGenerated) => {
    if (!isGenerated) {
      try {
        console.log(`Generating payslip for payroll ID: ${payrollId}`);
        const response = await axios.post(`http://localhost:5000/api/payroll/generate_payslip/${payrollId}`);
        alert(response.data.message);
        const refreshedData = await axios.get('http://localhost:5000/api/payroll');
        setPayrollData(refreshedData.data);
      } catch (error) {
        console.error("Error generating payslip:", error);
        alert("Failed to generate payslip");
      }
    } else {
      try {
        const response = await axios.get(`http://localhost:5000/api/payroll/download_payslip/${payrollId}`, {
          responseType: 'blob'
        });
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Payslip_${payrollId}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
      } catch (error) {
        console.error("Error downloading payslip:", error);
        alert("Failed to download payslip");
      }
    }
  };

  return (
    <div className={styles.payrollListContainer}>
      <Sidebar/>
      <div className={styles.payrollList}>
      <h1>Payroll List</h1>
      <table className={styles.payrollTable}>
        <thead>
          <tr>
            <th>Employee ID</th>
            <th>Employee Name</th>
            <th>Role</th>
            <th>Department</th>
            <th>Net Salary</th>
            <th>Pay Date</th>
            <th>Payslip</th>
          </tr>
        </thead>
        <tbody>
          {payrollData.map((item, index) => (
            <tr key={index}>
              <td>{item.employee_id}</td>
              <td>{item.employee_name}</td>
              <td>{item.role}</td>
              <td>{item.department}</td>
              <td>${item.net_salary}</td>
              <td>{item.pay_date}</td>
              <td>
                <button onClick={() => handlePayslipAction(item.payroll_id, item.payslip_generated)}>
                  {item.payslip_generated ? "Download" : "Generate Payslip"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
};

export default PayrollList;
