"""
להלן אותה תשובה מסודרת, מתומצתת ופרקטית, עם תוספת של פעולות בסיסיות יומיומיות כמו: הצגת DBs, טבלאות, סכמות, קולקשנים, אינדקסים, דוגמאות CRUD, ועוד.


---

1) בסיס לינוקס לתפעול DB (RHEL)

שירותים (systemd)

מה זה: ניהול הפעלה/עצירה/לוגים של שירותי DB.


sudo systemctl status postgresql
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl restart postgresql
sudo journalctl -u postgresql -n 200 --no-pager

sudo systemctl status mongod
sudo systemctl restart mongod
sudo journalctl -u mongod -n 200 --no-pager

רשת/פורט

מה זה: בדיקה מי מאזין על הפורט + פתיחה בפיירוול.


ss -tulnp | egrep '5432|27017'
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=5432/tcp --permanent
sudo firewall-cmd --add-port=27017/tcp --permanent
sudo firewall-cmd --reload

דיסק/זיכרון

מה זה: DB נופלים מהר כשדיסק מלא (במיוחד WAL/לוגים).


df -h
free -m
du -sh /var/lib/pgsql/data/pg_wal 2>/dev/null


---

2) PostgreSQL – תפעול בסיסי (CLI: psql)

כניסה

sudo -u postgres psql

הצגת DBs / משתמשים / סכמות

מה זה: ניווט בסיסי במסד.


\l          -- כל הדאטאבייסים
\du         -- משתמשים/תפקידים (roles)
\dn         -- סכמות (schemas)
\c appdb    -- התחברות לדאטאבייס

הצגת טבלאות / מבנה / נתונים

מה זה: לראות מה קיים ומה העמודות.


\dt             -- טבלאות בסכמה הנוכחית
\dt public.*    -- כל הטבלאות ב-public
\d students     -- מבנה טבלה (עמודות, types)
\d+ students    -- מבנה + עוד פרטים (storage וכו')
SELECT * FROM students LIMIT 20;   -- הצגת נתונים

אינדקסים, constraints, sequences, views

\di             -- אינדקסים
\ds             -- sequences (SERIAL/IDENTITY)
\dv             -- views
\dp             -- הרשאות על אובייקטים

CRUD קצר (דוגמה)

CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  grade INT
);

INSERT INTO students (name, grade) VALUES ('Yali', 95);

SELECT * FROM students WHERE grade >= 90;

UPDATE students SET grade = 98 WHERE name = 'Yali';

DELETE FROM students WHERE name = 'Yali';

טרנזקציות

מה זה: שינוי קבוצתי עם rollback אם משהו נשבר.


BEGIN;
UPDATE students SET grade = grade + 1;
-- אם הכל טוב:
COMMIT;
-- אם לא:
ROLLBACK;

גיבוי בסיסי (לוגי)

pg_dump -Fc -d appdb -f /backup/appdb.dump
pg_restore -d appdb /backup/appdb.dump


---

3) PostgreSQL – קצת מתקדם (WAL / רפליקציה / failover)

בדיקות WAL / Archiver

sudo -u postgres psql -c "SHOW wal_level;"
sudo -u postgres psql -c "SELECT * FROM pg_stat_archiver;"

בדיקות רפליקציה (Primary)

SELECT client_addr, application_name, state, sync_state
FROM pg_stat_replication;

בדיקות רפליקציה (Secondary)

SELECT pg_is_in_recovery();
SELECT now() - pg_last_xact_replay_timestamp() AS lag;

קידום רפליקה (Failover ידני)

sudo -u postgres pg_ctl promote -D /var/lib/pgsql/data


---

4) MongoDB – תפעול בסיסי (CLI: mongosh)

כניסה

mongosh

הצגת DBs / מעבר DB

מה זה: רשימת בסיס נתונים וניווט.


show dbs
use appdb
db.getName()

הצגת Collections

מה זה: המקביל לטבלאות.


show collections
db.getCollectionNames()

הצגת מסמכים (Find) + Limit/Pretty

db.students.find().limit(20)
db.students.find().limit(20).pretty()
db.students.find({grade: {$gte: 90}}).limit(20)

CRUD קצר (דוגמה)

db.students.insertOne({name:"Yali", grade:95, subjects:["math","physics"]})

db.students.insertMany([
  {name:"Noa", grade:88},
  {name:"Dan", grade:91}
])

db.students.updateOne({name:"Yali"}, {$set:{grade:98}})
db.students.updateMany({grade: {$lt: 90}}, {$inc:{grade:1}})

db.students.deleteOne({name:"Dan"})
db.students.deleteMany({grade: {$lt: 60}})

הצגת מבנה “סכימתי” בפועל (מה קיים במסמכים)

מה זה: Mongo אין schema קשיח, אז מסתכלים דרך דוגמאות/אגרגציה.


db.students.findOne()

אינדקסים

מה זה: קריטי לביצועים.


db.students.getIndexes()
db.students.createIndex({name:1})
db.students.createIndex({grade:-1})

ספירות וסטטיסטיקות בסיסיות

db.students.countDocuments()
db.stats()
db.students.stats()

Aggregation בסיסי (קצת יותר מתקדם אבל פרקטי)

db.students.aggregate([
  {$group: {_id: null, avgGrade: {$avg: "$grade"}, maxGrade: {$max: "$grade"}}}
])


---

5) MongoDB – Replica Set (Primary/Secondaries) בדיקות יומיומיות

סטטוס רפליקציה

rs.status()
rs.printReplicationInfo()
rs.printSecondaryReplicationInfo()

Write Concern (בטיחות כתיבה)

db.students.insertOne({x:1}, {writeConcern:{w:"majority"}})


---

6) גיבוי ושחזור Mongo

mongodump --out /backup/mongo_$(date +%F)
mongorestore /backup/mongo_2026-02-22


---

7) Checklist קצר לתפעול יומי (בלי חורים)

Linux

systemctl status …, journalctl -u …

df -h, ss -tulnp


Postgres

\l, \dt, \d table, SELECT … LIMIT

גיבוי: pg_dump, בדיקת רפליקציה: pg_stat_replication


Mongo

show dbs, show collections, db.coll.find().limit(20)

אינדקסים: getIndexes()

Replica set: rs.status()



---

אם תרצה, אני יכול גם להוסיף “פקודות עזר” של psql (כמו \timing, \x, \watch) ושל mongosh (כמו it, help, output formatting) כדי שיהיה לך כלי עבודה מלא לתפעול יום־יומי.





===========================================================
FLASK MASTER (TEACHING + USAGE EDITION)
===========================================================

מטרה:
✅ ללמד אותך Flask בצורה מדורגת + עם הסברים מעולים
✅ לכל פיצ'ר יש "איך משתמשים" (דפדפן/ curl) + מה אמור לקרות
✅ קובץ אחד בלבד, בלי ספריות צד שלישי מעבר ל-Flask

-----------------------------------------------------------
איך להריץ:
-----------------------------------------------------------
1) התקנה:
   pip install flask

2) הרצה:
   python flask_master_teaching_usage.py

3) דפדפן:
   http://127.0.0.1:5000/

-----------------------------------------------------------
איך לעבוד נכון:
-----------------------------------------------------------
- תריץ את השרת
- תפתח את Home page (/)
- תנסה endpoint אחד בכל פעם
- תבדוק מה חוזר (טקסט/JSON/הורדת קובץ)
- תסתכל ב-DevTools -> Network (וגם headers)

-----------------------------------------------------------
Windows curl הערה חשובה:
-----------------------------------------------------------
- Windows CMD: משתמשים ב- ^ לשורה חדשה וצריך להיזהר עם גרשיים.
- PowerShell: מומלץ להשתמש ב:
  curl.exe ...   (כדי לא להתבלבל עם alias של curl)

אני נותן דוגמאות לשניהם.

===========================================================
"""

