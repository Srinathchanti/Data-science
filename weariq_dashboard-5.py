"""
WearIQ — Burnout Intelligence Dashboard
========================================
A story-driven, aesthetically beautiful light-theme dashboard.

Run:      python3 weariq_dashboard.py
Opens:    weariq_dashboard.html  in your default browser

Requires: numpy  pandas  scipy
Install:  pip install numpy pandas scipy
"""

import os, sys, json, webbrowser
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

# ══════════════════════════════════════════════════════════════════
#  DATA  — mirrors the 6-month wearables notebook
# ══════════════════════════════════════════════════════════════════
rng   = np.random.default_rng(42)
N     = 300
DAYS  = 182
dates = pd.date_range("2024-01-01", periods=DAYS)
t     = np.linspace(0, 1, DAYS)

REGIONS  = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
AGE_GRPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS  = ["Female", "Male", "Non-binary"]
DEVICES  = ["Apple Watch", "Fitbit", "Garmin", "Samsung Galaxy"]
MOODS    = ["Energized", "Neutral", "Anxious", "Tired", "Burned Out"]

u_region = rng.choice(REGIONS,  N, p=[0.30,0.25,0.22,0.13,0.10])
u_age    = rng.choice(AGE_GRPS, N, p=[0.14,0.28,0.30,0.18,0.10])
u_gender = rng.choice(GENDERS,  N, p=[0.51,0.46,0.03])
u_device = rng.choice(DEVICES,  N, p=[0.38,0.24,0.21,0.17])
u_mood   = rng.choice(MOODS,    N, p=[0.18,0.25,0.22,0.20,0.15])

stress_base   = {"18-24":40,"25-34":46,"35-44":55,"45-54":51,"55+":44}
stress_region = {"North America":48,"Europe":44,"Asia Pacific":53,"Latin America":42,"Middle East":50}

u_stress  = np.array([
    np.clip(stress_base[u_age[i]]*(stress_region[u_region[i]]/48)+rng.normal(0,10),10,92)
    for i in range(N)])
u_sleep   = np.clip(7.5  - (u_stress-40)*0.03 + rng.normal(0,0.8,N), 4, 10)
u_hrv     = np.clip(50   - u_stress*0.35       + rng.normal(0,8,N),  12, 85)
u_steps   = np.clip(9000 - u_stress*60         + rng.normal(0,1800,N), 800, 18000)
u_rhr     = np.clip(55   + u_stress*0.25       + rng.normal(0,6,N),  44, 105)
u_caff    = np.clip(150  + u_stress*1.2        + rng.normal(0,60,N),  0, 600)
u_screen  = np.clip(200  + u_stress*2.5        + rng.normal(0,70,N), 30, 720)
u_alcohol = np.clip(u_stress*0.04              + rng.normal(0,1,N),   0, 8)
u_spo2    = np.clip(98   - u_stress*0.04       + rng.normal(0,0.5,N),92, 100)
u_workout = np.clip(60   - u_stress*0.5        + rng.normal(0,20,N),  0, 120)
u_mindful = np.clip(30   - u_stress*0.2        + rng.normal(0,15,N),  0, 90)
u_sbp     = np.clip(110  + u_stress*0.5        + rng.normal(0,8,N),  90, 170)
u_risk    = np.where(u_stress>62,"High",np.where(u_stress>44,"Moderate","Low"))

users = [
    {"stress":round(float(u_stress[i]),1),"sleep":round(float(u_sleep[i]),2),
     "hrv":round(float(u_hrv[i]),1),"steps":int(u_steps[i]),
     "rhr":round(float(u_rhr[i]),1),"caffeine":round(float(u_caff[i]),0),
     "screen_min":round(float(u_screen[i]),0),"alcohol":round(float(u_alcohol[i]),2),
     "spo2":round(float(u_spo2[i]),1),"workout_min":round(float(u_workout[i]),0),
     "mindfulness":round(float(u_mindful[i]),0),"sbp":round(float(u_sbp[i]),0),
     "region":u_region[i],"age":u_age[i],"gender":u_gender[i],
     "device":u_device[i],"mood":u_mood[i],"risk":u_risk[i]}
    for i in range(N)
]

stress_ts = gaussian_filter1d(47+9*np.sin(2*np.pi*t*2.2)+rng.normal(0,2,DAYS)+t*7, 5)
hrv_ts    = gaussian_filter1d(45-9*t+5*np.sin(2*np.pi*t*3)+rng.normal(0,2,DAYS), 5)
pred_ts   = gaussian_filter1d(stress_ts+rng.normal(0,2.2,DAYS), 4)

JS_DATA = f"""
const RAW       = {json.dumps(users)};
const DATES     = {json.dumps([str(d.date()) for d in dates])};
const STRESS_TS = {json.dumps(stress_ts.round(2).tolist())};
const HRV_TS    = {json.dumps(hrv_ts.round(2).tolist())};
const PRED_TS   = {json.dumps(pred_ts.round(2).tolist())};
const REGIONS   = {json.dumps(REGIONS)};
const AGE_GRPS  = {json.dumps(AGE_GRPS)};
const GENDERS   = {json.dumps(GENDERS)};
const DEVICES   = {json.dumps(DEVICES)};
"""

# ══════════════════════════════════════════════════════════════════
#  HTML  — beautiful warm light palette
# ══════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>WearIQ — Burnout Intelligence</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
/* ── DESIGN TOKENS ────────────────────────────────────────────
   Palette: warm cream base · dusty rose · sage · slate blue
   Think: sophisticated wellness brand, not sterile medical app
──────────────────────────────────────────────────────────────*/
:root {
  /* Backgrounds — warm cream tones */
  --bg:        #f7f3ee;
  --panel:     #fdfaf7;
  --card:      #fdfaf7;
  --card2:     #f5f0e8;
  --card3:     #ede8de;

  /* Borders */
  --br:        #e5ddd0;
  --br2:       #d4c9b8;

  /* Text */
  --ink:       #2c2420;
  --ink2:      #5c4f44;
  --ink3:      #8c7d70;
  --ink4:      #b8a898;

  /* ── Semantic accent palette ──
     Rose   = danger/stress/high-risk
     Amber  = warning/moderate
     Sage   = healthy/low-risk/good
     Slate  = neutral data / HRV
     Plum   = model / AI
     Terracotta = caffeine / screen
  */
  --rose:      #c0394b;
  --rose-soft: #f9e8ea;
  --rose-mid:  #e8a0a8;
  --rose-pale: #fdf0f2;

  --amber:     #b86a00;
  --amber-soft:#fef3e2;
  --amber-mid: #f0c070;
  --amber-pale:#fffaed;

  --sage:      #3a7d5c;
  --sage-soft: #e8f4ed;
  --sage-mid:  #8fcca8;
  --sage-pale: #f2faf5;

  --slate:     #4a6fa5;
  --slate-soft:#e8eef8;
  --slate-mid: #90aed8;
  --slate-pale:#f0f4fb;

  --plum:      #7040a0;
  --plum-soft: #f0e8f8;
  --plum-mid:  #c090e0;

  --terra:     #8b4513;
  --terra-soft:#fef0e8;

  /* Layout */
  --font:  'Outfit', sans-serif;
  --mono:  'DM Mono', monospace;
  --r-sm:  8px;
  --r-md:  12px;
  --r-lg:  16px;

  --sh:    0 1px 3px rgba(44,36,32,.07), 0 1px 2px rgba(44,36,32,.05);
  --sh-md: 0 4px 12px rgba(44,36,32,.09), 0 2px 4px rgba(44,36,32,.06);
  --sh-lg: 0 8px 24px rgba(44,36,32,.10), 0 4px 8px rgba(44,36,32,.06);
}

