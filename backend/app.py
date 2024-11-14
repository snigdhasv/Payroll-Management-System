# backend/app.py
from flask import Flask, request, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, text, extract
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime, timedelta, date
from sqlalchemy import func, extract, text
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import logging
from sqlalchemy.exc import SQLAlchemyError
import secrets


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})  # Allow CORS for cross-origin requests from React frontend

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

    print(f"Received login attempt for username: '{username}'")

    # Query for user with the provided username
    user = User.query.filter_by(username=username).first()

    if user and user.password == password:  # Simplified password check
        # Store user ID and role in session
        session['employee_id'] = user.employee_id
        session['role'] = user.role
        
        print("Login successful, session created")
        dashboard_url = '/employee_dashboard' if user.role == 'employee' else '/admin_dashboard'
        return jsonify({"message": "Login successful", "role": user.role, "dashboard_url": dashboard_url}), 200
    else:
        print("Invalid credentials")
        return jsonify({"message": "Invalid username or password"}), 401
    
    
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()  # Clear all session data
    return jsonify({"message": "Logged out successfully"}), 200



@app.route('/api/employee/dashboard', methods=['GET'])
def get_employee_payroll():
    # Retrieve `employee_id` from session instead of expecting it in request params
    employee_id = session.get('employee_id')
    if not employee_id:
        return jsonify({"error": "Employee ID is required"}), 400

    # Fetch payroll data for the specific employee
    payroll_data = (
        db.session.query(
            Employee.first_name,
            Employee.last_name,
            Employee.role,
            Employee.department,
            Payroll.pay_date,
            Payroll.basic_salary,
            Payroll.bonus,
            Payroll.tax_deduction,
            Payroll.deductions,
            Payroll.net_salary,
            Payroll.payslip_generated,
            Payslip.payslip_id,
            Payslip.payslip_pdf    
        )
        .join(Employee, Employee.employee_id == Payroll.employee_id)
        .outerjoin(Payslip, Payroll.payroll_id == Payslip.payroll_id)
        .filter_by(employee_id=employee_id)
    )

    if not payroll_data:
        return jsonify({"message": "No payroll data found for this employee"}), 404

    # Format payroll data for response
    payroll_details = [{
        "employee_name": f"{record.first_name} {record.last_name}",
        "role": record.role,
        "department": record.department,
        "pay_date": record.pay_date,
        "basic_salary": float(record.basic_salary),
        "bonus": float(record.bonus),
        "tax_deduction": float(record.tax_deduction),
        "deductions": float(record.deductions),
        "net_salary": float(record.net_salary),
        "payslip_generated": bool(record.payslip_generated),
        "payslip_pdf": f"/api/payslip/download/{record.payslip_id}" if record.payslip_id else None
    } for record in payroll_data]

    return jsonify(payroll_details), 200


