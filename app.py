== এখানেই কাস্টমারের জন্য চেঞ্জ করবা ===
HOSPITAL_NAME = "City Hospital Parking"
OWNER_NAME = "City Hospital"
LOGO_EMOJI = "🏥"
PRICE_BIKE = 20
PRICE_CAR = 50
ADMIN_PASS = "admin123"
OPERATOR_PASS = "1234"
# =========================================

from flask import Flask, request, redirect, session
import csv, os, math
from datetime import datetime
from fpdf import FPDF
app = Flask(__name__)
app.secret_key = "sell123"
FILE = "parking_data.csv"
if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["Number","Type","Entry","Exit","Bill"])

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        p=request.form["password"]
        if p==ADMIN_PASS: session["role"]="admin"; return redirect("/")
        elif p==OPERATOR_PASS: session["role"]="operator"; return redirect("/")
        else: return "<h3>ভুল পাসওয়ার্ড</h3>"
    return f"<html><body style='text-align:center;margin-top:80px;font-family:Arial'><h2>{LOGO_EMOJI} {HOSPITAL_NAME}</h2><form method='POST'><input type='password' name='password' placeholder='পাসওয়ার্ড' style='padding:12px'><br><br><button style='padding:12px 30px;background:green;color:white'>Login</button></form><p>Admin: {ADMIN_PASS} | Operator: {OPERATOR_PASS}</p></body></html>"

@app.route("/")
def home():
    if "role" not in session: return redirect("/login")
    inside=[]; income=0
    with open(FILE, encoding="utf-8") as f:
        for r in list(csv.DictReader(f))[::-1]:
            if not r["Exit"]: inside.append(r)
            if r["Bill"]:
                try: income+=int(r["Bill"])
                except: pass
    rows="".join([f"<tr><td>{r['Number']}</td><td>{r['Type']}</td><td>{r['Entry']}</td></tr>" for r in inside])
    return f"<html><body style='text-align:center;font-family:Arial'><h2>{HOSPITAL_NAME} - Dashboard</h2><p>ভিতরে: {len(inside)} | আজকের আয়: {income} Tk | <a href='/logout'>Logout</a></p><form method='POST' action='/entry'><input name='number' placeholder='গাড়ির নাম্বার' required><select name='type'><option>Bike - {PRICE_BIKE}Tk</option><option>Car - {PRICE_CAR}Tk</option><option>CNG</option><option>Bus</option><option>Ambulance</option></select><button>Entry</button></form><form method='POST' action='/exit'><input name='number' placeholder='Exit নাম্বার' required><button>Exit + Bill Print</button></form><table border=1 style='margin:auto'><tr><th>Number</th><th>Type</th><th>Entry</th></tr>{rows}</table></body></html>"

@app.route("/entry", methods=["POST"])
def entry():
    n=request.form["number"].upper(); t=request.form["type"].split(" - ")[0]
    with open(FILE, "a", newline="", encoding="utf-8") as f: csv.writer(f).writerow([n, t, datetime.now().strftime("%Y-%m-%d %I:%M %p"), "", "0"])
    return redirect("/")

@app.route("/exit", methods=["POST"])
def exit_car():
    n=request.form["number"].upper()
    rows=list(csv.DictReader(open(FILE, encoding="utf-8")))
    for r in rows:
        if r["Number"]==n and not r["Exit"]:
            price={"Bike":PRICE_BIKE,"Car":PRICE_CAR,"CNG":30,"Bus":100,"Ambulance":0}.get(r["Type"],50)
            r["Exit"]=datetime.now().strftime("%Y-%m-%d %I:%M %p"); r["Bill"]=price
            pdf=FPDF(); pdf.add_page(); pdf.set_font("Arial",size=12)
            pdf.cell(200,10,txt=f"{HOSPITAL_NAME} - {OWNER_NAME}",ln=True,align='C')
            pdf.cell(200,10,txt=f"Bill for {r['Number']} - {price} Tk",ln=True)
            pdf.output(f"Bill_{n}.pdf")
            with open(FILE,"w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=["Number","Type","Entry","Exit","Bill"]); w.writeheader(); w.writerows(rows)
            return f"<h2>Bill {price} Tk Done</h2><a href='/'>Back</a>"
    return f"<h3>{n} পাওয়া যায়নি</h3><a href='/'>Back</a>"

@app.route("/logout")
def logout():
    session.clear(); return redirect("/login")
app.run(host="0.0.0.0", port=5000)
