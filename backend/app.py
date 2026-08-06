from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "super_secret_pharmacy_key"

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root@1234",
    database="pharma"
)
cursor = db.cursor(dictionary=True)

# ==========================================
#       AUTHENTICATION (LOGIN / LOGOUT / SIGNUP)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['loggedin'] = True
            session['uid'] = user['uid']
            session['shop_name'] = user['shop_name']
            return redirect('/')
        else:
            return "❌ Invalid Credentials! Please go back and try again."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        shop_name = request.form['shop_name']
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return "❌ Username already taken!"
            
        cursor.execute("INSERT INTO users (username, password, shop_name) VALUES (%s, %s, %s)", (username, password, shop_name))
        db.commit()
        return redirect('/login')
    return render_template('signup.html')

# ==========================================
#       SECURE DASHBOARD
# ==========================================
@app.route('/')
def home():
    if 'loggedin' not in session:
        return redirect('/login')
        
    uid = session['uid'] # Current logged-in user ki ID

    # Ab sirf is specific user ka data count hoga
    cursor.execute("SELECT COUNT(*) AS total_medicines FROM medicine WHERE owner_id=%s", (uid,))
    total_medicines = cursor.fetchone()['total_medicines']

    cursor.execute("SELECT SUM(stock) AS total_stock FROM medicine WHERE owner_id=%s", (uid,))
    total_stock = cursor.fetchone()['total_stock'] or 0

    cursor.execute("SELECT COUNT(*) AS total_suppliers FROM supplier WHERE owner_id=%s", (uid,))
    total_suppliers = cursor.fetchone()['total_suppliers']

    cursor.execute("SELECT COUNT(*) AS total_customers FROM customer WHERE owner_id=%s", (uid,))
    total_customers = cursor.fetchone()['total_customers']

    cursor.execute("SELECT SUM(price * stock) AS total_value FROM medicine WHERE owner_id=%s", (uid,))
    total_value = cursor.fetchone()['total_value'] or 0

    return render_template(
        'home.html',
        total_medicines=total_medicines,
        total_stock=total_stock,
        total_suppliers=total_suppliers,  
        total_customers=total_customers,
        total_value=total_value
    )

# ==========================================
#       MEDICINES
# ==========================================
@app.route('/medicines')
def medicines():
    if 'loggedin' not in session: return redirect('/login')
    
    cursor.execute("SELECT * FROM medicine WHERE owner_id=%s", (session['uid'],))
    data = cursor.fetchall()
    return render_template('medicines.html', medicines=data)