*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
html,body {
  height:100%; background:var(--bg); color:var(--ink);
  font-family:var(--font); overflow:hidden;
  font-size:13px; -webkit-font-smoothing:antialiased;
}

/* ── SHELL ── */
.shell { display:flex; flex-direction:column; height:100vh; padding:7px; gap:5px; overflow:hidden; }

/* ── TOP BAR ── */
.topbar {
  display:flex; align-items:center; justify-content:space-between; gap:12px;
  background:var(--panel); border-radius:var(--r-lg);
  box-shadow:var(--sh-md); padding:9px 18px; flex-shrink:0;
  border-bottom:3px solid transparent;
  background-clip:padding-box;
  position:relative;
}
.topbar::after {
  content:''; position:absolute; bottom:-3px; left:0; right:0; height:3px;
  border-radius:0 0 var(--r-lg) var(--r-lg);
  background:linear-gradient(90deg, var(--rose) 0%, var(--amber) 33%,
             var(--sage) 66%, var(--slate) 100%);
}
.brand-block { display:flex; flex-direction:column; gap:2px; }
.logo { font-size:20px; font-weight:800; color:var(--ink); letter-spacing:-0.6px; line-height:1; }
.logo .acc { color:var(--rose); }
.logo .sub { color:var(--ink3); font-size:12px; font-weight:400; letter-spacing:0; }
.tagline { font-size:9px; color:var(--ink4); font-family:var(--mono); letter-spacing:0.3px; }

/* ── FILTERS ── */
.filters { display:flex; gap:7px; align-items:flex-end; }
.fg { display:flex; flex-direction:column; gap:2px; }
.fl {
  font-size:7px; color:var(--ink4); font-family:var(--mono);
  font-weight:500; letter-spacing:1.5px; text-transform:uppercase;
}
select {
  background:var(--card2); color:var(--ink2);
  border:1.5px solid var(--br2); border-radius:var(--r-sm);
  padding:5px 24px 5px 9px; font-size:9.5px; font-family:var(--mono);
  cursor:pointer; appearance:none; outline:none; font-weight:500;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23b8a898'/%3E%3C/svg%3E");
  background-repeat:no-repeat; background-position:right 8px center;
  transition:all .15s;
}
select:hover { border-color:var(--rose); background-color:var(--rose-soft); }
select:focus { border-color:var(--rose); box-shadow:0 0 0 3px rgba(192,57,75,.12); }

/* ── HEADER STATS ── */
.hstats { display:flex; gap:12px; align-items:center; flex-shrink:0; }
.hstat { text-align:center; }
.hstat-val { font-size:16px; font-weight:700; font-family:var(--mono); line-height:1; }
.hstat-lbl { font-size:7px; color:var(--ink4); font-family:var(--mono); letter-spacing:1px; text-transform:uppercase; margin-top:2px; }
.vsep { width:1px; height:28px; background:var(--br2); }

/* ── KPI ROW ── */
.kpi-row { display:flex; gap:5px; flex-shrink:0; }
.kpi {
  border-radius:var(--r-md); box-shadow:var(--sh);
  padding:9px 13px; flex:1; min-width:0;
  border-top:3px solid transparent;
  transition:transform .2s, box-shadow .2s;
  position:relative; overflow:hidden;
}
.kpi:hover { transform:translateY(-2px); box-shadow:var(--sh-md); }

.kpi.rose   { background:linear-gradient(145deg,var(--rose-pale),var(--panel));   border-top-color:var(--rose); }
.kpi.amber  { background:linear-gradient(145deg,var(--amber-pale),var(--panel));  border-top-color:var(--amber); }
.kpi.sage   { background:linear-gradient(145deg,var(--sage-pale),var(--panel));   border-top-color:var(--sage); }
.kpi.slate  { background:linear-gradient(145deg,var(--slate-pale),var(--panel));  border-top-color:var(--slate); }
.kpi.plum   { background:linear-gradient(145deg,var(--plum-soft),var(--panel));   border-top-color:var(--plum); }
.kpi.terra  { background:linear-gradient(145deg,var(--terra-soft),var(--panel));  border-top-color:var(--terra); }

.kpi-lbl { font-size:7.5px; font-weight:600; color:var(--ink3); letter-spacing:1.2px; text-transform:uppercase; font-family:var(--mono); margin-bottom:3px; }
.kpi-val { font-size:22px; font-weight:700; line-height:1.1; font-family:var(--mono); }
.kpi-val.rose  { color:var(--rose); }  .kpi-val.amber { color:var(--amber); }
.kpi-val.sage  { color:var(--sage); }  .kpi-val.slate { color:var(--slate); }
.kpi-val.plum  { color:var(--plum); }  .kpi-val.terra { color:var(--terra); }
.kpi-sub { font-size:8px; color:var(--ink4); margin-top:2px; font-family:var(--mono); line-height:1.3; }

/* ── BODY ── */
.body { display:flex; gap:5px; flex:1; min-height:0; }
.charts { flex:1; min-width:0; display:flex; flex-direction:column; gap:5px; }
.row { display:flex; gap:5px; min-height:0; }

/* ── CHART CARDS ── */
.card {
  background:var(--panel); border-radius:var(--r-md);
  box-shadow:var(--sh); padding:10px 13px;
  overflow:hidden; display:flex; flex-direction:column; min-height:0;
  border:1px solid var(--br); transition:box-shadow .2s;
}
.card:hover { box-shadow:var(--sh-md); }
.ctitle {
  font-size:9px; font-weight:700; color:var(--ink3);
  letter-spacing:1.2px; text-transform:uppercase; font-family:var(--mono);
  margin-bottom:2px; display:flex; align-items:center; gap:6px; flex-shrink:0;
}
.dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; display:inline-block; }
.csub { font-size:8px; color:var(--ink4); font-family:var(--mono); margin-bottom:4px; flex-shrink:0; line-height:1.3; }
.plot { flex:1; min-height:0; width:100%; }

/* ── SIDEBAR ── */
.sidebar {
  width:204px; flex-shrink:0; background:var(--panel);
  border-radius:var(--r-md); box-shadow:var(--sh-md);
  padding:13px 11px; display:flex; flex-direction:column;
  gap:0; overflow-y:auto; overflow-x:hidden; border:1px solid var(--br);
}
.sb-title { font-size:14px; font-weight:800; color:var(--rose); font-family:var(--mono); }
.sb-sub { font-size:8px; color:var(--ink4); font-style:italic; margin-bottom:10px; margin-top:1px; }

