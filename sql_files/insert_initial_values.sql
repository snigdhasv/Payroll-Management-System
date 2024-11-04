ALTER TABLE Tax_Bracket MODIFY max_salary DECIMAL(15, 2) NULL;

INSERT INTO Tax_Bracket (min_salary, max_salary, tax_rate) VALUES 
    (0.00, 30000.00, 5.00),      -- 5% tax for salaries up to 30,000
    (30001.00, 60000.00, 10.00), -- 10% tax for salaries between 30,001 and 60,000
    (60001.00, 100000.00, 15.00),-- 15% tax for salaries between 60,001 and 100,000
    (100001.00, NULL, 20.00);    -- 20% tax for salaries above 100,000

-- Populate Employee table
INSERT INTO Employee (first_name, last_name, email, phone_number, address, department, role, status, salary, hire_date)
VALUES 
    ('John', 'Doe', 'john.doe@example.com', '123-456-7890', '123 Main St', 'Human Resources', 'Manager', 'Active', 55000.00, '2024-06-15'),
    ('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', '456 Elm St', 'Finance', 'Analyst', 'Active', 45000.00, '2024-01-20'),
    ('Michael', 'Johnson', 'michael.j@example.com', '456-789-1230', '789 Pine St', 'Research and Development', 'Developer', 'Active', 75000.00, '2024-09-10'),
    ('Emily', 'Davis', 'emily.d@example.com', '321-654-9870', '321 Oak St', 'Production and Operations', 'Supervisor', 'Active', 105000.00, '2024-03-05');

-- Populate Users table
INSERT INTO Users (username, password, employee_id, role)
VALUES 
    ('john_doe', 'hashed_password1', 1, 'admin'),
    ('jane_smith', 'hashed_password2', 2, 'employee'),
    ('michael_j', 'hashed_password3', 3, 'employee'),
    ('emily_d', 'hashed_password4', 4, 'admin');

-- Populate Payroll table
INSERT INTO Payroll (employee_id, basic_salary, bonus, tax_deduction, deductions, net_salary, pay_date, payslip_generated)
VALUES 
    (1, 55000.00, 5000.00, 2750.00, 2000.00, 55500.00, '2024-10-01', FALSE),
    (2, 45000.00, 3000.00, 4500.00, 1500.00, 42000.00, '2024-10-01', FALSE),
    (3, 75000.00, 6000.00, 11250.00, 2500.00, 67250.00, '2024-10-01', FALSE),
    (4, 105000.00, 8000.00, 21000.00, 3000.00, 89000.00, '2024-10-01', FALSE);


-- Populate Leaves table
INSERT INTO Leaves (employee_id, leave_type, start_date, end_date, status, reason)
VALUES 
    (1, 'Annual Leave', '2024-12-01', '2024-12-05', 'Pending', 'Family vacation'),
    (2, 'Sick Leave', '2024-09-10', '2024-09-12', 'Approved', 'Flu'),
    (3, 'Maternity Leave', '2024-07-01', '2024-10-01', 'Approved', 'Maternity care'),
    (4, 'Unpaid Leave', '2024-06-15', '2024-06-20', 'Rejected', 'Personal reasons');


SELECT * FROM Users;
SELECT * FROM Employee;
SELECT * FROM Payroll;
SHOW TRIGGERS LIKE 'Payroll';

SELECT * FROM Payslips;
SELECT * FROM Leaves;