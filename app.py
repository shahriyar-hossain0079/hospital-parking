from flask import Flask, request, redirect, session, render_template_string
import csv, os, math
from datetime import datetime

HOSPITAL_NAME = "City Hospital Parking"
OWNER_NAME = "City Hospital Ltd."
PRICE_BIKE = 20
PRICE_CAR = 50
ADMIN_PASS = "admin123"
OPERATOR_PASS = "1234"

app = Flask(__name__)
app.secret_key = "parking_secret_123"
FILE = "parking_data.csv"

if not os.path.exists(FILE):
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["Number","Type","Entry","Exit","Bill"])

def get_data():
    if not os.path.exists(FILE): return []
    with open(FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

LOGIN = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#eef2f7;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.card{background:white;padding:30px;border-radius:15px;box-shadow:0 5px 20px rgba(0,0,0,0.1);width:320px;text-align:center}
input{width:90%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #ccc}
button{width:95%;padding:12px;background:#007bff;color:white;border:none;border-radius:8px;font-size:16px}</style></head>
<body><div class="card"><h2>City Hospital</h2>
<form method="post"><input type="password" name="password" placeholder="পাসওয়ার্ড" required><button>Login</button></form>
<p style="font-size:12px;color:gray">Admin: admin123 | Operator: 1234</p></div></body></html>
"""

MAIN = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#f5f7fb;padding:10px;margin:0}
.header{background:#007bff;color:white;padding:15px;border-radius:10px;text-align:center}
.box{background:white;padding:15px;border-radius:10px;margin:10px 0}
input,select{width:100%;padding:12px;margin:5px 0;border-radius:8px;border:1px solid #ddd;box-sizing:border-box}
.btn{padding:12px;border:none;border-radius:8px;color:white;width:100%;font-size:16px}
.btn-entry{background:#28a745}.btn-exit{background:#dc3545}.btn-print{background:#17a2b8}
table{width:100%;background:white;border-collapse:collapse;border-radius:10px;overflow:hidden}
th{background:#007bff;color:white}th,td{padding:10px;border-bottom:1px solid #eee;text-align:center;font-size:14px}
.receipt{background:white;width:320px;margin:20px auto;padding:20px;border-radius:10px;border:2px dashed #333;text-align:center}
@media print{.no-print{display:none!important}body{background:white}}
</style></head><body>
<div class="header"><h2>{{hname}}</h2><small>{{oname}}</small></div>
{% if bill %}
<div class="receipt"><h2>{{hname}}</h2><p>{{oname}}</p><hr>
<p><b>গাড়ি নং:</b> {{bill.Number}}</p><p><b>ধরন:</b> {{bill.Type}}</p>
<p><b>প্রবেশ:</b> {{bill.Entry}}</p><p><b>বাহির:</b> {{bill.Exit}}</p><hr>
<h2>মোট বিল: {{bill.Bill}} টাকা</h2><p>ধন্যবাদ</p><p style="font-size:11px">{{now}}</p></div>
<div class="no-print" style="text-align:center">
<button class="btn btn-print" style="width:200px" onclick="window.print()">প্রিন্ট করুন</button><br><br>
<a href="/"><button class="btn" style="background:gray;width:200px">ড্যাশবোর্ড</button></a></div>
<script>window.onload=function(){setTimeout(()=>window.print(),600);}</script>
{% else %}
<div class="box">
<form method="post" action="/entry">
<input name="number" placeholder="গাড়ির নম্বর" required>
<select name="type"><option value="Bike">Bike - {{bike}} Tk</option><option value="Car">Car - {{car}} Tk</option></select>
<button class="btn btn-entry">প্রবেশ</button></form></div>
<div class="box"><table><tr><th>নম্বর</th><th>ধরন</th><th>অবস্থা</th><th>Action</th></tr>
{% for r in data[::-1] %}<tr><td><b>{{r.Number}}</b></td><td>{{r.Type}}</td><td>{{'✅ '+r.Bill+' Tk' if r.Exit else 'ভিতরে'}}</td>
<td>{% if not r.Exit %}<a href="/exit/{{r.Number}}"><button class="btn btn-exit" style="padding:6px">বাহির</button></a>
{% else %}<a href="/bill/{{r.Number}}"><button class="btn btn-print" style="padding:6px">রশিদ</button></a>{% endif %}</td></tr>
{% endfor %}</table></div>
<div class="no-print" style="text-align:center"><br><a href="/logout">Logout</a></div>
{% endif %}</body></html>
"""

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        p=request.form.get("password")
        if p==ADMIN_PASS or p==OPERATOR_PASS:
            session["login"]=True
            return redirect("/")
    return render_template_string(LOGIN)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    if not session.get("login"): return redirect("/login")
    return render_template_string(MAIN, data=get_data(), hname=HOSPITAL_NAME, oname=OWNER_NAME, bike=PRICE_BIKE, car=PRICE_CAR, bill=None)

@app.route("/entry", methods=["POST"])
def entry():
    if not session.get("login"): return redirect("/login")
    num=request.form.get("number").strip().upper()
    typ=request.form.get("type")
    with open(FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([num, typ, datetime.now().strftime("%Y-%m-%d %H:%M"), "", ""])
    return redirect("/")

@app.route("/exit/<number>")
def exit_car(number):
    if not session.get("login"): return redirect("/login")
    rows=get_data()
    for r in rows:
        if r["Number"]==number and not r["Exit"]:
            import math
            e=datetime.strptime(r["Entry"], "%Y-%m-%d %H:%M")
            h=math.ceil((datetime.now()-e).total_seconds()/3600)
            if h<1: h=1
            bill=h*(PRICE_BIKE if r["Type"]=="Bike" else PRICE_CAR)
            r["Exit"]=datetime.now().strftime("%Y-%m-%d %H:%M")
            r["Bill"]=str(bill)
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=["Number","Type","Entry","Exit","Bill"])
        w.writeheader(); w.writerows(rows)
    return redirect(f"/bill/{number}")

@app.route("/bill/<number>")
def bill_page(number):
    if not session.get("login"): return redirect("/login")
    for r in get_data():
        if r["Number"]==number:
            return render_template_string(MAIN, bill=r, hname=HOSPITAL_NAME, oname=OWNER_NAME, now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data=[], bike=PRICE_BIKE, car=PRICE_CAR)
    return "Not Found"

if __name__=="__main__":
    app.run()
