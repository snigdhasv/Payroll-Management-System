// src/pages/EmployeeList.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from '../../styles/Admin/Employee.module.css';

const EmployeeList = () => {
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/admin/employees');
        setEmployees(response.data);
      } catch (error) {
        console.error("Error fetching employees data:", error);
      }
    };

    fetchEmployees();
  }, []);

  // Delete an employee by ID
  // src/pages/EmployeeList.jsx
  const handleDeleteEmployee = async (employee_id) => {
    try {
      await axios.delete(`http://localhost:5000/api/employees/${employee_id}`);  // Use backticks for template string
      setEmployees(employees.filter(emp => emp.employee_id !== employee_id));
    } catch (error) {
      console.error("Error deleting employee:", error);
    }
  };

  return (
    <div className={styles.employeeList}>
      <table className={styles.employeeTable}>
        <thead>
          <tr>
            <th>ID</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Department</th>
            <th>Role</th>
            <th>Status</th>
            <th>Salary</th>
            <th>Hire Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employees.map(emp => (
            <tr key={emp.employee_id}>
              <td>{emp.employee_id}</td>
              <td>{emp.first_name}</td>
              <td>{emp.last_name}</td>
              <td>{emp.email}</td>
              <td>{emp.phone_number}</td>
              <td>{emp.address}</td>
              <td>{emp.department}</td>
              <td>{emp.role}</td>
              <td>{emp.status}</td>
              <td>${emp.salary}</td>
              <td>{emp.hire_date}</td>
              <td>
                <button onClick={() => handleDeleteEmployee(emp.employee_id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
  );
};

export default EmployeeList;