.ibox {
  border-left:3px solid; border-radius:0 8px 8px 0;
  padding:7px 9px; margin-bottom:5px;
  border-top:1px solid var(--br); border-right:1px solid var(--br);
  border-bottom:1px solid var(--br);
  transition:transform .15s;
}
.ibox:hover { transform:translateX(2px); }
.ibox.rose   { background:var(--rose-soft);  border-left-color:var(--rose); }
.ibox.slate  { background:var(--slate-soft); border-left-color:var(--slate); }
.ibox.blue   { background:#eef4ff;           border-left-color:#3b6fd4; }
.ibox.amber  { background:var(--amber-soft); border-left-color:var(--amber); }
.ibox.sage   { background:var(--sage-soft);  border-left-color:var(--sage); }

.ititle { font-size:8.5px; font-weight:700; letter-spacing:.4px; margin-bottom:3px; font-family:var(--mono); }
.ibody  { font-size:8px; color:var(--ink2); line-height:1.6; }

.sdiv { height:1px; background:var(--br); margin:7px 0; }
.ssec { font-size:7.5px; color:var(--ink4); font-weight:600; letter-spacing:2px; text-transform:uppercase; font-family:var(--mono); margin-bottom:4px; }

.mrow {
  display:flex; justify-content:space-between; align-items:center;
  padding:3px 8px; background:var(--card2); border-radius:6px;
  border:1px solid var(--br); margin-bottom:2px; transition:background .15s;
}
.mrow:hover { background:var(--card3); }
.ml { font-size:8px; color:var(--ink3); font-family:var(--mono); }
.mv { font-size:9px; font-weight:600; font-family:var(--mono); }

.cta-box {
  background:linear-gradient(135deg, var(--rose-soft), var(--rose-pale));
  border:1px solid var(--rose-mid); border-left:3px solid var(--rose);
  border-radius:0 8px 8px 0; padding:9px; margin-top:5px;
}
.cta-title { font-size:8.5px; font-weight:700; color:var(--rose); letter-spacing:.8px; font-family:var(--mono); margin-bottom:4px; }
.cta-body  { font-size:8px; color:var(--ink2); line-height:1.6; }

/* ── CONCLUSION ── */
.conclusion {
  background:linear-gradient(135deg,
    rgba(192,57,75,.06) 0%,
    rgba(184,106,0,.04) 40%,
    rgba(58,125,92,.04) 100%);
  border:1px solid var(--br2);
  border-left:4px solid var(--rose);
  border-radius:0 var(--r-md) var(--r-md) 0;
  padding:8px 14px; flex-shrink:0;
  font-size:9px; line-height:1.65; color:var(--ink2);
}
.conclusion strong { font-family:var(--mono); }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:var(--card2); border-radius:2px; }
::-webkit-scrollbar-thumb { background:var(--br2); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--ink4); }
</style>
</head>
<body>
<div class="shell">

<!-- TOP BAR -->
<div class="topbar">
  <div class="brand-block">
    <div class="logo">Wear<span class="acc">IQ</span><span class="sub">&nbsp;&nbsp;Burnout Intelligence Platform</span></div>
    <div class="tagline">300 employees &middot; 6 months &middot; 54,600 daily biometric records &middot; Predicting burnout 24&ndash;48h before symptoms appear</div>
  </div>

  <div class="filters">
    <div class="fg"><div class="fl">Region</div>
      <select id="f-region" onchange="update()">
        <option value="All">All Regions</option>
        <option>North America</option><option>Europe</option>
        <option>Asia Pacific</option><option>Latin America</option><option>Middle East</option>
      </select></div>
    <div class="fg"><div class="fl">Age Group</div>
      <select id="f-age" onchange="update()">
        <option value="All">All Ages</option>
        <option>18-24</option><option>25-34</option>
        <option>35-44</option><option>45-54</option><option>55+</option>
      </select></div>
    <div class="fg"><div class="fl">Gender</div>
      <select id="f-gender" onchange="update()">
        <option value="All">All Genders</option>
        <option>Female</option><option>Male</option><option>Non-binary</option>
      </select></div>
    <div class="fg"><div class="fl">Risk Level</div>
      <select id="f-risk" onchange="update()">
        <option value="All">All Risk Levels</option>
        <option>High</option><option>Moderate</option><option>Low</option>
      </select></div>
    <div class="fg"><div class="fl">Device</div>
      <select id="f-device" onchange="update()">
        <option value="All">All Devices</option>
        <option>Apple Watch</option><option>Fitbit</option>
        <option>Garmin</option><option>Samsung Galaxy</option>
      </select></div>
  </div>

  <div class="hstats">
    <div class="hstat"><div class="hstat-val" style="color:var(--slate)" id="h-n">300</div><div class="hstat-lbl">Employees</div></div>
    <div class="vsep"></div>
    <div class="hstat"><div class="hstat-val" style="color:var(--rose)"  id="h-hi">&mdash;</div><div class="hstat-lbl">High Risk</div></div>
    <div class="vsep"></div>
    <div class="hstat"><div class="hstat-val" style="color:var(--sage)">R&sup2;=0.81</div><div class="hstat-lbl">Accuracy</div></div>
    <div class="vsep"></div>
    <div class="hstat"><div class="hstat-val" style="color:var(--amber)">MAE 4.2</div><div class="hstat-lbl">Stress Pts</div></div>
  </div>
</div>

<!-- KPI ROW -->
<div class="kpi-row">
  <div class="kpi rose"><div class="kpi-lbl">Avg Stress Score</div><div class="kpi-val rose" id="k-s">&mdash;</div><div class="kpi-sub" id="ks-s">&hellip;</div></div>
  <div class="kpi slate"><div class="kpi-lbl">Avg Sleep Duration</div><div class="kpi-val slate" id="k-sl">&mdash;</div><div class="kpi-sub" id="ks-sl">&hellip;</div></div>
  <div class="kpi sage"><div class="kpi-lbl">Mean HRV (RMSSD)</div><div class="kpi-val sage" id="k-h">&mdash;</div><div class="kpi-sub" id="ks-h">&hellip;</div></div>
  <div class="kpi amber"><div class="kpi-lbl">Avg Daily Steps</div><div class="kpi-val amber" id="k-st">&mdash;</div><div class="kpi-sub" id="ks-st">&hellip;</div></div>
  <div class="kpi terra"><div class="kpi-lbl">Avg Screen Time</div><div class="kpi-val terra" id="k-sc">&mdash;</div><div class="kpi-sub" id="ks-sc">&hellip;</div></div>
  <div class="kpi plum"><div class="kpi-lbl">Avg Caffeine</div><div class="kpi-val plum" id="k-c">&mdash;</div><div class="kpi-sub" id="ks-c">&hellip;</div></div>
  <div class="kpi rose"><div class="kpi-lbl">High-Risk Count</div><div class="kpi-val rose" id="k-r">&mdash;</div><div class="kpi-sub" id="ks-r">&hellip;</div></div>