@app.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        # Total employees
        try:
            total_employees = db.session.execute(text("CALL GetTotalEmployees()")).scalar() or 0
        except SQLAlchemyError as e:
            logging.error("Error fetching total employees: %s", e)
            total_employees = 0

        # Average salary
        try:
            avg_salary = db.session.execute(text("CALL GetAverageSalary()")).scalar()
            avg_salary = str(round(avg_salary, 2)) if avg_salary else "0.00"
        except SQLAlchemyError as e:
            logging.error("Error fetching average salary: %s", e)
            avg_salary = "0.00"

        # Employee count per department
        department_data = {}
        try:
            department_result = db.session.execute(text("CALL GetEmployeeCountPerDepartment()"))
            for department, count in department_result:
                department_data[department] = count
        except SQLAlchemyError as e:
            logging.error("Error fetching department data: %s", e)

        # Payroll expenses over the last 12 months
        payroll_expenses = []
        x_axis_labels = []
        try:
            payroll_expenses_result = db.session.execute(text("CALL GetPayrollExpensesLast12Months()"))
            now = datetime.now()
            last_12_months = {
                (now - relativedelta(months=i)).strftime('%Y-%m'): 0 for i in range(11, -1, -1)
            }
            for year, month, total in payroll_expenses_result:
                month_key = f"{int(year)}-{int(month):02}"
                if month_key in last_12_months:
                    last_12_months[month_key] = float(total)
            x_axis_labels = list(last_12_months.keys())
            payroll_expenses = list(last_12_months.values())
        except SQLAlchemyError as e:
            logging.error("Error fetching payroll expenses: %s", e)

        # Pending leave requests count
        try:
            pending_leaves_count = db.session.execute(text("CALL GetPendingLeavesCount()")).scalar() or 0
        except SQLAlchemyError as e:
            logging.error("Error fetching pending leaves count: %s", e)
            pending_leaves_count = 0

        # Employee growth (new hires each month for the past year)
        employee_growth = []
        try:
            employee_growth_result = db.session.execute(text("CALL GetEmployeeGrowth()"))
            for year, month, count in employee_growth_result:
                employee_growth.append({"year": int(year), "month": int(month), "count": int(count)})
        except SQLAlchemyError as e:
            logging.error("Error fetching employee growth: %s", e)

        # Department payroll data
        department_payroll_data = {}
        try:
            department_payroll_result = db.session.execute(text("CALL GetDepartmentPayrollExpenses()"))
            for department, total in department_payroll_result:
                department_payroll_data[department] = f"{float(total):.2f}"  # Convert to string with 2 decimals
        except SQLAlchemyError as e:
            logging.error("Error fetching department payroll data: %s", e)

        # Highest salary employees
        highest_salary_employees = []
        try:
            highest_salary_result = db.session.execute(text("CALL GetTop5HighestSalaryEmployees()"))
            for first_name, last_name, salary in highest_salary_result:
                highest_salary_employees.append({
                    "name": f"{first_name} {last_name}",
                    "salary": f"{float(salary):.2f}"  # Convert to string with 2 decimals
                })
        except SQLAlchemyError as e:
            logging.error("Error fetching highest salary employees: %s", e)

        # Bonuses and incentives
        try:
            bonuses_incentives = db.session.execute(text("CALL GetTotalBonusesIncentives()")).scalar()
            bonuses_incentives = f"{bonuses_incentives:.2f}" if bonuses_incentives else "0.00"  # Format as string
        except SQLAlchemyError as e:
            logging.error("Error fetching bonuses and incentives: %s", e)
            bonuses_incentives = "0.00"

        # Return JSON response with formatted data
        return jsonify({
            "totalEmployees": total_employees,
            "avgSalary": avg_salary,
            "departmentData": department_data,
            "payrollExpenses": payroll_expenses,
            "xAxisLabels": x_axis_labels,
            "pendingLeaves": pending_leaves_count,
            "employeeGrowth": employee_growth,
            "departmentPayrollData": department_payroll_data,
            "highestSalaryEmployees": highest_salary_employees,
            "bonusesIncentivesPaid": bonuses_incentives,
        }), 200

    except Exception as e:
        logging.error("Error in get_dashboard_data: %s", e)
        return jsonify({"error": "Internal server error"}), 500


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


# API Endpoint to fetch payroll data with employee and payslip details
@app.route('/api/payroll', methods=['GET'])
def get_payroll_data():
    payroll_data = (
        db.session.query(
            Payroll.employee_id,
            Employee.first_name,
            Employee.last_name,
            Employee.role,
            Employee.department,
            Payroll.net_salary,
            Payroll.pay_date,
            Payroll.payslip_generated,
            Payslip.payslip_id  
        )
        .join(Employee, Employee.employee_id == Payroll.employee_id)
        .outerjoin(Payslip, Payroll.payroll_id == Payslip.payroll_id)
        .all()
    )
    
    payroll_list = [
        {
            "employee_id": record.employee_id,
            "employee_name": f"{record.first_name} {record.last_name}",
            "role": record.role,
            "department": record.department,
            "net_salary": float(record.net_salary) if record.net_salary is not None else 0.0,
            "pay_date": record.pay_date.isoformat(),
            "payslip_generated": record.payslip_generated,
            "payroll_id": record.employee_id,
            "payslip_pdf": f"/api/payslip/download/{record.payslip_id}" if record.payslip_id else None
        }
        for record in payroll_data
    ]


    return jsonify(payroll_list), 200


# Serve Payslip PDF by ID
@app.route('/api/payslip/download/<int:payslip_id>', methods=['GET'])
def serve_payslip_by_id(payslip_id):
    payslip = Payslip.query.get(payslip_id)
    if payslip:
        return send_file(BytesIO(payslip.payslip_pdf), mimetype='application/pdf', as_attachment=True, download_name=f"Payslip_{payslip_id}.pdf")
    return jsonify({"message": "Payslip not found"}), 404


