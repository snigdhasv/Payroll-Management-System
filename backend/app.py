# backend/app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

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
            if user.role == 'employee':
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



# Run the app
if __name__ == '__main__':
    app.run(port=5000, debug=True)