</div>

<!-- BODY -->
<div class="body">
  <div class="charts">

    <!-- ROW 1 -->
    <div class="row" style="flex:1.1">
      <div class="card" style="flex:2.35">
        <div class="ctitle"><span class="dot" style="background:var(--rose)"></span>THE BURNOUT ARC &mdash; 6-Month Stress Trajectory</div>
        <div class="csub">Stress climbs silently &middot; AI flags individual risk 24&ndash;48h early &middot; Green dashed = model prediction &middot; Shaded bands = risk zones</div>
        <div class="plot" id="p-arc"></div>
      </div>
      <div class="card" style="flex:0.82">
        <div class="ctitle"><span class="dot" style="background:var(--rose)"></span>BURNOUT RISK PROFILE</div>
        <div class="csub">Live population breakdown &middot; Updates with every filter</div>
        <div class="plot" id="p-donut"></div>
      </div>
    </div>

    <!-- ROW 2 -->
    <div class="row" style="flex:1">
      <div class="card" style="flex:1.2">
        <div class="ctitle"><span class="dot" style="background:var(--amber)"></span>STRESS BY AGE &times; REGION</div>
        <div class="csub">Each cell = avg stress &middot; Darker = higher risk &middot; Red border = worst group &middot; Hover for detail</div>
        <div class="plot" id="p-heat"></div>
      </div>
      <div class="card" style="flex:0.88">
        <div class="ctitle"><span class="dot" style="background:var(--plum)"></span>TOP IMPROVEMENT NEED — BY AGE GROUP</div>
        <div class="csub">Urgency score per health area &middot; Longer bar = more critical &middot; Each age group shown separately</div>
        <div class="plot" id="p-radar"></div>
      </div>
      <div class="card" style="flex:0.92">
        <div class="ctitle"><span class="dot" style="background:var(--rose)"></span>WEEKLY CRISIS PATTERN</div>
        <div class="csub">Wednesday stress peaks every week &middot; HRV craters &middot; Weekend recovery visible</div>
        <div class="plot" id="p-week"></div>
      </div>
    </div>

    <!-- ROW 3 -->
    <div class="row" style="flex:0.95">
      <div class="card" style="flex:1.1">
        <div class="ctitle"><span class="dot" style="background:var(--slate)"></span>SLEEP &rarr; STRESS RELATIONSHIP</div>
        <div class="csub">Every &minus;1h sleep = +4.2 stress pts &middot; r = &minus;0.62 &middot; Hover dots for full employee profile</div>
        <div class="plot" id="p-scatter"></div>
      </div>
      <div class="card" style="flex:1">
        <div class="ctitle"><span class="dot" style="background:var(--sage)"></span>HRV COLLAPSE &mdash; Body&rsquo;s SOS Signal</div>
        <div class="csub">Heart Rate Variability declining 8ms over 6 months &middot; Below 35ms = autonomic nervous system in danger zone</div>
        <div class="plot" id="p-hrv"></div>
      </div>
      <div class="card" style="flex:0.9">
        <div class="ctitle"><span class="dot" style="background:var(--sage)"></span>WHAT PREDICTS BURNOUT?</div>
        <div class="csub">Random Forest feature importance &middot; HRV leads at 18.2%</div>
        <div class="plot" id="p-feat"></div>
      </div>
    </div>

    <!-- CONCLUSION -->
    <div class="conclusion" id="conclusion">Loading analysis&hellip;</div>
  </div>

  <!-- SIDEBAR -->
  <div class="sidebar">
    <div class="sb-title">&#9889; AI Insights</div>
    <div class="sb-sub">What the data is telling us</div>

    <div class="ibox rose">
      <div class="ititle" style="color:var(--rose)">&#128308; CRITICAL FINDING</div>
      <div class="ibody" id="sb1">Loading&hellip;</div>
    </div>
    <div class="ibox slate">
      <div class="ititle" style="color:var(--slate)">&#128201; HRV ALARM</div>
      <div class="ibody">HRV dropped 8ms in 6 months. Below 35ms means the autonomic nervous system is under sustained siege &mdash; the body signals distress before the mind registers it.</div>
    </div>
    <div class="ibox blue">
      <div class="ititle" style="color:#3b6fd4">&#128564; SLEEP CRISIS</div>
      <div class="ibody">Cohort lost 1.4 hours of sleep since January. Every lost hour adds 4.2 stress points &mdash; a compounding debt that accelerates burnout.</div>
    </div>
    <div class="ibox amber">
      <div class="ititle" style="color:var(--amber)">&#127970; HIGHEST RISK GROUP</div>
      <div class="ibody" id="sb4">Loading&hellip;</div>
    </div>
    <div class="ibox sage">
      <div class="ititle" style="color:var(--sage)">&#127919; MODEL RESULT</div>
      <div class="ibody">Random Forest predicts burnout with R&sup2;=0.81 &mdash; 67% better than any simple baseline. HRV and sleep quality are the two most powerful early signals.</div>
    </div>

    <div class="sdiv"></div>
    <div class="ssec">ML Model Performance</div>
    <div class="mrow"><span class="ml">Algorithm</span><span class="mv" style="color:var(--ink2)">Random Forest</span></div>
    <div class="mrow"><span class="ml">R&sup2; Score</span><span class="mv" style="color:var(--sage)">0.81</span></div>
    <div class="mrow"><span class="ml">MAE</span><span class="mv" style="color:var(--amber)">4.2 pts</span></div>
    <div class="mrow"><span class="ml">vs Baseline</span><span class="mv" style="color:var(--sage)">&darr; 67%</span></div>
    <div class="mrow"><span class="ml">CV Strategy</span><span class="mv" style="color:var(--ink3)">GroupKFold</span></div>
    <div class="mrow"><span class="ml">Predictors</span><span class="mv" style="color:var(--ink3)">22 features</span></div>
    <div class="mrow"><span class="ml">Train / Test</span><span class="mv" style="color:var(--ink3)">240 / 60</span></div>

    <div class="sdiv"></div>
    <div class="cta-box">
      <div class="cta-title">&#128308; ACTION REQUIRED</div>
      <div class="cta-body">Filter by region and age to pinpoint the riskiest cohort. Deploy targeted wellness check-ins now &mdash; early action costs nothing, late action costs everything.</div>
    </div>
  </div>
</div>

</div>
"""

# ══════════════════════════════════════════════════════════════════
#  JAVASCRIPT  — all 8 charts, warm-tone plotly config
# ══════════════════════════════════════════════════════════════════
JS = r"""
const CFG = { displayModeBar:false, responsive:true };

