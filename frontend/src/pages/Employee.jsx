// src/pages/Employee.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EmployeeList from './EmployeeList';
import AddEmployeeForm from './AddEmployeeForm';
import styles from '../styles/EmployeeList.module.css';
import Sidebar from './Sidebar';

const EmployeePage = () => {
  const [employees, setEmployees] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/admin/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error("Error fetching employees data:", error);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const toggleForm = () => {
    setShowForm(!showForm);
  };


  return (
    <div className={styles.employeePageContainer}>
      <Sidebar />
      <div className={styles.contentContainer}>
        <h1>Employee Management</h1>
        <EmployeeList employees={employees} />
        <button onClick={toggleForm} className={styles.toggleButton}>
          {showForm ? 'Hide Form' : 'Add New Employee'}
        </button>
        {showForm && <AddEmployeeForm onEmployeeAdded={fetchEmployees} />}
      </div>
    </div>
  );
};

export default EmployeePage;
