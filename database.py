import sqlite3, hashlib, secrets
from datetime import datetime, date
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000)
    return salt + "$" + digest.hex()

def verify_password(password, stored):
    try:
        salt, digest = stored.split("$",1)
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000)
        return secrets.compare_digest(check.hex(), digest)
    except Exception:
        return False

def init_db():
    conn=get_connection(); c=conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
      full_name TEXT NOT NULL, password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'User', active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS categories(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      type TEXT NOT NULL CHECK(type IN ('Income','Expense')),
      UNIQUE(name,type));
    CREATE TABLE IF NOT EXISTS transactions(
      id INTEGER PRIMARY KEY AUTOINCREMENT, trans_date TEXT NOT NULL,
      trans_type TEXT NOT NULL CHECK(trans_type IN ('Income','Expense')),
      category_id INTEGER NOT NULL, amount REAL NOT NULL,
      details TEXT DEFAULT '', reference_no TEXT DEFAULT '',
      recurring_id INTEGER, created_by INTEGER, created_at TEXT NOT NULL,
      FOREIGN KEY(category_id) REFERENCES categories(id),
      FOREIGN KEY(created_by) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS recurring_transactions(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      trans_type TEXT NOT NULL CHECK(trans_type IN ('Income','Expense')),
      category_id INTEGER NOT NULL, amount REAL NOT NULL,
      details TEXT DEFAULT '', day_of_month INTEGER NOT NULL DEFAULT 1,
      start_date TEXT NOT NULL, end_date TEXT, active INTEGER NOT NULL DEFAULT 1,
      last_generated TEXT, created_by INTEGER,
      FOREIGN KEY(category_id) REFERENCES categories(id),
      FOREIGN KEY(created_by) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS opening_balances(
      id INTEGER PRIMARY KEY AUTOINCREMENT, balance_date TEXT UNIQUE NOT NULL,
      amount REAL NOT NULL, details TEXT DEFAULT '', created_by INTEGER,
      created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS invoices(
      id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_no TEXT UNIQUE NOT NULL,
      invoice_date TEXT NOT NULL, customer_name TEXT NOT NULL,
      customer_address TEXT DEFAULT '', customer_phone TEXT DEFAULT '',
      customer_email TEXT DEFAULT '', description TEXT DEFAULT '',
      amount REAL NOT NULL, tax REAL NOT NULL DEFAULT 0,
      total REAL NOT NULL, notes TEXT DEFAULT '', created_by INTEGER,
      created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS company_settings(
      id INTEGER PRIMARY KEY CHECK(id=1), company_name TEXT NOT NULL DEFAULT 'My Company',
      address TEXT DEFAULT '', phone TEXT DEFAULT '', email TEXT DEFAULT '',
      gstin TEXT DEFAULT '', logo_path TEXT DEFAULT '', currency_symbol TEXT DEFAULT '₹');
    """)
    if not c.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        c.execute("INSERT INTO users(username,full_name,password_hash,role,active,created_at) VALUES(?,?,?,?,?,?)",
                  ("admin","Administrator",hash_password("admin123"),"Admin",1,datetime.now().isoformat()))
    for n,t in [("Salary","Income"),("Business Income","Income"),("Interest","Income"),("Other Income","Income"),
                ("Food","Expense"),("Travel","Expense"),("Rent","Expense"),("Electricity","Expense"),
                ("Medical","Expense"),("Education","Expense"),("Shopping","Expense"),("Other Expense","Expense")]:
        c.execute("INSERT OR IGNORE INTO categories(name,type) VALUES(?,?)",(n,t))
    c.execute("INSERT OR IGNORE INTO company_settings(id,company_name) VALUES(1,'My Company')")
    conn.commit(); conn.close()

def authenticate(username,password):
    conn=get_connection(); r=conn.execute("SELECT * FROM users WHERE username=? AND active=1",(username.strip(),)).fetchone(); conn.close()
    return dict(r) if r and verify_password(password,r["password_hash"]) else None

def get_users():
    conn=get_connection(); r=conn.execute("SELECT id,username,full_name,role,active,created_at FROM users ORDER BY username").fetchall(); conn.close(); return r
def add_user(username,full_name,password,role):
    conn=get_connection()
    try:
        conn.execute("INSERT INTO users(username,full_name,password_hash,role,active,created_at) VALUES(?,?,?,?,?,?)",
                     (username.strip(),full_name.strip(),hash_password(password),role,1,datetime.now().isoformat())); conn.commit()
        return True,"User created."
    except sqlite3.IntegrityError: return False,"Username already exists."
    finally: conn.close()
def update_user_status(uid,active):
    conn=get_connection(); conn.execute("UPDATE users SET active=? WHERE id=?",(int(active),uid)); conn.commit(); conn.close()
def change_password(uid,pw):
    conn=get_connection(); conn.execute("UPDATE users SET password_hash=? WHERE id=?",(hash_password(pw),uid)); conn.commit(); conn.close()

def get_categories(typ=None):
    conn=get_connection()
    r=conn.execute("SELECT * FROM categories"+(" WHERE type=? ORDER BY name" if typ else " ORDER BY type,name"),(typ,) if typ else ()).fetchall()
    conn.close(); return r
def add_category(name,typ):
    conn=get_connection()
    try:
        conn.execute("INSERT INTO categories(name,type) VALUES(?,?)",(name.strip(),typ)); conn.commit(); return True,"Category added."
    except sqlite3.IntegrityError: return False,"Category already exists."
    finally: conn.close()
def delete_category(cid):
    conn=get_connection()
    if conn.execute("SELECT 1 FROM transactions WHERE category_id=? LIMIT 1",(cid,)).fetchone():
        conn.close(); return False,"Category is used by a transaction."
    conn.execute("DELETE FROM categories WHERE id=?",(cid,)); conn.commit(); conn.close(); return True,"Category deleted."

def add_transaction(d,t,cid,amount,details="",reference_no="",user_id=None,recurring_id=None):
    conn=get_connection(); conn.execute("""INSERT INTO transactions
    (trans_date,trans_type,category_id,amount,details,reference_no,recurring_id,created_by,created_at)
    VALUES(?,?,?,?,?,?,?,?,?)""",(str(d),t,cid,float(amount),details,reference_no,recurring_id,user_id,datetime.now().isoformat()))
    conn.commit(); conn.close()

def update_transaction(i,d,t,cid,amount,details,reference_no):
    conn=get_connection(); conn.execute("""UPDATE transactions SET trans_date=?,trans_type=?,category_id=?,
    amount=?,details=?,reference_no=? WHERE id=?""",(str(d),t,cid,float(amount),details,reference_no,i)); conn.commit(); conn.close()
def delete_transaction(i):
    conn=get_connection(); conn.execute("DELETE FROM transactions WHERE id=?",(i,)); conn.commit(); conn.close()

def get_transactions(start=None,end=None,typ=None,category_id=None):
    conn=get_connection(); sql="""SELECT t.*,c.name category,u.username FROM transactions t
    JOIN categories c ON c.id=t.category_id LEFT JOIN users u ON u.id=t.created_by WHERE 1=1"""; p=[]
    if start: sql+=" AND date(t.trans_date)>=date(?)"; p.append(str(start))
    if end: sql+=" AND date(t.trans_date)<=date(?)"; p.append(str(end))
    if typ: sql+=" AND t.trans_type=?"; p.append(typ)
    if category_id: sql+=" AND t.category_id=?"; p.append(category_id)
    sql+=" ORDER BY date(t.trans_date) DESC,t.id DESC"
    r=conn.execute(sql,p).fetchall(); conn.close(); return r

def summary(start=None,end=None):
    rows=get_transactions(start,end); inc=sum(r["amount"] for r in rows if r["trans_type"]=="Income"); exp=sum(r["amount"] for r in rows if r["trans_type"]=="Expense")
    return inc,exp,inc-exp

def get_opening_balance(d=None):
    conn=get_connection()
    if d:
        r=conn.execute("SELECT COALESCE(SUM(amount),0) amount FROM opening_balances WHERE date(balance_date)<=date(?)",(str(d),)).fetchone()
    else: r=conn.execute("SELECT COALESCE(SUM(amount),0) amount FROM opening_balances").fetchone()
    conn.close(); return float(r["amount"])

def get_opening_rows():
    conn=get_connection(); r=conn.execute("SELECT * FROM opening_balances ORDER BY balance_date DESC").fetchall(); conn.close(); return r
def add_opening_balance(d,amount,details,user_id):
    conn=get_connection(); conn.execute("INSERT OR REPLACE INTO opening_balances(balance_date,amount,details,created_by,created_at) VALUES(?,?,?,?,?)",(str(d),float(amount),details,user_id,datetime.now().isoformat())); conn.commit(); conn.close()

def add_recurring(name,typ,cid,amount,details,day,start,end,user_id):
    conn=get_connection(); conn.execute("""INSERT INTO recurring_transactions
    (name,trans_type,category_id,amount,details,day_of_month,start_date,end_date,active,created_by)
    VALUES(?,?,?,?,?,?,?,?,1,?)""",(name,typ,cid,float(amount),details,int(day),str(start),str(end) if end else None,user_id)); conn.commit(); conn.close()
def get_recurring():
    conn=get_connection(); r=conn.execute("""SELECT r.*,c.name category FROM recurring_transactions r JOIN categories c ON c.id=r.category_id ORDER BY r.active DESC,r.name""").fetchall(); conn.close(); return r
def toggle_recurring(i,active):
    conn=get_connection(); conn.execute("UPDATE recurring_transactions SET active=? WHERE id=?",(int(active),i)); conn.commit(); conn.close()
def delete_recurring(i):
    conn=get_connection(); conn.execute("DELETE FROM recurring_transactions WHERE id=?",(i,)); conn.commit(); conn.close()

def generate_recurring_until(target_date,user_id):
    # Idempotently creates each due occurrence through target month.
    target=date.fromisoformat(str(target_date))
    conn=get_connection(); rows=conn.execute("SELECT * FROM recurring_transactions WHERE active=1").fetchall()
    count=0
    for r in rows:
        y,m=target.year,target.month
        from calendar import monthrange
        day=min(r["day_of_month"],monthrange(y,m)[1])
        due=date(y,m,day)
        start=date.fromisoformat(r["start_date"])
        if due<start or (r["end_date"] and due>date.fromisoformat(r["end_date"])): continue
        exists=conn.execute("SELECT 1 FROM transactions WHERE recurring_id=? AND trans_date=?",(r["id"],due.isoformat())).fetchone()
        if not exists:
            conn.execute("""INSERT INTO transactions(trans_date,trans_type,category_id,amount,details,reference_no,recurring_id,created_by,created_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",(due.isoformat(),r["trans_type"],r["category_id"],r["amount"],r["details"],"RECURRING",r["id"],user_id,datetime.now().isoformat()))
            count+=1
        conn.execute("UPDATE recurring_transactions SET last_generated=? WHERE id=?",(due.isoformat(),r["id"]))
    conn.commit(); conn.close(); return count

def get_company():
    conn=get_connection(); r=conn.execute("SELECT * FROM company_settings WHERE id=1").fetchone(); conn.close(); return r
def save_company(name,address,phone,email,gstin,logo,currency):
    conn=get_connection(); conn.execute("""UPDATE company_settings SET company_name=?,address=?,phone=?,email=?,gstin=?,logo_path=?,currency_symbol=? WHERE id=1""",(name,address,phone,email,gstin,logo,currency)); conn.commit(); conn.close()

def next_invoice_no():
    conn=get_connection(); r=conn.execute("SELECT invoice_no FROM invoices ORDER BY id DESC LIMIT 1").fetchone(); conn.close()
    if not r: return "INV-0001"
    try: return f"INV-{int(r['invoice_no'].split('-')[-1])+1:04d}"
    except: return f"INV-{datetime.now():%Y%m%d%H%M%S}"

def add_invoice(no,d,customer,address,phone,email,desc,amount,tax,total,notes,user):
    conn=get_connection(); conn.execute("""INSERT INTO invoices(invoice_no,invoice_date,customer_name,customer_address,customer_phone,customer_email,description,amount,tax,total,notes,created_by,created_at)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",(no,str(d),customer,address,phone,email,desc,float(amount),float(tax),float(total),notes,user,datetime.now().isoformat())); conn.commit(); conn.close()
def get_invoices():
    conn=get_connection(); r=conn.execute("SELECT * FROM invoices ORDER BY date(invoice_date) DESC,id DESC").fetchall(); conn.close(); return r
def get_invoice(i):
    conn=get_connection(); r=conn.execute("SELECT * FROM invoices WHERE id=?",(i,)).fetchone(); conn.close(); return r