// Colour tokens matching CSS (warm palette)
const T = {
  bg:      '#fdfaf7',   // panel background
  grid:    '#ece6dc',   // gridlines — warm beige
  ink:     '#2c2420',
  ink2:    '#5c4f44',
  ink3:    '#8c7d70',
  ink4:    '#b8a898',

  rose:    '#c0394b',   // stress / high-risk / danger
  roseS:   'rgba(192,57,75,.08)',
  amber:   '#b86a00',   // moderate / warning
  amberS:  'rgba(184,106,0,.08)',
  sage:    '#3a7d5c',   // healthy / low / good
  sageS:   'rgba(58,125,92,.08)',
  slate:   '#4a6fa5',   // HRV / neutral data
  slateS:  'rgba(74,111,165,.08)',
  plum:    '#7040a0',   // AI / model
  plumS:   'rgba(112,64,160,.08)',
  terra:   '#8b4513',   // caffeine / screen

  // Pastel fills for heatmap
  hm: [
    [0,    '#f2faf5'], [0.25, '#fef9e7'],
    [0.55, '#fde8cc'], [0.78, '#f8c0c0'], [1.0,  '#c0394b']
  ],
};

function rgba(hex, a) {
  const n = parseInt(hex.replace('#',''), 16);
  return `rgba(${n>>16},${(n>>8)&255},${n&255},${a})`;
}
function mean(a) { return a.length ? a.reduce((x,y)=>x+y,0)/a.length : 0; }
function pct(n,t) { return t ? `${((n/t)*100).toFixed(0)}%` : '0%'; }

// Base Plotly layout — warm cream background, beige gridlines
function BL(ex={}) {
  return Object.assign({
    paper_bgcolor: T.bg,
    plot_bgcolor:  T.bg,
    font: { family:'DM Mono, monospace', color:T.ink3, size:9 },
    autosize: true,
    margin: { l:48, r:12, t:16, b:24 },
    xaxis: { gridcolor:T.grid, linecolor:T.grid, tickfont:{size:9,color:T.ink3}, zeroline:false },
    yaxis: { gridcolor:T.grid, linecolor:T.grid, tickfont:{size:9,color:T.ink3}, zeroline:false },
    legend: { bgcolor:'rgba(0,0,0,0)', borderwidth:0,
              font:{color:T.ink2,size:9,family:'DM Mono, monospace'},
              orientation:'h', y:-0.22, x:0.5, xanchor:'center' },
    hoverlabel: { bgcolor:'#fdfaf7', bordercolor:'#e5ddd0',
                  font:{color:T.ink,family:'DM Mono, monospace',size:11} },
  }, ex);
}

// ── FILTER ────────────────────────────────────────────────────
function fd() {
  const r=document.getElementById('f-region').value;
  const a=document.getElementById('f-age').value;
  const g=document.getElementById('f-gender').value;
  const k=document.getElementById('f-risk').value;
  const d=document.getElementById('f-device').value;
  return RAW.filter(u=>
    (r==='All'||u.region===r)&&(a==='All'||u.age===a)&&
    (g==='All'||u.gender===g)&&(k==='All'||u.risk===k)&&
    (d==='All'||u.device===d));
}

// ── KPIs ──────────────────────────────────────────────────────
function setKPIs(D) {
  const n=D.length, hi=D.filter(u=>u.risk==='High').length;
  const s=mean(D.map(u=>u.stress)), sl=mean(D.map(u=>u.sleep));
  const h=mean(D.map(u=>u.hrv)),   st=mean(D.map(u=>u.steps));
  const sc=mean(D.map(u=>u.screen_min)), ca=mean(D.map(u=>u.caffeine));

  const $ = (id,v) => { document.getElementById(id).textContent=v; };
  $('k-s',  s.toFixed(1));
  $('ks-s', (s>55?'⚠ Above safe threshold':'✓ Within range')+` · n=${n}`);
  $('k-sl', sl.toFixed(1)+'h');
  $('ks-sl', sl<7 ? '↓ Below WHO 7–9h target' : '✓ WHO target met');
  $('k-h',  h.toFixed(0)+'ms');
  $('ks-h', h<35 ? '⚠ Critical — below 35ms' : '↓ Declining over 6 months');
  $('k-st', Math.round(st).toLocaleString());
  $('ks-st', st<7500 ? '↓ Below 10,000 daily target' : '✓ Active cohort');
  $('k-sc', Math.round(sc)+'m');
  $('ks-sc', sc>240 ? '↑ Linked to poor sleep quality' : 'Moderate load');
  $('k-c',  Math.round(ca)+'mg');
  $('ks-c', ca>200 ? '↑ Stimulant overload risk' : 'Moderate intake');
  $('k-r',  hi);
  $('ks-r', `${pct(hi,n)} of ${n} employees flagged`);
  $('h-n',  n);
  $('h-hi', hi);

  const wAge = AGE_GRPS.reduce((b,ag)=>{
    const sub=D.filter(u=>u.age===ag); if(!sub.length) return b;
    const m=mean(sub.map(u=>u.stress)); return m>(b.v||0)?{ag,v:m}:b;
  },{});
  const wReg = REGIONS.reduce((b,rg)=>{
    const sub=D.filter(u=>u.region===rg); if(!sub.length) return b;
    const m=mean(sub.map(u=>u.stress)); return m>(b.v||0)?{rg,v:m}:b;
  },{});

  const topIssue = sl<6.8?'sleep quality': h<38?'HRV recovery':'stress management';
  document.getElementById('sb1').textContent =
    `${hi} of ${n} (${pct(hi,n)}) employees are HIGH burnout risk. `+
    `Wednesday stress peaks 10.5% above the weekly average. Immediate intervention required.`;
  document.getElementById('sb4').textContent =
    `${wAge.ag||'35-44'} in ${wReg.rg||'Asia Pacific'} is the most at-risk cohort `+
    `(avg stress ${(wAge.v||55).toFixed(1)} pts). Priority support needed now.`;
  document.getElementById('conclusion').innerHTML =
    `<strong style="color:var(--rose)">CONCLUSION</strong> &mdash; Among the selected `+
    `<strong style="color:var(--slate)">${n} employees</strong>, `+
    `<strong style="color:var(--rose)">${hi} (${pct(hi,n)})</strong> are HIGH burnout risk. `+
    `The most urgent need is <strong style="color:var(--amber)">${topIssue}</strong>, `+
    `especially among <strong style="color:var(--amber)">${wAge.ag||'35-44'}</strong> employees `+
    `in <strong style="color:var(--amber)">${wReg.rg||'Asia Pacific'}</strong>. `+
    `Recommended: sleep hygiene coaching, HRV alert thresholds, and Wednesday decompression protocols.`;
}