@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    mname = request.form['mname']
    category = request.form['category']
    price = request.form['price']
    stock = request.form['stock']
    expiry_date = request.form['expiry_date']
    sid = request.form['sid']
    uid = session['uid'] # Kis user ne add kiya

    cursor.execute("SELECT IFNULL(MAX(mid), 0) + 1 AS next_id FROM medicine")
    next_id = cursor.fetchone()["next_id"]

    cursor.execute("""
        INSERT INTO medicine (mid, mname, category, price, stock, expiry_date, sid, owner_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (next_id, mname, category, price, stock, expiry_date, sid, uid))
    
    db.commit()
    return redirect('/medicines')

# ==========================================
#       SUPPLIERS
# ==========================================
@app.route('/suppliers')
def suppliers():
    if 'loggedin' not in session: return redirect('/login')
    cursor.execute("SELECT * FROM supplier WHERE owner_id=%s", (session['uid'],))
    suppliers = cursor.fetchall()
    return render_template('suppliers.html', suppliers=suppliers)

# ==========================================
#       CUSTOMERS + AUDIT
# ==========================================
@app.route('/customers')
def customers():
    if 'loggedin' not in session: return redirect('/login')
    
    cursor.execute("SELECT * FROM customer WHERE owner_id=%s ORDER BY cid ASC", (session['uid'],))
    customers = cursor.fetchall()

    try:
        cursor.execute("SELECT * FROM customer_audit WHERE owner_id=%s ORDER BY action_time DESC", (session['uid'],))
        audit = cursor.fetchall()
    except:
        audit = []

    return render_template('customers.html', customers=customers, audit=audit)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    try:
        cname = request.form['cname']
        caddress = request.form['caddress']
        cphone = request.form['cphone']
        uid = session['uid']

        cursor.execute("SELECT IFNULL(MAX(cid), 0) + 1 AS next_id FROM customer")
        next_id = cursor.fetchone()['next_id']

        cursor.execute("""
            INSERT INTO customer (cid, cname, caddress, cphone, owner_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (next_id, cname, caddress, cphone, uid))

        cursor.execute("""
            INSERT INTO customer_audit (customer_id, customer_name, action, owner_id)
            VALUES (%s, %s, %s, %s)
        """, (next_id, cname, 'Added', uid))

        db.commit()
    except Exception as e:
        print("❌ ERROR while adding customer:", e)

    return redirect('/customers')

# ==========================================
#       ALERTS (LOW STOCK & EXPIRY)
# ==========================================
@app.route('/lowstock')
def low_stock():
    if 'loggedin' not in session: return redirect('/login')
    cursor.execute("""
        SELECT mname, category, price, stock 
        FROM medicine 
        WHERE stock < 50 AND owner_id=%s
        ORDER BY stock ASC
    """, (session['uid'],))
    data = cursor.fetchall()
    return render_template('lowstock.html', data=data)

@app.route('/expiry_alert')
def expiry_alert():
    if 'loggedin' not in session: return redirect('/login')
    cursor.execute("""
        SELECT mname, category, price, expiry_date
        FROM medicine
        WHERE expiry_date <= (CURDATE() + INTERVAL 60 DAY) AND owner_id=%s
        ORDER BY expiry_date ASC
    """, (session['uid'],))
    data = cursor.fetchall()
    return render_template('expiry_alert.html', data=data)

# ==========================================
#       DELIVERY PERSON
# ==========================================
@app.route('/delivery')
def delivery():
    if 'loggedin' not in session: return redirect('/login')
    cursor.execute("SELECT * FROM deliveryperson WHERE owner_id=%s", (session['uid'],))
    data = cursor.fetchall()
    return render_template('delivery.html', data=data)

@app.route('/add_delivery', methods=['POST'])
def add_delivery():
    try:
        dname = request.form['dname']
        daddress = request.form['daddress']
        dphone = request.form['dphone']
        registration = request.form.get('registration')
        uid = session['uid']

        cursor.execute("SELECT IFNULL(MAX(did), 0) + 1 AS next_id FROM deliveryperson")
        next_id = cursor.fetchone()["next_id"]

        cursor.execute("""
            INSERT INTO deliveryperson (did, dname, daddress, dphone, registration, owner_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (next_id, dname, daddress, dphone, registration, uid))

        db.commit()
    except Exception as e:
        print("❌ Error while adding delivery person:", e)

    return redirect('/delivery')

# ==========================================
#       SALES SUMMARY
# ==========================================
@app.route("/sales")
def sales_summary():
    # Security check
    if 'loggedin' not in session: return redirect('/login')
    uid = session['uid'] 
    
    # Sirf logged-in user ki sales calculate karein
    cursor.execute("""
        SELECT 
            IFNULL(SUM(om.quantity * m.price), 0) AS total_sales,
            COUNT(DISTINCT o.oid) AS total_orders
        FROM order_medicine om
        JOIN medicine m ON om.mid = m.mid
        JOIN orders o ON om.oid = o.oid
        WHERE m.owner_id = %s;
    """, (uid,))
    result = cursor.fetchone()

    # Sirf logged-in user ki top medicines dikhayein
    cursor.execute("""
        SELECT 
            m.mname AS medicine_name,
            SUM(om.quantity) AS total_quantity_sold,
            SUM(om.quantity * m.price) AS total_revenue
        FROM order_medicine om
        JOIN medicine m ON om.mid = m.mid
        WHERE m.owner_id = %s
        GROUP BY m.mname
        ORDER BY total_quantity_sold DESC
        LIMIT 5;
    """, (uid,))
    top_medicines = cursor.fetchall()

    return render_template("sales.html", sales=result, top_medicines=top_medicines)

# ==========================================
#       BULK UPLOAD ROUTES (CSV)
# ==========================================

# 1. BULK UPLOAD CUSTOMERS
@app.route('/upload_csv_customers', methods=['POST'])
def upload_csv_customers():
    if 'loggedin' not in session: return redirect('/login')
    file = request.files['csv_file']
    if not file: return "❌ File missing!"

    try:
        df = pd.read_csv(file)
        df = df.fillna('') # Khali cells ko handle karne ke liye
        uid = session['uid']

        for index, row in df.iterrows():
            cursor.execute("SELECT IFNULL(MAX(cid), 0) + 1 AS next_id FROM customer")
            next_id = cursor.fetchone()["next_id"]
            
            cname = row['cname']
            
            # Customer add karein
            cursor.execute("""
                INSERT INTO customer (cid, cname, caddress, cphone, owner_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (next_id, cname, row['caddress'], row['cphone'], uid))

            # Audit table mein bhi entry daalein (Bulk added)
            cursor.execute("""
                INSERT INTO customer_audit (customer_id, customer_name, action, owner_id)
                VALUES (%s, %s, %s, %s)
            """, (next_id, cname, 'Bulk Added via CSV', uid))
            
        db.commit()
    except Exception as e:
        return f"❌ Error in Customer CSV: {e}"
    return redirect('/customers')


# 2. BULK UPLOAD SUPPLIERS
@app.route('/upload_csv_suppliers', methods=['POST'])
def upload_csv_suppliers():
    if 'loggedin' not in session: return redirect('/login')
    file = request.files['csv_file']
    if not file: return "❌ File missing!"

    try:
        df = pd.read_csv(file)
        df = df.fillna('')
        uid = session['uid']

        for index, row in df.iterrows():
            cursor.execute("SELECT IFNULL(MAX(sid), 0) + 1 AS next_id FROM supplier")
            next_id = cursor.fetchone()["next_id"]

            cursor.execute("""
                INSERT INTO supplier (sid, sname, sphone, saddress, owner_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (next_id, row['sname'], row['sphone'], row['saddress'], uid))
            
        db.commit()
    except Exception as e:
        return f"❌ Error in Supplier CSV: {e}"
    return redirect('/suppliers')


# 3. BULK UPLOAD DELIVERY PERSON
@app.route('/upload_csv_delivery', methods=['POST'])
def upload_csv_delivery():
    if 'loggedin' not in session: return redirect('/login')
    file = request.files['csv_file']
    if not file: return "❌ File missing!"

    try:
        df = pd.read_csv(file)
        df = df.fillna('')
        uid = session['uid']

        for index, row in df.iterrows():
            cursor.execute("SELECT IFNULL(MAX(did), 0) + 1 AS next_id FROM deliveryperson")
            next_id = cursor.fetchone()["next_id"]

            cursor.execute("""
                INSERT INTO deliveryperson (did, dname, daddress, dphone, registration, owner_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (next_id, row['dname'], row['daddress'], row['dphone'], row.get('registration', ''), uid))
            
        db.commit()
    except Exception as e:
        return f"❌ Error in Delivery CSV: {e}"
    return redirect('/delivery')

if __name__ == '__main__':
    app.run(debug=True)