from __future__ import annotations

import io
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from flask import (
    Flask,
    Blueprint,
    Response,
    abort,
    jsonify,
    make_response,
    redirect,
    render_template_string,
    request,
    send_file,
    session,
    url_for,
)


# ===========================================================
# CH1 — Helper: זמן UTC
# ===========================================================
def utc_now_iso() -> str:
    """
    למה זה קיים?
    - בהרבה APIs רוצים להחזיר זמן בצורה עקבית
    - UTC מונע בעיות timezone
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ===========================================================
# CH2 — App Factory
# ===========================================================
def create_app() -> Flask:
    """
    App Factory:
    - יוצר ומחזיר app חדש
    - זה פרודקשן pattern
    - עוזר בבדיקות (test_client)
    """
    app = Flask(__name__)

    # =======================================================
    # CH3 — Config
    # =======================================================
    # SECRET_KEY:
    # חובה ל-session. בפרודקשן שמים ב-env.
    app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", secrets.token_hex(16))

    # Limit uploads:
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

    # JSON בעברית בלי escape
    app.json.ensure_ascii = False

    # =======================================================
    # CH4 — Fake DB in memory (Todos)
    # =======================================================
    # זה רק בשביל ללמוד CRUD לפני DB אמיתי.
    app.config["TODOS"] = [
        {"id": 1, "title": "Learn Flask basics", "done": True},
        {"id": 2, "title": "Try POST + JSON", "done": False},
    ]
    app.config["NEXT_TODO_ID"] = 3

    # =======================================================
    # CH5 — Upload dir
    # =======================================================
    upload_dir = Path(os.getenv("TEMP", "/tmp")) / "flask_master_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_DIR"] = upload_dir

    # =======================================================
    # CH6 — Hooks: before/after request
    # =======================================================
    @app.before_request
    def before_every_request() -> None:
        """
        לפני כל בקשה:
        - נמדוד זמן
        - ניצור request_id (tracking)
        """
        request.environ["start_time"] = time.perf_counter()
        request.environ["request_id"] = secrets.token_hex(8)

    @app.after_request
    def after_every_request(resp: Response) -> Response:
        """
        אחרי כל בקשה:
        - נוסיף headers שימושיים לתשובה
        """
        start = request.environ.get("start_time")
        rid = request.environ.get("request_id", "-")

        if isinstance(start, (int, float)):
            ms = (time.perf_counter() - start) * 1000
            resp.headers["X-Request-Duration-ms"] = f"{ms:.2f}"

        resp.headers["X-Request-Id"] = str(rid)
        return resp

    # =======================================================
    # CH7 — Error handlers (JSON errors)
    # =======================================================
    @app.errorhandler(404)
    def handle_404(_e):
        return jsonify({"error": "not_found", "path": request.path}), 404

    @app.errorhandler(400)
    def handle_400(_e):
        return jsonify({"error": "bad_request"}), 400

    @app.errorhandler(401)
    def handle_401(_e):
        return jsonify({"error": "unauthorized"}), 401

    @app.errorhandler(413)
    def handle_413(_e):
        return jsonify({"error": "payload_too_large"}), 413

    # =======================================================
    # CH8 — HOME PAGE: "איך משתמשים" מרכזי
    # =======================================================
    @app.get("/")
    def home() -> str:
        """
        דף בית שמרכז הכל:
        - קישורים לדפדפן
        - דוגמאות curl
        - הסבר מה אמור לקרות
        """
        template = r"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>
            <title>Flask Master</title>
            <style>
              body { font-family: system-ui, Arial; margin: 24px; background: #fafafa; }
              .card { background: white; border: 1px solid #e6e6e6; border-radius: 12px; padding: 14px; margin: 12px 0; }
              code, pre { background: #f3f4f6; padding: 2px 6px; border-radius: 8px; }
              pre { padding: 10px; overflow:auto; white-space: pre-wrap; }
              .grid { display:grid; gap: 12px; grid-template-columns: 1fr; }
              @media (min-width: 1000px){ .grid { grid-template-columns: 1fr 1fr; } }
              .hint { color: #333; }
              h2,h3 { margin: 8px 0; }
              ul { margin: 8px 0; }
              li { margin: 6px 0; }
            </style>
          </head>
          <body>
            <h1>Flask Master — Teaching + Usage</h1>
            <p>UTC: <code>{{ utc }}</code></p>
            <p class="hint">
              טיפ: פתח DevTools → Network. בדוק headers:
              <code>X-Request-Id</code>, <code>X-Request-Duration-ms</code>
            </p>

            <div class="grid">
              <div class="card">
                <h2>Browser (לחץ)</h2>
                <ul>
                  <li><a href="/ping">/ping</a> — אמור להחזיר <code>pong</code></li>
                  <li><a href="/json">/json</a> — אמור להחזיר JSON עם זמן</li>
                  <li><a href="/add?a=2&b=3">/add?a=2&b=3</a> — אמור להחזיר result=5</li>
                  <li><a href="/user/42">/user/42</a> — path param</li>
                  <li><a href="/cookies/set">/cookies/set</a> ואז <a href="/cookies/get">/cookies/get</a> — cookie demo</li>
                  <li><a href="/session/incr">/session/incr</a> — כל refresh מעלה counter</li>
                  <li><a href="/redirect-me">/redirect-me</a> — אמור להפנות בחזרה ל-/</li>
                  <li><a href="/stream">/stream</a> — אמור להדפיס chunks בהדרגה</li>
                  <li><a href="/download-demo">/download-demo</a> — אמור להוריד קובץ</li>
                  <li><a href="/api/time">/api/time</a> — API time</li>
                  <li><a href="/api/todos">/api/todos</a> — רשימת TODOS</li>
                  <li><a href="/api/protected">/api/protected</a> — אמור להחזיר 401 בלי token</li>
                </ul>
              </div>

              <div class="card">
                <h2>curl examples</h2>

                <h3>Linux/Mac</h3>
                <pre><code># Echo JSON (POST)
curl -X POST http://127.0.0.1:5000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"msg":"hi"}'

# Create todo (POST)
curl -X POST http://127.0.0.1:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'

# Patch todo (PATCH)
curl -X PATCH http://127.0.0.1:5000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'

# Delete todo (DELETE)
curl -X DELETE http://127.0.0.1:5000/api/todos/1

# Protected (token)
curl http://127.0.0.1:5000/api/protected -H "X-Api-Token: letmein"

# Upload file
curl -F "file=@my.txt" http://127.0.0.1:5000/api/upload
</code></pre>

                <h3>Windows CMD</h3>
                <pre><code>REM Echo JSON
curl -X POST http://127.0.0.1:5000/api/echo ^
  -H "Content-Type: application/json" ^
  -d "{\"msg\":\"hi\"}"

REM Create todo
curl -X POST http://127.0.0.1:5000/api/todos ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Buy milk\"}"

REM Protected
curl http://127.0.0.1:5000/api/protected -H "X-Api-Token: letmein"</code></pre>

                <h3>PowerShell</h3>
                <pre><code># שים לב: עדיף curl.exe
curl.exe -X POST http://127.0.0.1:5000/api/echo `
  -H "Content-Type: application/json" `
  -d '{\"msg\":\"hi\"}'

curl.exe http://127.0.0.1:5000/api/protected -H "X-Api-Token: letmein"</code></pre>

              </div>
            </div>

            <div class="card">
              <h2>מה ללמוד/לשים לב</h2>
              <ul>
                <li><b>GET</b> = קורא מידע (לרוב בלי body)</li>
                <li><b>POST</b> = יוצר משהו / שולח body (לרוב JSON)</li>
                <li><b>PATCH</b> = עדכון חלקי</li>
                <li><b>DELETE</b> = מחיקה</li>
                <li><b>Cookies</b> נשמרים בדפדפן. <b>Session</b> ב-Flask הוא cookie חתום.</li>
                <li><b>Blueprint</b> עוזר לארגן routes (API תחת /api)</li>
              </ul>
            </div>
          </body>
        </html>
        """
        return render_template_string(template, utc=utc_now_iso())

    # =======================================================
    # CH9 — Basics: text / JSON
    # =======================================================
    @app.get("/ping")
    def ping():
        """
        איך משתמשים:
        - בדפדפן: GET /ping
        מה קורה:
        - מחזיר טקסט "pong"
        """
        return "pong"

    @app.get("/json")
    def json_demo():
        """
        איך משתמשים:
        - בדפדפן: GET /json
        מה קורה:
        - מחזיר JSON
        """
        return {"message": "Hello JSON", "utc": utc_now_iso()}

    # =======================================================
    # CH10 — Query params: /add?a=2&b=3
    # =======================================================
    @app.get("/add")
    def add():
        """
        איך משתמשים:
        - בדפדפן: /add?a=2&b=3
        מה קורה:
        - קורא request.args, ממיר ל-float, מחזיר סכום

        תרגיל:
        - נסה /add?a=hello&b=3 -> אמור לקבל invalid_number
        - נסה /add?a=2 -> אמור לקבל missing_params
        """
        a = request.args.get("a")
        b = request.args.get("b")
        if a is None or b is None:
            return {"error": "missing_params", "hint": "Use /add?a=2&b=3"}, 400
        try:
            fa = float(a)
            fb = float(b)
        except ValueError:
            return {"error": "invalid_number"}, 400
        return {"a": fa, "b": fb, "result": fa + fb}

    # =======================================================
    # CH11 — Path params: /user/42
    # =======================================================
    @app.get("/user/<int:user_id>")
    def user(user_id: int):
        """
        איך משתמשים:
        - בדפדפן: /user/42
        מה קורה:
        - Flask "מחלץ" את ה-42 מהנתיב ומעביר לפונקציה כ-int
        """
        return {"user_id": user_id, "source": "path param"}

    # =======================================================
    # CH12 — Cookies
    # =======================================================
    @app.get("/cookies/set")
    def cookies_set():
        """
        איך משתמשים:
        1) פתח: /cookies/set
        2) ואז פתח: /cookies/get

        מה קורה:
        - /cookies/set שולח response עם cookie בשם demo_cookie=hello
        - הדפדפן שומר אותו
        - /cookies/get קורא אותו ומחזיר ב-JSON
        """
        resp = make_response({"ok": True, "cookie_set": "demo_cookie=hello"})
        resp.set_cookie("demo_cookie", "hello", max_age=3600, httponly=True, samesite="Lax")
        return resp

    @app.get("/cookies/get")
    def cookies_get():
        """
        איך משתמשים:
        - GET /cookies/get אחרי שקבעת cookie
        מה קורה:
        - מחזיר את הערך שנמצא אצל הלקוח
        """
        return {"demo_cookie": request.cookies.get("demo_cookie")}

    # =======================================================
    # CH13 — Session
    # =======================================================
    @app.get("/session/incr")
    def session_incr():
        """
        איך משתמשים:
        - בדפדפן: /session/incr ולחץ refresh כמה פעמים
        מה קורה:
        - counter נשמר ב-session cookie חתום
        - בכל פעם הוא גדל

        חשוב:
        - לא לשים session מידע גדול/סודי (זה לא encrypted)
        """
        counter = int(session.get("counter", 0)) + 1
        session["counter"] = counter
        return {"session_counter": counter}

    # =======================================================
    # CH14 — Redirect
    # =======================================================
    @app.get("/redirect-me")
    def redirect_me():
        """
        איך משתמשים:
        - בדפדפן: /redirect-me
        מה קורה:
        - מחזיר redirect ל-home ("/")
        """
        return redirect(url_for("home"))

    # =======================================================
    # CH15 — Streaming response
    # =======================================================
    @app.get("/stream")
    def stream():
        """
        איך משתמשים:
        - בדפדפן: /stream
        מה קורה:
        - השרת שולח 5 שורות, אחת כל 0.2 שניות
        - תראה שזה "מגיע בהדרגה"

        טיפ:
        - לפעמים בדפדפן זה יראה הכל בסוף בגלל buffering.
          נסה גם:
          curl http://127.0.0.1:5000/stream
        """
        def gen() -> Iterable[bytes]:
            for i in range(5):
                yield f"chunk {i} at {utc_now_iso()}\n".encode("utf-8")
                time.sleep(0.2)
        return Response(gen(), mimetype="text/plain; charset=utf-8")

    # =======================================================
    # CH16 — send_file download demo
    # =======================================================
    @app.get("/download-demo")
    def download_demo():
        """
        איך משתמשים:
        - בדפדפן: /download-demo
        מה קורה:
        - אמור לרדת קובץ hello.txt למחשב
        """
        data = io.BytesIO(b"Hello from Flask download!\n")
        return send_file(data, as_attachment=True, download_name="hello.txt")

    # =======================================================
    # CH17 — Blueprint: API תחת /api
    # =======================================================
    api = Blueprint("api", __name__, url_prefix="/api")

    def require_token() -> None:
        """
        איך משתמשים:
        - בלי token: GET /api/protected -> 401
        - עם token ב-header:
          curl http://127.0.0.1:5000/api/protected -H "X-Api-Token: letmein"

        מה קורה:
        - אם token לא נכון -> abort(401)
        """
        expected = os.environ.get("DEMO_API_TOKEN", "letmein")
        token = request.headers.get("X-Api-Token") or request.args.get("token")
        if token != expected:
            abort(401)

    @api.get("/time")
    def api_time():
        """
        איך משתמשים:
        - GET /api/time
        מה קורה:
        - מחזיר זמן UTC
        """
        return {"utc_time": utc_now_iso()}

    @api.post("/echo")
    def api_echo():
        """
        איך משתמשים (POST JSON):
        - Linux/Mac:
          curl -X POST http://127.0.0.1:5000/api/echo \
            -H "Content-Type: application/json" \
            -d '{"msg":"hi"}'

        - Windows CMD:
          curl -X POST http://127.0.0.1:5000/api/echo ^
            -H "Content-Type: application/json" ^
            -d "{\"msg\":\"hi\"}"

        מה קורה:
        - קורא JSON מה-body ומחזיר אותו בחזרה
        """
        payload = request.get_json(silent=True)
        if payload is None:
            return {"error": "expected_json"}, 400
        return {"you_sent": payload}

    # =======================================================
    # CH18 — CRUD Todos
    # =======================================================
    @api.get("/todos")
    def list_todos():
        """
        איך משתמשים:
        - GET /api/todos
        מה קורה:
        - מחזיר רשימת todos + count
        """
        todos = app.config["TODOS"]
        return {"items": todos, "count": len(todos)}

    @api.post("/todos")
    def create_todo():
        """
        איך משתמשים:
        - POST /api/todos עם JSON:
          {"title":"Buy milk"}

        Linux/Mac:
          curl -X POST http://127.0.0.1:5000/api/todos \
            -H "Content-Type: application/json" \
            -d '{"title":"Buy milk"}'

        מה קורה:
        - יוצר todo חדש עם id אוטומטי
        - done=false
        - מחזיר אותו עם status 201
        """
        payload = request.get_json(silent=True) or {}
        title = str(payload.get("title", "")).strip()
        if not title:
            return {"error": "title_required"}, 400

        todo_id = int(app.config["NEXT_TODO_ID"])
        app.config["NEXT_TODO_ID"] = todo_id + 1

        todo = {"id": todo_id, "title": title, "done": False}
        app.config["TODOS"].append(todo)
        return todo, 201

    @api.patch("/todos/<int:todo_id>")
    def update_todo(todo_id: int):
        """
        איך משתמשים:
        - PATCH /api/todos/1 עם JSON:
          {"done": true}
          או:
          {"title": "New title"}

        Linux/Mac:
          curl -X PATCH http://127.0.0.1:5000/api/todos/1 \
            -H "Content-Type: application/json" \
            -d '{"done":true}'

        מה קורה:
        - מוצא todo לפי id
        - מעדכן רק שדות שנשלחו
        """
        payload = request.get_json(silent=True) or {}
        todos = app.config["TODOS"]
        todo = next((t for t in todos if t["id"] == todo_id), None)
        if todo is None:
            abort(404)

        if "title" in payload:
            title = str(payload.get("title", "")).strip()
            if not title:
                return {"error": "title_required"}, 400
            todo["title"] = title

        if "done" in payload:
            todo["done"] = bool(payload["done"])

        return todo

    @api.delete("/todos/<int:todo_id>")
    def delete_todo(todo_id: int):
        """
        איך משתמשים:
        - DELETE /api/todos/1

        Linux/Mac:
          curl -X DELETE http://127.0.0.1:5000/api/todos/1

        מה קורה:
        - מוחק את הפריט ומחזיר את מה שנמחק
        """
        todos = app.config["TODOS"]
        idx = next((i for i, t in enumerate(todos) if t["id"] == todo_id), None)
        if idx is None:
            abort(404)
        deleted = todos.pop(idx)
        return {"deleted": deleted}

    # =======================================================
    # CH19 — Upload / Download
    # =======================================================
    @api.post("/upload")
    def upload_file():
        """
        איך משתמשים:
        - שולחים multipart/form-data עם field בשם "file"

        Linux/Mac:
          curl -F "file=@my.txt" http://127.0.0.1:5000/api/upload

        Windows CMD:
          curl -F "file=@my.txt" http://127.0.0.1:5000/api/upload

        מה קורה:
        - שומר קובץ בתיקיית UPLOAD_DIR
        - מחזיר שם קובץ חדש (stored_as)
        """
        if "file" not in request.files:
            return {"error": "missing_file_field", "hint": 'Use form field name "file".'}, 400

        f = request.files["file"]
        if not f.filename:
            return {"error": "empty_filename"}, 400

        safe_name = f"{secrets.token_hex(8)}_{Path(f.filename).name}"
        dest = app.config["UPLOAD_DIR"] / safe_name
        f.save(dest)

        return {"stored_as": safe_name, "bytes": dest.stat().st_size}, 201

    @api.get("/download/<path:name>")
    def download_file(name: str):
        """
        איך משתמשים:
        1) תעלה קובץ דרך /api/upload
        2) תקבל stored_as למשל: "abc123_my.txt"
        3) תוריד:
           GET /api/download/abc123_my.txt

        מה קורה:
        - שולח את הקובץ להורדה
        """
        path = app.config["UPLOAD_DIR"] / Path(name).name  # sanitize בסיסי
        if not path.exists():
            abort(404)
        return send_file(path, as_attachment=True, download_name=path.name)

    # =======================================================
    # CH20 — Protected endpoint
    # =======================================================
    @api.get("/protected")
    def protected():
        """
        איך משתמשים:
        - בלי token:
          GET /api/protected -> 401

        - עם token:
          curl http://127.0.0.1:5000/api/protected -H "X-Api-Token: letmein"

        מה קורה:
        - אם token נכון -> {"ok": true}
        """
        require_token()
        return {"ok": True, "hint": "Send X-Api-Token: letmein (or set DEMO_API_TOKEN)"}

    # מחברים את ה-Blueprint
    app.register_blueprint(api)

    # =======================================================
    # CH21 — Self test (לבדוק שהכל עובד)
    # =======================================================
    def self_test() -> None:
        """
        איך משתמשים:
        python flask_master_teaching_usage.py --self-test

        מה קורה:
        - מריץ כמה בקשות פנימיות ומוודא סטטוסים
        """
        with app.test_client() as client:
            assert client.get("/ping").status_code == 200
            assert client.get("/api/time").status_code == 200
            assert client.post("/api/echo", json={"x": 1}).status_code == 200
            assert client.get("/nope").status_code == 404

    app.config["_SELF_TEST"] = self_test

    return app


# יצירת האפליקציה בפועל
app = create_app()


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        app.config["_SELF_TEST"]()
        print("Self-test OK ✅")
        raise SystemExit(0)

    # debug=True ללמידה:
    # - auto reload
    # - error tracebacks
    app.run(host="127.0.0.1", port=5000, debug=True)