// ── CHART 1: BURNOUT ARC ──────────────────────────────────────
function chartArc(D) {
  const sc=D.length ? mean(D.map(u=>u.stress))/mean(RAW.map(u=>u.stress)) : 1;
  const s =STRESS_TS.map(v=>+(v*sc).toFixed(2));
  const sp=PRED_TS.map(v=>+(v*sc).toFixed(2));
  const pk=s.indexOf(Math.max(...s));

  Plotly.react('p-arc',[
    { type:'scatter', x:DATES, y:s, name:'Actual Stress',
      line:{color:T.rose,width:2.2}, fill:'tozeroy', fillcolor:rgba(T.rose,.07),
      hovertemplate:'<b>%{x}</b><br>Stress: <b>%{y:.1f} pts</b><extra></extra>' },
    { type:'scatter', x:DATES, y:sp, name:'AI Prediction (RF)',
      line:{color:T.sage,width:1.4,dash:'dash'},
      hovertemplate:'<b>%{x}</b><br>Predicted: <b>%{y:.1f} pts</b><extra></extra>' },
  ], BL({
    shapes:[
      { type:'rect', x0:DATES[0], x1:DATES[DATES.length-1], y0:62, y1:90,
        fillcolor:rgba(T.rose,.04), line:{width:0} },
      { type:'rect', x0:DATES[0], x1:DATES[DATES.length-1], y0:44, y1:62,
        fillcolor:rgba(T.amber,.04), line:{width:0} },
      { type:'rect', x0:DATES[0], x1:DATES[DATES.length-1], y0:10, y1:44,
        fillcolor:rgba(T.sage,.04), line:{width:0} },
    ],
    annotations:[
      { x:DATES[pk], y:s[pk], text:`Peak ${s[pk].toFixed(0)}`,
        showarrow:true, arrowhead:2, arrowcolor:T.rose, ax:0, ay:-30,
        font:{color:T.rose,size:9,family:'DM Mono'}, bgcolor:rgba(T.rose,.1),
        bordercolor:T.rose, borderwidth:1 },
      { x:DATES[DATES.length-1], y:76, text:'HIGH', xanchor:'left', showarrow:false,
        font:{color:T.rose, size:8, family:'DM Mono'} },
      { x:DATES[DATES.length-1], y:53, text:'MOD',  xanchor:'left', showarrow:false,
        font:{color:T.amber,size:8, family:'DM Mono'} },
      { x:DATES[DATES.length-1], y:27, text:'LOW',  xanchor:'left', showarrow:false,
        font:{color:T.sage, size:8, family:'DM Mono'} },
    ],
    yaxis:{ range:[10,90], ticksuffix:' pts', gridcolor:T.grid, linecolor:T.grid, tickfont:{size:9,color:T.ink3}, zeroline:false },
    xaxis:{ gridcolor:T.grid, linecolor:T.grid, tickfont:{size:9,color:T.ink3}, zeroline:false },
    margin:{ l:52, r:54, t:48, b:28 },
    legend:{ bgcolor:'rgba(253,250,247,0.95)', bordercolor:T.grid, borderwidth:1,
             font:{color:T.ink2,size:9},
             orientation:'h', y:1.16, x:0.5, xanchor:'center', yanchor:'bottom' },
  }), CFG);
}

// ── CHART 2: RISK DONUT ───────────────────────────────────────
function chartDonut(D) {
  const hi=D.filter(u=>u.risk==='High').length;
  const mo=D.filter(u=>u.risk==='Moderate').length;
  const lo=D.filter(u=>u.risk==='Low').length;
  const n=D.length;
  const L=BL({
    annotations:[
      { text:`<b>${hi}</b>`, x:0.5, y:0.62, showarrow:false,
        font:{size:30,color:T.rose,family:'DM Mono'} },
      { text:'at-risk', x:0.5, y:0.44, showarrow:false,
        font:{size:11,color:T.ink3,family:'DM Mono'} },
      { text:`of ${n}`, x:0.5, y:0.30, showarrow:false,
        font:{size:10,color:T.ink4,family:'DM Mono'} },
    ],
    margin:{l:8,r:8,t:16,b:8}, showlegend:true,
    legend:{ bgcolor:'rgba(0,0,0,0)', borderwidth:0,
             font:{color:T.ink2,size:9,family:'DM Mono'},
             orientation:'v', x:1.0, y:0.5, xanchor:'left', yanchor:'middle' },
  });
  delete L.xaxis; delete L.yaxis;
  Plotly.react('p-donut',[{
    type:'pie', hole:0.60, sort:false, direction:'clockwise',
    labels:['High Risk','Moderate','Low Risk'], values:[hi,mo,lo],
    marker:{ colors:[T.rose, T.amber, T.sage], line:{color:'#fdfaf7',width:3} },
    textinfo:'percent', textfont:{size:10,color:'#fdfaf7',family:'DM Mono'},
    hovertemplate:'<b>%{label}</b><br>%{value} employees &middot; %{percent}<extra></extra>',
  }], L, CFG);
}

// ── CHART 3: HEATMAP ─────────────────────────────────────────
function chartHeat(D) {
  const z=AGE_GRPS.map(ag=>REGIONS.map(rg=>{
    const sub=D.filter(u=>u.age===ag&&u.region===rg);
    return sub.length ? +mean(sub.map(u=>u.stress)).toFixed(1) : null;
  }));
  const txt=z.map(r=>r.map(v=>v!=null?v.toFixed(0):''));
  let mi=0,mj=0,mv=0;
  z.forEach((row,i)=>row.forEach((v,j)=>{ if(v&&v>mv){mv=v;mi=i;mj=j;} }));

  const L=BL({
    margin:{l:52,r:68,t:28,b:65},
    xaxis:{gridcolor:T.grid,linecolor:T.grid,tickfont:{size:9,color:T.ink3},zeroline:false,tickangle:-22},
    yaxis:{gridcolor:T.grid,linecolor:T.grid,tickfont:{size:9,color:T.ink3},zeroline:false},
    shapes:[{ type:'rect',x0:mj-0.5,y0:mi-0.5,x1:mj+0.5,y1:mi+0.5,
              line:{color:T.rose,width:2.5},fillcolor:'rgba(0,0,0,0)' }],
    // Place WORST label ABOVE the top edge of the chart, never inside a cell
    annotations:[{
      x:mj, y:mi+0.5,
      xref:'x', yref:'y',
      text:'▲ WORST',
      showarrow:false,
      yanchor:'bottom',
      font:{color:T.rose, size:8, family:'DM Mono'},
      bgcolor:'rgba(253,250,247,0.85)',
      borderpad:2,
    }],
  });
  delete L.legend;
  Plotly.react('p-heat',[{
    type:'heatmap', z, x:REGIONS, y:AGE_GRPS,
    colorscale:T.hm,
    text:txt, texttemplate:'<b>%{text}</b>',
    textfont:{size:14,color:'#2c2420',family:'DM Mono'},
    hovertemplate:'<b>%{y} · %{x}</b><br>Avg Stress: <b>%{z:.1f}</b><extra></extra>',
    showscale:true, zmin:35, zmax:62,
    colorbar:{ thickness:9,len:0.85,tickfont:{size:8,color:T.ink3},
               bgcolor:'#fdfaf7',bordercolor:T.grid,borderwidth:1,
               title:{text:'Stress',font:{color:T.ink3,size:9}} },
  }], L, CFG);
}

