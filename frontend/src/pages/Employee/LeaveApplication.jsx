import React, { useState } from 'react';
import axios from 'axios';
import styles from '../../styles/Employee/LeaveApplication.module.css';
import Sidebar from './EmployeeSidebar';

const EmployeeLeaveApplication = () => {
  const [leaveDetails, setLeaveDetails] = useState({
    leave_type: '',
    start_date: '',
    end_date: '',
    reason: '',
  });
  const [message, setMessage] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setLeaveDetails({ ...leaveDetails, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        'http://localhost:5000/api/employee/apply_leave',
        leaveDetails, // Send leave details object directly
        { withCredentials: true } // Ensure session cookie is sent
      );

      // Show success message and clear form
      setMessage({ text: response.data.message, type: 'success' });
      setLeaveDetails({ leave_type: '', start_date: '', end_date: '', reason: '' });
    } catch (error) {
      console.error('Error applying leave:', error.response || error);
      setMessage({ text: error.response?.data?.error || 'Failed to apply for leave', type: 'error' });
    }
  };

  return (
    <div className={styles.container}>
      <Sidebar />
      <div className={styles.content}>
        <h1>Apply for Leave</h1>
        {message && (
          <p className={`${styles.message} ${message.type === 'success' ? styles.success : styles.error}`}>
            {message.text}
          </p>
        )}
        <form onSubmit={handleSubmit} className={styles.leaveForm}>
          <div className={styles.formRow}>
            <label>Leave Type:</label>
            <select
              name="leave_type"
              value={leaveDetails.leave_type}
              onChange={handleInputChange}
              required
            >
              <option value="" disabled>Select leave type</option>
              <option value="Sick Leave">Sick Leave</option>
              <option value="Casual Leave">Casual Leave</option>
              <option value="Maternity Leave">Maternity Leave</option>
              <option value="Paternity Leave">Paternity Leave</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className={styles.formRow}>
            <label>Start Date:</label>
            <input
              type="date"
              name="start_date"
              value={leaveDetails.start_date}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className={styles.formRow}>
            <label>End Date:</label>
            <input
              type="date"
              name="end_date"
              value={leaveDetails.end_date}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className={styles.formRow}>
            <label>Reason:</label>
            <textarea
              name="reason"
              value={leaveDetails.reason}
              onChange={handleInputChange}
              placeholder="Provide a reason for your leave"
              required
            />
          </div>
          <div className={styles.buttonContainer}>
            <button type="submit" className={styles.submitButton}>Submit</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmployeeLeaveApplication;
