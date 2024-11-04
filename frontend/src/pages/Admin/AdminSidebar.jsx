// src/components/Sidebar.jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from '../../styles/Admin/AdminSidebar.module.css';

const Sidebar = () => {
    const location = useLocation(); // Hook to get the current route path

    // Function to determine if a link is active
    const isActive = (path) => location.pathname === path;

    return (
        <aside className={styles.sidebar}>
            <h2>Payroll Manager</h2>
            <nav>
                <ul>
                    <li>
                        <div className={`${styles.navLinks} ${isActive('/admin_dashboard') ? styles.active : ''}`}>
                            <Link to="/admin_dashboard">Dashboard</Link>
                        </div>
                    </li>
                    <li>
                        <div className={`${styles.navLinks} ${isActive('/employees') ? styles.active : ''}`}>
                            <Link to="/employees">Employees</Link>
                        </div>
                    </li>
                    <li>
                        <div className={`${styles.navLinks} ${isActive('/payroll') ? styles.active : ''}`}>
                            <Link to="/payroll">Payroll</Link>
                        </div>
                    </li>
                    <li>
                        <div className={`${styles.navLinks} ${isActive('/leaves') ? styles.active : ''}`}>
                            <Link to="/leaves">Leaves</Link>
                        </div>
                    </li>
                </ul>
            </nav>
        </aside>
    );
};

export default Sidebar;