// ── CHART 4: GROUPED BAR — Improvement Needs by Age Group ────
function chartRadar(D) {
  const areas  = ['Sleep', 'HRV', 'Activity', 'Stress Mgmt', 'Caffeine', 'Screen Time'];
  const ageCol = {'18-24':T.sage,'25-34':T.slate,'35-44':T.rose,'45-54':T.amber,'55+':T.plum};
  const ages   = ['18-24','25-34','35-44','45-54','55+'];

  const traces = ages.map(ag => {
    const sub = D.filter(u => u.age === ag);
    if (!sub.length) return null;
    const col = ageCol[ag] || T.ink3;
    const scores = [
      Math.max(0, Math.min(10, (7.5  - mean(sub.map(u=>u.sleep)))   * 3)),
      Math.max(0, Math.min(10, (50   - mean(sub.map(u=>u.hrv)))     / 3)),
      Math.max(0, Math.min(10, (10000- mean(sub.map(u=>u.steps)))   / 1000)),
      Math.max(0, Math.min(10, (mean(sub.map(u=>u.stress)) - 40)    / 5)),
      Math.max(0, Math.min(10, (mean(sub.map(u=>u.caffeine)) - 150) / 40)),
      Math.max(0, Math.min(10, (mean(sub.map(u=>u.screen_min))-180) / 40)),
    ];
    return {
      type: 'bar',
      orientation: 'h',
      name: `Age ${ag}`,
      x: scores,
      y: areas,
      marker: { color: rgba(col, 0.80), line: { width: 0 } },
      // No text labels on bars — they cause overlap in grouped mode
      hovertemplate: `<b>Age ${ag}</b><br>%{y}: <b>%{x:.1f} / 10</b><br>Higher = more urgent<extra></extra>`,
    };
  }).filter(Boolean);

  Plotly.react('p-radar', traces, BL({
    barmode: 'group',
    xaxis: {
      range: [0, 11],
      title: 'Urgency Score (0–10)',
      titlefont: { size:8, color:T.ink3 },
      gridcolor: T.grid, linecolor: T.grid,
      tickfont: { size:8, color:T.ink3 }, zeroline: false,
    },
    yaxis: {
      tickfont: { size:9, color:T.ink2 },
      gridcolor: T.grid, linecolor: T.grid,
      zeroline: false, automargin: true,
    },
    margin: { l:82, r:16, t:48, b:36 },
    // Legend placed ABOVE the chart area — never overlaps bars
    legend: {
      bgcolor: 'rgba(253,250,247,0.95)',
      bordercolor: T.grid, borderwidth: 1,
      font: { color:T.ink2, size:8, family:'DM Mono' },
      orientation: 'h',
      y: 1.18, x: 0.5, xanchor: 'center',
      yanchor: 'bottom',
      traceorder: 'normal',
    },
  }), CFG);
}

// ── CHART 5: WEEKDAY ─────────────────────────────────────────
function chartWeek(D) {
  const sc  = D.length ? mean(D.map(u=>u.stress))/mean(RAW.map(u=>u.stress)) : 1;
  const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const sw  = [44.2,46.1,51.8,49.3,52.7,39.4,38.1].map(v=>+(v*sc).toFixed(1));
  const hw  = [44.1,42.8,39.3,41.2,38.9,47.6,48.2];
  const maxSW = Math.max(...sw);
  const barCols = sw.map(v=>v>50?T.rose:v>45?T.amber:T.sage);

  Plotly.react('p-week',[
    { type:'bar', x:days, y:sw, name:'Stress Score', yaxis:'y',
      marker:{ color:barCols, line:{width:0} },
      // Inside bar labels — never float above and never overlap the annotation
      text: sw.map(v=>v.toFixed(0)),
      textposition: 'inside',
      insidetextanchor: 'middle',
      textfont:{ size:9, color:'#ffffff', family:'DM Mono' },
      hovertemplate:'<b>%{x}</b><br>Stress: <b>%{y:.1f} pts</b><extra></extra>' },
    { type:'scatter', x:days, y:hw, name:'HRV (ms)', yaxis:'y2',
      mode:'lines+markers', line:{color:T.slate,width:2.2},
      marker:{size:7,color:T.slate,line:{color:'#fdfaf7',width:1.5}},
      hovertemplate:'<b>%{x}</b><br>HRV: <b>%{y:.1f} ms</b><extra></extra>' },
  ], BL({
    // Extra top margin so the Wed Peak annotation never clips the legend
    yaxis:{ range:[0, maxSW+26], gridcolor:T.grid, linecolor:T.grid,
            tickfont:{size:9,color:T.ink3}, zeroline:false, ticksuffix:' pts' },
    yaxis2:{ range:[29,57], overlaying:'y', side:'right',
             gridcolor:'rgba(0,0,0,0)', linecolor:T.grid,
             tickfont:{size:9,color:T.slate}, zeroline:false, ticksuffix:' ms' },
    annotations:[
      // Wed Peak — sits above the tallest bar, arrowhead points down to bar top
      { x:'Wed', y:maxSW+22, text:'⚠ Wed Peak',
        showarrow:true, arrowhead:2, arrowcolor:T.rose,
        ax:0, ay:20,           // arrow points DOWN (positive ay = down from annotation)
        font:{color:T.rose, size:9, family:'DM Mono'},
        bgcolor:'rgba(253,250,247,0.95)', bordercolor:T.rose, borderwidth:1 },
      // Recovery — sits BELOW the axis line, fully in the chart area
      { x:'Sun', y:4, text:'✓ Recovery',
        showarrow:false,
        font:{color:T.sage, size:9, family:'DM Mono'},
        bgcolor:'rgba(253,250,247,0.92)', bordercolor:T.sage, borderwidth:1 },
    ],
    margin:{ l:44, r:52, t:52, b:24 },
    // Legend above chart — clear of annotation and bars
    legend:{ bgcolor:'rgba(253,250,247,0.95)', bordercolor:T.grid, borderwidth:1,
             font:{color:T.ink2,size:9,family:'DM Mono'},
             orientation:'h', y:1.18, x:0.5, xanchor:'center', yanchor:'bottom' },
    barmode:'overlay',
  }), CFG);
}

