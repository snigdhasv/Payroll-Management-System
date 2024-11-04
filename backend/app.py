# backend/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, text, extract
from datetime import datetime, timedelta, date
from sqlalchemy import func, extract, text
from decimal import Decimal
from dateutil.relativedelta import relativedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow CORS for cross-origin requests from React frontend

# Configure SQLAlchemy to connect to MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:snig23@localhost/payroll_management_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the User model corresponding to the Users table
class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.Integer)
    role = db.Column(db.String(20), nullable=False)
    
class TaxBracket(db.Model):
    __tablename__ = 'Tax_Bracket'
    tax_bracket_id = db.Column(db.Integer, primary_key=True)
    min_salary = db.Column(db.Numeric(15, 2), nullable=False)
    max_salary = db.Column(db.Numeric(15, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False)

    
# Define the Employee model corresponding to the Employee table
class Employee(db.Model):
    __tablename__ = 'Employee'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Text)
    department = db.Column(db.String(50))
    role = db.Column(db.String(50))
    status = db.Column(db.String(20))
    salary = db.Column(db.Numeric(15, 2), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    tax_bracket_id = db.Column(db.Integer, db.ForeignKey('Tax_Bracket.tax_bracket_id'), nullable=True)

    # Relationship to Payroll (one-to-many relationship)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True)

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name}>"

