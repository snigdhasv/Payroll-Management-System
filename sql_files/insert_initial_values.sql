ALTER TABLE Tax_Bracket MODIFY max_salary DECIMAL(15, 2) NULL;

INSERT INTO Tax_Bracket (min_salary, max_salary, tax_rate) VALUES 
    (0.00, 30000.00, 5.00),      -- 5% tax for salaries up to 30,000
    (30001.00, 60000.00, 10.00), -- 10% tax for salaries between 30,001 and 60,000
    (60001.00, 100000.00, 15.00),-- 15% tax for salaries between 60,001 and 100,000
    (100001.00, NULL, 20.00);    -- 20% tax for salaries above 100,000

-- Populate Employee table
INSERT INTO Employee (first_name, last_name, email, phone_number, address, department, role, status, salary, hire_date)
VALUES 
    ('John', 'Doe', 'john.doe@example.com', '123-456-7890', '123 Main St', 'Human Resources', 'Manager', 'active', 55000.00, '2024-06-15'),
    ('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', '456 Elm St', 'Finance', 'Analyst', 'active', 45000.00, '2024-01-20'),
    ('Michael', 'Johnson', 'michael.j@example.com', '456-789-1230', '789 Pine St', 'Research and Development', 'Developer', 'active', 75000.00, '2024-09-10'),
    ('Emily', 'Davis', 'emily.d@example.com', '321-654-9870', '321 Oak St', 'Production and Operations', 'Supervisor', 'inactive', 105000.00, '2024-03-05'),
    ('Alice', 'Brown', 'alice.brown@example.com', '555-123-4567', '234 Maple St', 'Marketing', 'Specialist', 'active', 60000.00, '2024-08-01'),
    ('David', 'Wilson', 'david.wilson@example.com', '555-234-5678', '567 Birch St', 'IT', 'Technician', 'active', 50000.00, '2024-02-15'),
    ('Sophia', 'Lee', 'sophia.lee@example.com', '555-345-6789', '890 Cedar St', 'Finance', 'Manager', 'active', 70000.00, '2024-04-10'),
    ('James', 'Martinez', 'james.martinez@example.com', '555-456-7890', '321 Walnut St', 'Research and Development', 'Senior Developer', 'active', 85000.00, '2024-05-20'),
    ('Olivia', 'Garcia', 'olivia.garcia@example.com', '555-567-8901', '654 Spruce St', 'Human Resources', 'Coordinator', 'active', 45000.00, '2024-07-25'),
    ('Daniel', 'Hernandez', 'daniel.hernandez@example.com', '555-678-9012', '789 Fir St', 'Production and Operations', 'Manager', 'active', 95000.00, '2024-09-01');
-- Populate Users table
INSERT INTO Users (username, password, employee_id, role)
VALUES 
    ('john_doe', 'hashed_password1', 1, 'admin'),
    ('jane_smith', 'hashed_password2', 2, 'employee'),
    ('michael_j', 'hashed_password3', 3, 'employee'),
    ('emily_d', 'hashed_password4', 4, 'admin'),
    ('alice_b', 'hashed_password5', 5, 'employee'),
    ('david_w', 'hashed_password6', 6, 'employee'),
    ('sophia_l', 'hashed_password7', 7, 'admin'),
    ('james_m', 'hashed_password8', 8, 'employee'),
    ('olivia_g', 'hashed_password9', 9, 'employee'),
    ('daniel_h', 'hashed_password10', 10, 'admin');

-- Populate Payroll table
INSERT INTO Payroll (employee_id, basic_salary, bonus, tax_deduction, deductions, net_salary, pay_date, payslip_generated)
VALUES 
    (1, 55000.00, 5000.00, 2750.00, 2000.00, 55500.00, '2024-10-01', FALSE),
    (2, 45000.00, 3000.00, 4500.00, 1500.00, 42000.00, '2024-11-01', FALSE),
    (3, 75000.00, 6000.00, 11250.00, 2500.00, 67250.00, '2024-10-01', FALSE),
    (4, 105000.00, 8000.00, 21000.00, 3000.00, 89000.00, '2024-09-01', FALSE),
    (5, 60000.00, 4000.00, 3000.00, 2000.00, 58000.00, '2024-08-01', FALSE),
    (6, 50000.00, 2500.00, 2500.00, 1500.00, 45500.00, '2024-09-01', FALSE),
    (7, 70000.00, 5000.00, 3500.00, 3000.00, 62000.00, '2024-10-01', FALSE),
    (8, 85000.00, 7000.00, 12750.00, 3500.00, 73500.00, '2024-10-01', FALSE),
    (9, 45000.00, 3000.00, 4500.00, 1500.00, 42000.00, '2024-11-01', FALSE),
    (10, 95000.00, 8000.00, 19000.00, 4000.00, 87000.00, '2024-11-01', FALSE);


-- Populate Leaves table
INSERT INTO Leaves (employee_id, leave_type, start_date, end_date, status, reason)
VALUES 
    (1, 'Annual Leave', '2024-12-01', '2024-12-05', 'Pending', 'Family vacation'),
    (2, 'Sick Leave', '2024-09-10', '2024-09-12', 'Approved', 'Flu'),
    (4, 'Maternity Leave', '2024-09-01', '2024-12-01', 'Approved', 'Maternity care'),
    (3, 'Unpaid Leave', '2024-06-15', '2024-06-20', 'Rejected', 'Personal reasons');


SELECT * FROM Users;
SELECT * FROM Employee;
SELECT * FROM Payroll;
SHOW TRIGGERS LIKE 'Payroll';

SELECT * FROM Payslips;
SELECT * FROM Leaves;