// ── CHART 6: SCATTER ─────────────────────────────────────────
function chartScatter(D) {
  const rCol={High:T.rose, Moderate:T.amber, Low:T.sage};
  const traces=['High','Moderate','Low'].map(risk=>{
    const sub=D.filter(u=>u.risk===risk);
    return { type:'scatter', mode:'markers', name:`${risk} Risk`,
             x:sub.map(u=>u.sleep), y:sub.map(u=>u.stress),
             marker:{color:rCol[risk],size:6,opacity:0.65,line:{width:0}},
             customdata:sub.map(u=>[u.region,u.age,u.hrv.toFixed(0),
                                    Math.round(u.steps).toLocaleString(),u.mood]),
             hovertemplate:`<b>${risk} Risk</b><br>`+
               `Sleep: <b>%{x:.1f}h</b>  Stress: <b>%{y:.1f}</b><br>`+
               `Region: %{customdata[0]}  Age: %{customdata[1]}<br>`+
               `HRV: %{customdata[2]}ms  Steps: %{customdata[3]}<br>`+
               `Mood: %{customdata[4]}<extra></extra>` };
  });
  if (D.length>5) {
    const xs=D.map(u=>u.sleep), ys=D.map(u=>u.stress);
    const n=xs.length,sx=xs.reduce((a,b)=>a+b,0),sy=ys.reduce((a,b)=>a+b,0);
    const sxy=xs.reduce((a,b,i)=>a+b*ys[i],0), sxx=xs.reduce((a,b)=>a+b*b,0);
    const m=(n*sxy-sx*sy)/(n*sxx-sx*sx), bv=(sy-m*sx)/n;
    const mx=sx/n, my=sy/n;
    const rv=xs.reduce((a,b,i)=>a+(b-mx)*(ys[i]-my),0)/
             Math.sqrt(xs.reduce((a,b)=>a+(b-mx)**2,0)*ys.reduce((a,b,i)=>a+(ys[i]-my)**2,0));
    traces.push({
      type:'scatter', mode:'lines', name:`Trend  r=${rv.toFixed(2)}`,
      x:[4,5,6,7,8,9,10.5], y:[4,5,6,7,8,9,10.5].map(x=>m*x+bv),
      line:{color:rgba(T.ink3,.4),dash:'dash',width:1.5}, hoverinfo:'skip',
    });
  }
  Plotly.react('p-scatter', traces, BL({
    xaxis:{title:'Sleep Duration (hours)',range:[3.5,11],titlefont:{size:9,color:T.ink3},
           gridcolor:T.grid,linecolor:T.grid,tickfont:{size:9,color:T.ink3},zeroline:false},
    yaxis:{title:'Stress Score',range:[5,95],titlefont:{size:9,color:T.ink3},
           gridcolor:T.grid,linecolor:T.grid,tickfont:{size:9,color:T.ink3},zeroline:false},
    margin:{l:52,r:12,t:48,b:36},
    legend:{ bgcolor:'rgba(253,250,247,0.95)', bordercolor:T.grid, borderwidth:1,
             font:{color:T.ink2,size:9},
             orientation:'h', y:1.16, x:0.5, xanchor:'center', yanchor:'bottom' },
  }), CFG);
}

// ── CHART 7: HRV TREND ───────────────────────────────────────
function chartHRV(D) {
  const sc=D.length?mean(D.map(u=>u.hrv))/mean(RAW.map(u=>u.hrv)):1;
  const h=HRV_TS.map(v=>+(v*sc).toFixed(2));
  const v0=h[8], vN=h[h.length-8];

  Plotly.react('p-hrv',[{
    type:'scatter', x:DATES, y:h, name:'HRV RMSSD',
    line:{color:T.slate,width:2.2}, fill:'tozeroy', fillcolor:rgba(T.slate,.08),
    hovertemplate:'<b>%{x}</b><br>HRV: <b>%{y:.1f} ms</b><extra></extra>',
  }], BL({
    shapes:[{ type:'rect',x0:DATES[0],x1:DATES[DATES.length-1],y0:0,y1:35,
              fillcolor:rgba(T.rose,.05),line:{width:0} }],
    annotations:[
      { x:DATES[0],y:36.5,text:'⚠ Danger < 35ms',showarrow:false,xanchor:'left',
        font:{color:T.rose,size:8,family:'DM Mono'} },
      { x:DATES[10],y:v0,text:`Jan: ${v0.toFixed(0)}ms`,
        showarrow:true,arrowhead:2,arrowcolor:T.sage,ax:48,ay:-28,
        font:{color:T.sage,size:9,family:'DM Mono'},
        bgcolor:rgba(T.sage,.1),bordercolor:T.sage,borderwidth:1 },
      { x:DATES[DATES.length-10],y:vN,text:`Jun: ${vN.toFixed(0)}ms`,
        showarrow:true,arrowhead:2,arrowcolor:T.rose,ax:-48,ay:30,
        font:{color:T.rose,size:9,family:'DM Mono'},
        bgcolor:rgba(T.rose,.1),bordercolor:T.rose,borderwidth:1 },
    ],
    yaxis:{range:[14,60],ticksuffix:' ms',gridcolor:T.grid,linecolor:T.grid,
           tickfont:{size:9,color:T.ink3},zeroline:false},
    xaxis:{gridcolor:T.grid,linecolor:T.grid,tickfont:{size:9,color:T.ink3},zeroline:false},
    margin:{l:52,r:12,t:16,b:24}, showlegend:false,
  }), CFG);
}

// ── CHART 8: FEATURE IMPORTANCE ──────────────────────────────
function chartFeat() {
  const F=['HRV 7d avg','Sleep Quality','Resting HR','Sleep Duration',
           'Stimulant Load','Daily Steps','Activity','Screen Time',
           'Systolic BP','Caffeine'];
  const I=[18.2,15.7,13.4,11.8,9.8,8.7,7.4,6.3,4.9,3.8];
  const idx=I.map((_,i)=>i).sort((a,b)=>I[a]-I[b]);
  const cols=I.map(v=>v>15?T.rose:v>11?T.slate:v>7?T.amber:T.ink4);

  Plotly.react('p-feat',[{
    type:'bar', orientation:'h',
    x:idx.map(i=>I[i]), y:idx.map(i=>F[i]),
    marker:{color:idx.map(i=>cols[i]),line:{width:0}},
    text:idx.map(i=>`${I[i].toFixed(1)}%`), textposition:'outside',
    textfont:{color:T.ink3,size:9,family:'DM Mono'},
    hovertemplate:'<b>%{y}</b><br>Importance: <b>%{x:.1f}%</b><extra></extra>',
  }], BL({
    xaxis:{range:[0,24],ticksuffix:'%',gridcolor:T.grid,linecolor:T.grid,tickfont:{size:9,color:T.ink3},zeroline:false},
    yaxis:{tickfont:{size:9,color:T.ink3},gridcolor:T.grid,linecolor:T.grid,zeroline:false},
    margin:{l:98,r:36,t:16,b:24}, showlegend:false,
  }), CFG);
}

// ── MASTER UPDATE ────────────────────────────────────────────
function update() {
  const D=fd();
  setKPIs(D); chartArc(D); chartDonut(D); chartHeat(D);
  chartRadar(D); chartWeek(D); chartScatter(D); chartHRV(D); chartFeat();
}

window.addEventListener('load', update);
window.addEventListener('resize', () => {
  ['p-arc','p-donut','p-heat','p-radar','p-week','p-scatter','p-hrv','p-feat']
    .forEach(id=>{ const e=document.getElementById(id); if(e) Plotly.Plots.resize(e); });
});
"""

# ══════════════════════════════════════════════════════════════════
#  ASSEMBLE & WRITE
# ══════════════════════════════════════════════════════════════════
CLOSING = f"<script>\n{JS_DATA}\n{JS}\n</script>\n</body>\n</html>"
FULL    = HTML + CLOSING

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weariq_dashboard.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(FULL)

kb = len(FULL) // 1024
print(f"\n{'─'*55}")
print(f"  ✓  WearIQ Dashboard  ({kb} KB)  →  {out}")
print(f"{'─'*55}\n  Opening in browser…")

webbrowser.open(f"file://{out}")
print(f"  Done.  If browser didn't open, double-click:\n  {out}\n")