# Function to generate and store payslip PDF
@app.route('/api/payroll/generate_payslip/<int:payroll_id>', methods=['POST'])
def generate_payslip(payroll_id):
    print(f"Attempting to generate payslip for payroll ID: {payroll_id}")
    payroll = Payroll.query.get(payroll_id)
    employee = Employee.query.get(payroll.employee_id) if payroll else None
    if not payroll or not employee:
        return jsonify({"message": "Payroll or Employee not found"}), 404

    gross_earnings = payroll.basic_salary + payroll.bonus
    total_deductions = payroll.deductions + payroll.tax_deduction
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(250, height - 50, "Payslip")

    # Employee Details Section
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 100, f"Employee ID: {employee.employee_id}")
    pdf.drawString(300, height - 100, f"Designation: {employee.role}")
    pdf.drawString(50, height - 120, f"Employee Name: {employee.first_name} {employee.last_name}")
    pdf.drawString(300, height - 120, f"Date of Joining: {employee.hire_date.strftime('%Y-%m-%d')}")
    pdf.drawString(50, height - 140, f"Department: {employee.department}")
    pdf.drawString(300, height - 140, f"Pay Date: {payroll.pay_date.strftime('%Y-%m-%d')}")

    # Earnings Table
    earnings_data = [
        ["Earnings", "Amount"],
        ["Basic Salary", f"${payroll.basic_salary:.2f}"],
        ["Bonus", f"${payroll.bonus:.2f}"],
        ["Gross Earnings", f"${gross_earnings:.2f}"]
    ]
    earnings_table = Table(earnings_data, colWidths=[2 * inch, 2 * inch])
    earnings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    earnings_table.wrapOn(pdf, width, height)
    earnings_table.drawOn(pdf, 50, height - 250)

    # Deductions Table
    deductions_data = [
        ["Deductions", "Amount"],
        ["Tax Deductions", f"${payroll.tax_deduction:.2f}"],
        ["Other Deductions", f"${payroll.deductions:.2f}"],
        ["Total Deductions", f"${total_deductions:.2f}"]
    ]
    deductions_table = Table(deductions_data, colWidths=[2 * inch, 2 * inch])
    deductions_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    deductions_table.wrapOn(pdf, width, height)
    deductions_table.drawOn(pdf, 300, height - 250)

    # Net Pay Section
    net_pay_data = [
        ["Net Pay", f"${payroll.net_salary:.2f}"]
    ]
    net_pay_table = Table(net_pay_data, colWidths=[2 * inch, 2 * inch])
    net_pay_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    net_pay_table.wrapOn(pdf, width, height)
    net_pay_table.drawOn(pdf, 300, height - 300)

    # Save PDF
    pdf.showPage()
    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    # Store payslip in database
    new_payslip = Payslip(
        employee_id=employee.employee_id,
        payroll_id=payroll.payroll_id,
        payslip_pdf=pdf_data,
        generated_date=payroll.pay_date
    )
    db.session.add(new_payslip)
    payroll.payslip_generated = True
    db.session.commit()
    
    return jsonify({"message": "Payslip generated successfully"}), 201

# Endpoint to download generated payslip by payroll ID
@app.route('/api/payroll/download_payslip/<int:payroll_id>', methods=['GET'])
def download_payslip_by_payroll(payroll_id):
    payslip = Payslip.query.filter_by(payroll_id=payroll_id).first()
    if payslip:
        return send_file(BytesIO(payslip.payslip_pdf), mimetype='application/pdf', as_attachment=True, download_name=f"Payslip_{payslip.employee_id}_{payroll_id}.pdf")
    return jsonify({"message": "Payslip not found"}), 404

@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    leaves = db.session.query(
        Leaves.employee_id,
        Employee.first_name,
        Employee.last_name,
        Leaves.leave_type,
        Leaves.start_date,
        Leaves.end_date,
        Leaves.status,
        Leaves.reason
    ).join(Employee, Employee.employee_id == Leaves.employee_id).all()

    leave_data = [
        {
            "employee_id": leave.employee_id,
            "employee_name": f"{leave.first_name} {leave.last_name}",
            "leave_type": leave.leave_type,
            "start_date": leave.start_date.strftime('%Y-%m-%d'),
            "end_date": leave.end_date.strftime('%Y-%m-%d'),
            "status": leave.status,
            "reason": leave.reason
        }
        for leave in leaves
    ]

    return jsonify(leave_data)

@app.route('/api/leaves/update_status', methods=['POST'])
def update_leave_status():
    data = request.json
    leave_id = data.get('leave_id')
    new_status = data.get('status')

    leave = Leaves.query.get(leave_id)
    if leave:
        leave.status = new_status
        db.session.commit()
        return jsonify({"message": "Leave status updated successfully"}), 200
    else:
        return jsonify({"message": "Leave record not found"}), 404



# Run the app
if __name__ == '__main__':
    app.run(port=5000, debug=True)