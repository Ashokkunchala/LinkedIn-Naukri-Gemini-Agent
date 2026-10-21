import json
import logging
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from .config import APP_API_KEY, MONITOR_INTERVAL_SECONDS, ALERT_MODE, MONITOR_ENABLED
from .db import connect, init_db, audit
from .schemas import JobCreate, DraftRequest, ApprovalCreate, ApprovalDecision, ApplicationCreate
from .scoring import score_job
from .gemini import generate_draft, GeminiNotConfigured

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="LinkedIn-Naukri-Gemini-Agent", version="0.1.0",
              description="Approval-gated career copilot; external actions are disabled.")

@app.on_event("startup")
def startup():
    init_db()
    if not APP_API_KEY:
        logging.warning("APP_API_KEY is unset. Configure it before using outside local development.")

def require_key(x_api_key: str | None = Header(default=None)):
    if APP_API_KEY and x_api_key != APP_API_KEY:
        raise HTTPException(401, "Missing or invalid X-API-Key")
    if not APP_API_KEY:
        logging.warning("Write endpoint used without APP_API_KEY.")

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Career Agent</title><style>body{font:16px system-ui;max-width:900px;margin:28px auto;padding:0 16px;background:#f7f8fa;color:#17202a}section{background:white;border:1px solid #ddd;border-radius:12px;padding:18px;margin:14px 0}input,textarea,select,button{font:inherit;padding:9px;margin:5px 0;max-width:100%;box-sizing:border-box}input,textarea,select{width:100%}button{cursor:pointer;background:#172554;color:white;border:0;border-radius:6px}.job{border-top:1px solid #ddd;padding:12px 0}</style></head><body>
<h1>Career Agent</h1><p>Gemini career copilot for LinkedIn and Naukri.</p><p><b>Safety:</b> This starter does not submit applications or edit profiles. Review and perform platform actions yourself.</p>
<section><h2>Add job</h2><form id="f"><input name="key" type="password" placeholder="API key (if configured)"><select name="platform"><option>manual</option><option>linkedin</option><option>naukri</option></select><input name="title" required placeholder="Job title"><input name="company" placeholder="Company"><input name="location" placeholder="Location"><input name="url" placeholder="Job URL"><textarea name="description" rows="5" required placeholder="Paste job description"></textarea><input name="skills" placeholder="Your skills, comma-separated"><button>Add job</button></form><p id="msg"></p></section>
<section><h2>Jobs</h2><button onclick="load()">Refresh</button><div id="jobs"></div></section>
<section><h2>Approvals</h2><button onclick="loadA()">Refresh approvals</button><div id="approvals"></div><small>Approval records do not trigger external actions.</small></section>
<script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const headers=()=>({'Content-Type':'application/json','X-API-Key':document.querySelector('[name=key]').value});
document.querySelector('#f').onsubmit=async e=>{e.preventDefault();let f=new FormData(e.target);let b={platform:f.get('platform'),title:f.get('title'),company:f.get('company'),location:f.get('location'),url:f.get('url'),description:f.get('description'),skills:f.get('skills').split(',').map(x=>x.trim()).filter(Boolean)};let r=await fetch('/api/jobs',{method:'POST',headers:headers(),body:JSON.stringify(b)});document.querySelector('#msg').textContent=r.ok?'Job saved.':'Could not save job: '+await r.text();load()};
async function load(){let r=await fetch('/api/jobs');let a=await r.json();document.querySelector('#jobs').innerHTML=a.map(j=>'<div class="job"><b>'+esc(j.title)+'</b> — '+esc(j.company)+' · score '+j.fit_score+'%<p>'+esc(j.location)+' · '+esc(j.platform)+'</p><p>'+esc(j.description.slice(0,240))+'</p><button onclick="draft('+j.id+')">Draft cover letter</button> <button onclick="approve('+j.id+')">Request application approval</button><pre id="draft-'+j.id+'"></pre></div>').join('')||'No jobs yet.'}
async function draft(id){let profile=prompt('Paste your truthful candidate profile');if(!profile)return;let r=await fetch('/api/jobs/'+id+'/draft',{method:'POST',headers:headers(),body:JSON.stringify({kind:'cover_letter',profile})});let x=await r.json();document.querySelector('#draft-'+id).textContent=x.draft||x.detail||JSON.stringify(x)}
async function approve(id){let r=await fetch('/api/approvals',{method:'POST',headers:headers(),body:JSON.stringify({action_type:'submit_application',target:'job_id:'+id,payload:{job_id:id}})});alert(r.ok?'Approval request recorded. No application was submitted.':await r.text());loadA()}
async function loadA(){let r=await fetch('/api/approvals');let a=await r.json();document.querySelector('#approvals').innerHTML=a.map(x=>'<p>#'+x.id+' · '+esc(x.action_type)+' · '+esc(x.target)+' · '+esc(x.status)+'</p>').join('')||'No approvals yet.'}
load();loadA();
</script></body></html>""")

@app.get("/api/health")
def health():
    return {"status": "ok", "external_platform_actions": "disabled"}

@app.get("/api/monitor/status")
def monitor_status():
    return {"enabled": MONITOR_ENABLED, "interval_seconds": MONITOR_INTERVAL_SECONDS,
            "alert_mode": ALERT_MODE, "connectors": {"linkedin": "not_implemented", "naukri": "not_implemented"},
            "active": False, "reason": "No authorized platform connector is installed; no polling is running."}

@app.get("/api/jobs")
def jobs():
    with connect() as c:
        rows = c.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]

@app.post("/api/jobs", dependencies=[Depends(require_key)])
def add_job(j: JobCreate):
    score, matches = score_job(j.description, j.skills)
    with connect() as c:
        cur = c.execute("INSERT INTO jobs(platform,title,company,location,url,description,fit_score) VALUES(?,?,?,?,?,?,?)",
                        (j.platform, j.title, j.company, j.location, j.url, j.description, score))
        jid = cur.lastrowid
    audit("job_added", json.dumps({"job_id": jid, "platform": j.platform, "matches": matches}))
    return {"id": jid, "fit_score": score, "matched_skills": matches}

@app.post("/api/jobs/{job_id}/draft", dependencies=[Depends(require_key)])
def draft(job_id: int, d: DraftRequest):
    with connect() as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found")
    try:
        result = generate_draft(d.kind, dict(row), d.profile, d.extra_instructions)
    except GeminiNotConfigured as e:
        raise HTTPException(503, str(e))
    except Exception:
        logging.exception("Gemini draft failed")
        raise HTTPException(502, "Gemini request failed; check configuration and logs")
    audit("draft_generated", json.dumps({"job_id": job_id, "kind": d.kind}))
    return {"draft": result, "requires_human_review": True}

@app.get("/api/approvals")
def approvals():
    with connect() as c:
        rows = c.execute("SELECT * FROM approvals ORDER BY id DESC").fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["payload"] = json.loads(item["payload"])
        out.append(item)
    return out

@app.post("/api/approvals", dependencies=[Depends(require_key)])
def request_approval(a: ApprovalCreate):
    with connect() as c:
        cur = c.execute("INSERT INTO approvals(action_type,target,payload) VALUES(?,?,?)",
                        (a.action_type, a.target, json.dumps(a.payload, ensure_ascii=False)))
        aid = cur.lastrowid
    audit("approval_requested", json.dumps({"approval_id": aid, "action_type": a.action_type}))
    return {"id": aid, "status": "pending", "external_action_executed": False}

@app.post("/api/approvals/{approval_id}/decision", dependencies=[Depends(require_key)])
def decide(approval_id: int, d: ApprovalDecision):
    with connect() as c:
        row = c.execute("SELECT status FROM approvals WHERE id=?", (approval_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Approval not found")
        if row["status"] != "pending":
            raise HTTPException(409, "Approval already decided")
        status = "approved" if d.decision == "approve" else "rejected"
        c.execute("UPDATE approvals SET status=?,decided_at=CURRENT_TIMESTAMP,decision_note=? WHERE id=? AND status='pending'",
                  (status, d.note, approval_id))
    audit("approval_decided", json.dumps({"approval_id": approval_id, "decision": d.decision}))
    return {"id": approval_id, "status": status, "external_action_executed": False}

@app.get("/api/applications")
def applications():
    with connect() as c:
        rows = c.execute("SELECT a.*,j.title,j.company,j.platform,j.url FROM applications a LEFT JOIN jobs j ON j.id=a.job_id ORDER BY a.id DESC").fetchall()
    return [dict(r) for r in rows]

@app.post("/api/applications", dependencies=[Depends(require_key)])
def track_application(a: ApplicationCreate):
    with connect() as c:
        if not c.execute("SELECT id FROM jobs WHERE id=?", (a.job_id,)).fetchone():
            raise HTTPException(404, "Job not found")
        cur = c.execute("INSERT INTO applications(job_id,status,notes) VALUES(?,?,?)",
                        (a.job_id, a.status, a.notes))
        aid = cur.lastrowid
    audit("application_tracked", json.dumps({"application_id": aid, "job_id": a.job_id}))
    return {"id": aid, "status": a.status}