# Define the Payroll model corresponding to the Payroll table
class Payroll(db.Model):
    __tablename__ = 'Payroll'
    payroll_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employee.employee_id'), nullable=False)
    basic_salary = db.Column(db.Numeric(15, 2), nullable=False)
    bonus = db.Column(db.Numeric(15, 2), default=0)
    tax_deduction = db.Column(db.Numeric(15,2), default=0)
    deductions = db.Column(db.Numeric(15, 2), default=0)
    net_salary = db.Column(db.Numeric(15, 2), nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    payslip_generated = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Payroll for Employee {self.employee_id} on {self.pay_date}>"
    
class Leaves(db.Model):
    __tablename__ = 'Leaves'
    leave_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employee.employee_id'), nullable=False)
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # e.g., 'pending', 'approved', 'rejected'
    total_leave_days = db.Column(db.Integer)
    reason = db.Column(db.Text)

class Payslip(db.Model):
    __tablename__ = 'Payslips'
    payslip_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employee.employee_id'), nullable=False)
    payroll_id = db.Column(db.Integer, db.ForeignKey('Payroll.payroll_id'), nullable=False)
    payslip_pdf = db.Column(db.LargeBinary, nullable=False)  # Store PDF as binary data
    generated_date = db.Column(db.Date, nullable=False)

    employee = db.relationship('Employee', backref='payslips')
    payroll = db.relationship('Payroll', backref='payslips')

    

# Login route to authenticate users
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    print(f"Received login attempt for username: '{username}', password: '{password}'")

    # Query for user with the provided username
    user = User.query.filter_by(username=username).first()

    if user:
        print(f"User found: {user.username}, stored password: '{user.password}'")
        if user.password == password:  # plain-text password comparison for testing
            print("Password matches, login successful")
            if user.role == ['employee', 'user']:
                dashboard_url = '/employee_dashboard'
            elif user.role in ['manager', 'admin']:
                dashboard_url = '/admin_dashboard'
            else:
                dashboard_url = '/'  # Default redirection
                
            return jsonify({"message": "Login successful", "role": user.role, "dashboard_url": dashboard_url}), 200
        else:
            print("Password does not match")
            return jsonify({"message": "Invalid username or password"}), 401
    else:
        print("User not found")
        return jsonify({"message": "Invalid username or password"}), 401


# API Endpoint to fetch admin dashboard data
@app.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard_data():
    # Total employees
    total_employees = db.session.query(func.count(Employee.employee_id)).scalar()

    # Average salary
    avg_salary = db.session.query(func.avg(Employee.salary)).scalar()

    # Employee count per department
    departments = db.session.query(
        Employee.department, func.count(Employee.employee_id)
    ).group_by(Employee.department).all()
    department_data = {department: count for department, count in departments}

    # Payroll expenses over the last 12 months
    payroll_expenses_data = db.session.query(
        extract('year', Payroll.pay_date).label('year'),
        extract('month', Payroll.pay_date).label('month'),
        func.sum(Payroll.net_salary)
    ).filter(Payroll.pay_date >= text("DATE_SUB(CURDATE(), INTERVAL 12 MONTH)")).group_by('year', 'month').all()

    # Initialize a dictionary with the last 12 months as keys, each set to 0 initially
    now = datetime.now()
    last_12_months = {
        (now - relativedelta(months=i)).strftime('%Y-%m'): 0 for i in range(11, -1, -1)  # Last 12 months in order
    }

    # Populate the dictionary with actual data from the query
    for year, month, total in payroll_expenses_data:
        month_key = f"{int(year)}-{int(month):02}"  # Zero-padded month
        if month_key in last_12_months:
            last_12_months[month_key] = float(total) if isinstance(total, Decimal) else total  # Convert Decimal to float

    # Prepare x-axis labels and y-axis data
    x_axis_labels = list(last_12_months.keys())
    payroll_expenses = list(last_12_months.values())

    # Pending leave requests count
    pending_leaves_count = db.session.query(func.count(Leaves.leave_id)).filter(Leaves.status == 'pending').scalar()

    # Employee growth - counts new hires each month for the past year
    employee_growth = db.session.query(
        func.extract('year', Employee.hire_date).label('year'),
        func.extract('month', Employee.hire_date).label('month'),
        func.count(Employee.employee_id)
    ).filter(Employee.hire_date >= text("DATE_SUB(CURDATE(), INTERVAL 12 MONTH)")) \
    .group_by('year', 'month') \
    .order_by(text('year ASC'), text('month ASC')).all()

    # Department-wise payroll expenses
    department_payroll = db.session.query(
        Employee.department, func.sum(Payroll.net_salary)
    ).join(Payroll, Employee.employee_id == Payroll.employee_id
    ).group_by(Employee.department).all()
    department_payroll_data = {dept: total for dept, total in department_payroll}

    # Highest salary employees (top 5)
    highest_salary_employees = db.session.query(
        Employee.first_name, Employee.last_name, Employee.salary
    ).order_by(Employee.salary.desc()).limit(5).all()
    highest_salary_data = [{"name": f"{emp[0]} {emp[1]}", "salary": emp[2]} for emp in highest_salary_employees]

    # Total bonuses and incentives paid in the last 12 months
    bonuses_incentives = db.session.query(
        func.sum(Payroll.bonus)
    ).filter(Payroll.pay_date >= text("DATE_SUB(CURDATE(), INTERVAL 12 MONTH)")).scalar()

    return jsonify({
        "totalEmployees": total_employees,
        "avgSalary": round(avg_salary, 2) if avg_salary else 0,
        "departmentData": department_data,
        "payrollExpenses": payroll_expenses,
        "xAxisLabels": x_axis_labels,
        "pendingLeaves": pending_leaves_count,
        "employeeGrowth": [{"year": int(y), "month": int(m), "count": int(c)} for y, m, c in employee_growth],
        "departmentPayrollData": department_payroll_data,
        "highestSalaryEmployees": highest_salary_data,
        "bonusesIncentivesPaid": bonuses_incentives if bonuses_incentives else 0,
    }), 200


# API Endpoint to fetch all employees data
@app.route('/api/admin/employees', methods=['GET'])
def get_all_employees():
    employees = Employee.query.all()
    employees_data = [
        {
            "employee_id": emp.employee_id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone_number": emp.phone_number,
            "address": emp.address,
            "department": emp.department,
            "role": emp.role,
            "status": emp.status,
            "salary": float(emp.salary),  # Convert salary to float for JSON serialization
            "hire_date": emp.hire_date.isoformat()  # Convert date to ISO format for JSON
        }
        for emp in employees
    ]
    return jsonify(employees_data), 200


# API Endpoint to add a new employee
@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    try:
        # 1. Add the new employee to the Employee table
        new_employee = Employee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            department=data.get('department'),
            role=data.get('role'),  # This is the employee's job role
            status=data.get('status'),
            salary=data['salary'],
            hire_date=data['hire_date']
        )
        db.session.add(new_employee)
        db.session.flush()  # Flush to get employee_id for the new employee

        # 2. Create a corresponding User entry for login with the user_role
        new_user = User(
            username=data['username'],
            password=data['password'],  # Consider hashing this in production
            employee_id=new_employee.employee_id,
            role=data['user_role']  # This is the user role (access control)
        )
        db.session.add(new_user)

        # 3. Initialize Payroll entry with specified details
        new_payroll = Payroll(
            employee_id=new_employee.employee_id,
            basic_salary=data['basic_salary'],
            bonus=data.get('bonus', 0),
            deductions=data.get('deductions', 0),
            pay_date=date.today(),
            payslip_generated=False
        )

        db.session.add(new_payroll)
        db.session.flush()  # Flush to get payroll_id

        # Commit all changes as a single transaction
        db.session.commit()

        # Return success response
        return jsonify({
            "message": "Employee added successfully",
            "employee_id": new_employee.employee_id,
            "username": data['username'],
            "payroll_id": new_payroll.payroll_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to add employee", "error": str(e)}), 500
        

# API Endpoint to delete an employee by ID
@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({"message": "Employee not found"}), 404
        
        # Log to check if the employee exists
        print(f"Attempting to delete employee: {employee}")

        # Delete associated payroll records
        Payroll.query.filter_by(employee_id=employee_id).delete()
        
        # Log to confirm payroll deletion
        print(f"Deleted payroll records for employee ID: {employee_id}")

        # Delete the employee
        db.session.delete(employee)
        db.session.commit()
        
        print("Employee deletion successful")
        return jsonify({"message": "Employee deleted successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Deletion error: {e}")
        return jsonify({"message": "Internal Server Error", "details": str(e)}), 500


# Run the app
if __name__ == '__main__':
    app.run(port=5000, debug=True)