from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime
import re
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('12thfailjobs.db')
    cursor = conn.cursor()
    
    # Create users table with enhanced fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password TEXT NOT NULL,
            user_type TEXT DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            logo TEXT,
            description TEXT,
            website TEXT,
            location TEXT,
            industry TEXT,
            founded_year INTEGER,
            employee_count TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create job categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            color TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company_id INTEGER,
            category_id INTEGER,
            location TEXT NOT NULL,
            salary_min INTEGER,
            salary_max INTEGER,
            salary_type TEXT DEFAULT 'monthly',
            job_type TEXT DEFAULT 'full-time',
            experience_level TEXT,
            description TEXT NOT NULL,
            requirements TEXT,
            benefits TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_featured BOOLEAN DEFAULT 0,
            views INTEGER DEFAULT 0,
            applications_count INTEGER DEFAULT 0,
            posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            FOREIGN KEY (category_id) REFERENCES job_categories (id)
        )
    ''')
    
    # Create applications table with enhanced fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            location TEXT NOT NULL,
            experience_years INTEGER,
            expected_salary INTEGER,
            cover_letter TEXT,
            resume_path TEXT,
            status TEXT DEFAULT 'pending',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create saved jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_id INTEGER,
            saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            UNIQUE(user_id, job_id)
        )
    ''')
    
    # Insert default categories
    default_categories = [
        ('Technology', 'IT and software development jobs', 'fas fa-laptop-code', '#e63946'),
        ('Sales & Marketing', 'Sales, marketing and business development', 'fas fa-chart-line', '#1d3557'),
        ('Customer Service', 'Customer support and service roles', 'fas fa-headset', '#457b9d'),
        ('Delivery & Logistics', 'Delivery, transportation and logistics', 'fas fa-truck', '#a8dadc'),
        ('Security', 'Security guard and safety positions', 'fas fa-shield-alt', '#f1faee'),
        ('Manufacturing', 'Factory and production jobs', 'fas fa-industry', '#e63946'),
        ('Healthcare', 'Medical and healthcare positions', 'fas fa-heartbeat', '#1d3557'),
        ('Education', 'Teaching and training roles', 'fas fa-graduation-cap', '#457b9d')
    ]
    
    cursor.execute('SELECT COUNT(*) FROM job_categories')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO job_categories (name, description, icon, color) 
            VALUES (?, ?, ?, ?)
        ''', default_categories)
    
    # Insert sample companies
    sample_companies = [
        ('TechCorp Solutions', 'https://via.placeholder.com/100x100/1d3557/ffffff?text=TC', 'Leading technology solutions provider', 'https://techcorp.com', 'Mumbai', 'Technology', 2015, '500-1000'),
        ('SecureGuard Services', 'https://via.placeholder.com/100x100/e63946/ffffff?text=SG', 'Professional security services', 'https://secureguard.com', 'Delhi', 'Security', 2010, '100-500'),
        ('FoodExpress Delivery', 'https://via.placeholder.com/100x100/457b9d/ffffff?text=FE', 'Fast food delivery service', 'https://foodexpress.com', 'Bangalore', 'Logistics', 2018, '1000-5000'),
        ('EduTech Academy', 'https://via.placeholder.com/100x100/a8dadc/ffffff?text=EA', 'Online education platform', 'https://edutech.com', 'Chennai', 'Education', 2016, '100-500')
    ]
    
    cursor.execute('SELECT COUNT(*) FROM companies')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO companies (name, logo, description, website, location, industry, founded_year, employee_count) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_companies)
    
    # Insert sample jobs
    sample_jobs = [
        ('Frontend Developer', 1, 1, 'Mumbai', 25000, 45000, 'monthly', 'full-time', '1-3 years', 'We are looking for a skilled Frontend Developer to join our team.', 'React, JavaScript, HTML, CSS', 'Health insurance, flexible hours', 1, 1),
        ('Security Guard', 2, 5, 'Delhi', 12000, 18000, 'monthly', 'full-time', '0-1 years', 'Looking for reliable security personnel for corporate office.', 'Basic security training, good communication', 'Uniform provided, meal allowance', 1, 0),
        ('Delivery Executive', 3, 4, 'Bangalore', 15000, 25000, 'monthly', 'full-time', '0-1 years', 'Join our fast-growing delivery team.', 'Valid driving license, smartphone', 'Fuel allowance, performance bonus', 1, 1),
        ('Sales Representative', 1, 2, 'Chennai', 18000, 30000, 'monthly', 'full-time', '1-3 years', 'Drive sales growth through customer engagement.', 'Good communication, negotiation skills', 'Commission, travel allowance', 1, 0),
        ('Customer Support Executive', 4, 3, 'Hyderabad', 14000, 22000, 'monthly', 'full-time', '0-2 years', 'Provide excellent customer service.', 'Good communication, problem-solving', 'Work from home options, health benefits', 1, 1)
    ]
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO jobs (title, company_id, category_id, location, salary_min, salary_max, salary_type, job_type, experience_level, description, requirements, benefits, is_active, is_featured) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_jobs)
    
    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None

# Routes
@app.route('/')
def index():
    if os.path.exists('portal.html'):
        with open('portal.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    else:
        return 'Portal HTML not found'

@app.route('/job-card.js')
def job_card_js():
    if os.path.exists('job-card.js'):
        with open('job-card.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript; charset=utf-8'}
    else:
        return 'Job card JS not found', 404

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not name or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        if not validate_email(email):
            return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters long'}), 400
        
        # Check for duplicate email
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Create user
        hashed_password = hash_password(password)
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                      (name, email, hashed_password))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Account created successfully!'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        # Check credentials
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2]):
            user_id, user_name = user[0], user[1]
        else:
            user = None
        
        if user:
            session['user_id'] = user_id
            session['user_name'] = user_name
            return jsonify({
                'success': True, 
                'message': 'Login successful!',
                'user': {'id': user_id, 'name': user_name, 'email': email}
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@app.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'user': {
                'id': session['user_id'],
                'name': session['user_name']
            }
        }), 200
    return jsonify({'success': False, 'user': None}), 200

@app.route('/submit-application', methods=['POST'])
def submit_application():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        mobile = data.get('mobile', '').strip()
        location = data.get('location', '').strip()
        message = data.get('message', '').strip()
        
        # Validation
        if not name or not mobile or not location:
            return jsonify({'success': False, 'error': 'Name, mobile, and location are required'}), 400
        
        if not validate_mobile(mobile):
            return jsonify({'success': False, 'error': 'Please enter a valid 10-digit mobile number starting with 6-9'}), 400
        
        # Check for duplicate mobile
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM applications WHERE mobile = ?', (mobile,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Application with this mobile number already exists'}), 409
        
        # Insert application
        cursor.execute('INSERT INTO applications (name, mobile, location, message) VALUES (?, ?, ?, ?)', 
                      (name, mobile, location, message))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Application submitted successfully! We will contact you soon.'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/view-applications', methods=['GET'])
def view_applications():
    try:
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications ORDER BY timestamp DESC')
        applications = cursor.fetchall()
        conn.close()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Applications - 12thFailJobs</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                h1 { color: #e63946; text-align: center; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #1d3557; color: white; }
                tr:hover { background-color: #f9f9f9; }
                .no-data { text-align: center; padding: 40px; color: #666; }
                .back-btn { display: inline-block; padding: 10px 20px; background: #e63946; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/" class="back-btn">← Back to Portal</a>
                <h1>Job Applications</h1>
        '''
        
        if applications:
            html += '''
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Mobile</th>
                            <th>Location</th>
                            <th>Message</th>
                            <th>Submitted</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            for app in applications:
                html += f'''
                    <tr>
                        <td>{app[0]}</td>
                        <td>{app[1]}</td>
                        <td>{app[2]}</td>
                        <td>{app[3]}</td>
                        <td>{app[4] or 'N/A'}</td>
                        <td>{app[5]}</td>
                    </tr>
                '''
            
            html += '</tbody></table>'
        else:
            html += '<div class="no-data"><h3>No applications submitted yet</h3></div>'
        
        html += '</div></body></html>'
        
        return html
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search-jobs', methods=['POST'])
def search_jobs():
    try:
        data = request.get_json()
        query = data.get('query', '').strip().lower()
        category_id = data.get('category_id')
        location = data.get('location', '').strip()
        job_type = data.get('job_type')
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        
        # Build the query
        sql = '''
            SELECT j.id, j.title, j.location, j.salary_min, j.salary_max, j.salary_type, 
                   j.job_type, j.experience_level, j.description, j.is_featured, j.posted_date,
                   c.name as company_name, c.logo as company_logo,
                   cat.name as category_name, cat.icon as category_icon
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            JOIN job_categories cat ON j.category_id = cat.id
            WHERE j.is_active = 1
        '''
        params = []
        
        if query:
            sql += ' AND (j.title LIKE ? OR j.description LIKE ? OR c.name LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
        if category_id:
            sql += ' AND j.category_id = ?'
            params.append(category_id)
        
        if location:
            sql += ' AND j.location LIKE ?'
            params.append(f'%{location}%')
        
        if job_type:
            sql += ' AND j.job_type = ?'
            params.append(job_type)
        
        if salary_min:
            sql += ' AND j.salary_max >= ?'
            params.append(salary_min)
        
        if salary_max:
            sql += ' AND j.salary_min <= ?'
            params.append(salary_max)
        
        sql += ' ORDER BY j.is_featured DESC, j.posted_date DESC'
        
        cursor.execute(sql, params)
        jobs = cursor.fetchall()
        conn.close()
        
        # Format results
        results = []
        for job in jobs:
            results.append({
                'id': job[0],
                'title': job[1],
                'location': job[2],
                'salary_min': job[3],
                'salary_max': job[4],
                'salary_type': job[5],
                'job_type': job[6],
                'experience_level': job[7],
                'description': job[8],
                'is_featured': bool(job[9]),
                'posted_date': job[10],
                'company_name': job[11],
                'company_logo': job[12],
                'category_name': job[13],
                'category_icon': job[14]
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-categories', methods=['GET'])
def get_categories():
    try:
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.description, c.icon, c.color, COUNT(j.id) as job_count
            FROM job_categories c
            LEFT JOIN jobs j ON c.id = j.category_id AND j.is_active = 1
            WHERE c.is_active = 1
            GROUP BY c.id
            ORDER BY job_count DESC
        ''')
        categories = cursor.fetchall()
        conn.close()
        
        results = []
        for cat in categories:
            results.append({
                'id': cat[0],
                'name': cat[1],
                'description': cat[2],
                'icon': cat[3],
                'color': cat[4],
                'job_count': cat[5]
            })
        
        return jsonify({'success': True, 'categories': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-companies', methods=['GET'])
def get_companies():
    try:
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.name, c.logo, c.description, c.website, c.location, 
                   c.industry, c.founded_year, c.employee_count, COUNT(j.id) as job_count
            FROM companies c
            LEFT JOIN jobs j ON c.id = j.company_id AND j.is_active = 1
            WHERE c.is_active = 1
            GROUP BY c.id
            ORDER BY job_count DESC
        ''')
        companies = cursor.fetchall()
        conn.close()
        
        results = []
        for comp in companies:
            results.append({
                'id': comp[0],
                'name': comp[1],
                'logo': comp[2],
                'description': comp[3],
                'website': comp[4],
                'location': comp[5],
                'industry': comp[6],
                'founded_year': comp[7],
                'employee_count': comp[8],
                'job_count': comp[9]
            })
        
        return jsonify({'success': True, 'companies': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-job/<int:job_id>', methods=['GET'])
def get_job_details(job_id):
    try:
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT j.*, c.name as company_name, c.logo as company_logo, 
                   c.description as company_description, c.website as company_website,
                   cat.name as category_name, cat.icon as category_icon
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            JOIN job_categories cat ON j.category_id = cat.id
            WHERE j.id = ? AND j.is_active = 1
        ''', (job_id,))
        job = cursor.fetchone()
        conn.close()
        
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        # Increment view count
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE jobs SET views = views + 1 WHERE id = ?', (job_id,))
        conn.commit()
        conn.close()
        
        job_data = {
            'id': job[0],
            'title': job[1],
            'company_id': job[2],
            'category_id': job[3],
            'location': job[4],
            'salary_min': job[5],
            'salary_max': job[6],
            'salary_type': job[7],
            'job_type': job[8],
            'experience_level': job[9],
            'description': job[10],
            'requirements': job[11],
            'benefits': job[12],
            'is_featured': bool(job[13]),
            'views': job[14],
            'applications_count': job[15],
            'posted_date': job[16],
            'company_name': job[17],
            'company_logo': job[18],
            'company_description': job[19],
            'company_website': job[20],
            'category_name': job[21],
            'category_icon': job[22]
        }
        
        return jsonify({'success': True, 'job': job_data}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/apply-job', methods=['POST'])
def apply_job():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Please login to apply'}), 401
        
        data = request.get_json()
        job_id = data.get('job_id')
        experience_years = data.get('experience_years')
        expected_salary = data.get('expected_salary')
        cover_letter = data.get('cover_letter', '').strip()
        
        if not job_id:
            return jsonify({'success': False, 'error': 'Job ID is required'}), 400
        
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        
        # Check if already applied
        cursor.execute('SELECT id FROM applications WHERE user_id = ? AND job_id = ?', 
                      (session['user_id'], job_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'You have already applied for this job'}), 409
        
        # Get user details
        cursor.execute('SELECT name, email, mobile FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        # Get job details
        cursor.execute('SELECT location FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            conn.close()
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        # Insert application
        cursor.execute('''
            INSERT INTO applications (job_id, user_id, name, email, mobile, location, 
                                   experience_years, expected_salary, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, session['user_id'], user[0], user[1], user[2], job[0], 
              experience_years, expected_salary, cover_letter))
        
        # Update job applications count
        cursor.execute('UPDATE jobs SET applications_count = applications_count + 1 WHERE id = ?', (job_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Application submitted successfully!'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/save-job', methods=['POST'])
def save_job():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Please login to save jobs'}), 401
        
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'success': False, 'error': 'Job ID is required'}), 400
        
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        
        # Check if already saved
        cursor.execute('SELECT id FROM saved_jobs WHERE user_id = ? AND job_id = ?', 
                      (session['user_id'], job_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Job already saved'}), 409
        
        # Save job
        cursor.execute('INSERT INTO saved_jobs (user_id, job_id) VALUES (?, ?)', 
                      (session['user_id'], job_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Job saved successfully!'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-saved-jobs', methods=['GET'])
def get_saved_jobs():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Please login to view saved jobs'}), 401
        
        conn = sqlite3.connect('12thfailjobs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT j.id, j.title, j.location, j.salary_min, j.salary_max, j.salary_type,
                   j.job_type, j.experience_level, j.description, j.is_featured, j.posted_date,
                   c.name as company_name, c.logo as company_logo,
                   cat.name as category_name, cat.icon as category_icon
            FROM saved_jobs sj
            JOIN jobs j ON sj.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            JOIN job_categories cat ON j.category_id = cat.id
            WHERE sj.user_id = ? AND j.is_active = 1
            ORDER BY sj.saved_date DESC
        ''', (session['user_id'],))
        jobs = cursor.fetchall()
        conn.close()
        
        results = []
        for job in jobs:
            results.append({
                'id': job[0],
                'title': job[1],
                'location': job[2],
                'salary_min': job[3],
                'salary_max': job[4],
                'salary_type': job[5],
                'job_type': job[6],
                'experience_level': job[7],
                'description': job[8],
                'is_featured': bool(job[9]),
                'posted_date': job[10],
                'company_name': job[11],
                'company_logo': job[12],
                'category_name': job[13],
                'category_icon': job[14]
            })
        
        return jsonify({'success': True, 'jobs': results}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/contact', methods=['POST'])
def contact_us():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # Validation
        if not name or not email or not subject or not message:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        if not validate_email(email):
            return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
        
        # In a real application, you would send an email here
        # For now, we'll just return success
        
        return jsonify({'success': True, 'message': 'Thank you for your message! We will get back to you soon.'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Starting 12thFailJobs Backend Server...")
    print("📊 Database initialized: 12thfailjobs.db")
    print("🔗 API Endpoints:")
    print("   POST /signup - User registration")
    print("   POST /login - User authentication")
    print("   POST /logout - User logout")
    print("   GET  /check-auth - Check authentication status")
    print("   POST /submit-application - Submit job application")
    print("   GET  /view-applications - View all applications")
    print("   POST /search-jobs - Search jobs")
    print("🌐 Server running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 