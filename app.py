import streamlit as st
import datetime
from astral import Observer
from astral.sun import sun
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

# 1. PRECISION ESOTERIC MAPPINGS FROM KASH AL-BARNI'S TREATISE
SAAT_DATABASE = {
  "JUMA": {
    "DAY": [
      {"planet": "ZHRA", "status": "Sa'd Atsal"}, {"planet": "ATRD", "status": "Mumtaziz-Dost"}, {"planet": "QMAR", "status": "Nahas-Dushman"}, {"planet": "JAHL", "status": "Sa'd-Dost"}, {"planet": "MSTR", "status": "Sa'd Atsal, NA"}, {"planet": "MRKH", "status": "Sa'd, NA"},
      {"planet": "SHMS", "status": "Sa'd Atsal, Dushman"}, {"planet": "ZHRA", "status": "Sa'd Atsal"}, {"planet": "ATRD", "status": "S'ad Mumtaziz-Dost"}, {"planet": "QMAR", "status": "Nahas Anfasal-Dushman"}, {"planet": "JAHL", "status": "Nahas -Dost"}, {"planet": "MSTR", "status": "Sa'd Atsal, NA"}
    ],
    "NIGHT": [
      {"planet": "QMAR", "status": "Sa'd Atsal"}, {"planet": "JAHL", "status": "Nahas Mumtaziz-Dost"}, {"planet": "MSTR", "status": "Nahas-Dushman"}, {"planet": "MRKH", "status": "Sa'd-Dost"}, {"planet": "SHMS", "status": "Sa'd Atsal, NA"}, {"planet": "ZHRA", "status": "Sa'd, NA"},
      {"planet": "ATRD", "status": "Sa'd Atsal, Dushman"}, {"planet": "QMAR", "status": "Sa'd Atsal"}, {"planet": "JAHL", "status": "S'ad Anfsal -Dost"}, {"planet": "MSTR", "status": "Nahas Anfasal-Dushman"}, {"planet": "MRKH", "status": "Nahas -Dost"}, {"planet": "SHMS", "status": "Sa'd Atsal, NA"}
    ]
  },
  "HAFTA": {
    "DAY": [
      {"planet": "JAHL", "status": "Sa'd Atsal"}, {"planet": "MSTR", "status": "Sa'd Atsal,NA"}, {"planet": "MRKH", "status": "Nahas Atsal, Dushman"}, {"planet": "SHMS", "status": "Sa'd Atsal, Dushman"}, {"planet": "ZHRA", "status": "Sa'd Atsal, Dost"}, {"planet": "ATRD", "status": "Sa'd, Dost"},
      {"planet": "QMAR", "status": "Nahas, Dushman"}, {"planet": "JAHL", "status": "Bad, Anfsal"}, {"planet": "MSTR", "status": "Sa'd Atsal,NA"}, {"planet": "MRKH", "status": "Nahas, Dushman"}, {"planet": "SHMS", "status": "Sa'dl, Dushman"}, {"planet": "ZHRA", "status": "Sa'd Atsal, Dost"}
    ],
    "NIGHT": [
      {"planet": "MRKH", "status": "Sa'd Atsal"}, {"planet": "SHMS", "status": "Sa'd Atsal,NA"}, {"planet": "ZHRA", "status": "Nahas, Dushman"}, {"planet": "ATRD", "status": "Sa'd, Dushman"}, {"planet": "QMAR", "status": "Sa'd Atsal, Dost"}, {"planet": "JAHL", "status": "Mumtaziz, Dost"},
      {"planet": "MSTR", "status": "Nahas, Dushman"}, {"planet": "MRKH", "status": "Bad, Anfsal"}, {"planet": "SHMS", "status": "Sa'd Atsal,NA"}, {"planet": "ZHRA", "status": "Sad"}, {"planet": "ATRD", "status": "Sa'd, Dushman"}, {"planet": "QMAR", "status": "Sa'd Atsal, Dost"}
    ]
  },
  "ITWAAR": {
    "DAY": [
      {"planet": "SHMS", "status": "Sa'd"}, {"planet": "ZHRA", "status": "Nahas, Dushman"}, {"planet": "ATRD", "status": "Mumtaziz-NA"}, {"planet": "QMAR", "status": "Nahas, Dost"}, {"planet": "JAHL", "status": "Bad, Dushman"}, {"planet": "MSTR", "status": "Sa'd, Dost"},
      {"planet": "MRKH", "status": "Nahas, Dost"}, {"planet": "SHMS", "status": "Sa'd Atsal"}, {"planet": "ZHRA", "status": "Sa'd Atsal, Dushman"}, {"planet": "ATRD", "status": "Mumtaziz, NA"}, {"planet": "QMAR", "status": "Mumtaziz, Dost"}, {"planet": "JAHL", "status": "Bad, Dushman"}
    ],
    "NIGHT": [
      {"planet": "ATRD", "status": "Sa'd Atsal"}, {"planet": "QMAR", "status": "Nahas, Dushman"}, {"planet": "JAHL", "status": "Sad Anfasal"}, {"planet": "MSTR", "status": "Nahas, Dost"}, {"planet": "MRKH", "status": "Nahas Anfasal"}, {"planet": "SHMS", "status": "Sa'd, Dost"},
      {"planet": "ZHRA", "status": "Nahas, Dost"}, {"planet": "ATRD", "status": "Sa'd"}, {"planet": "QMAR", "status": "Sa'd Atsal, Dushman"}, {"planet": "JAHL", "status": "Sad"}, {"planet": "MSTR", "status": "Mumtaziz, Dost"}, {"planet": "MRKH", "status": "Nahas Anfasal"}
    ]
  },
  "PEER": {
    "DAY": [
      {"planet": "QMAR", "status": "Sa'd Atsal"}, {"planet": "JAHL", "status": "Sa'd Anfasal, NA"}, {"planet": "MSTR", "status": "Sa'd Atsal, NA"}, {"planet": "MRKH", "status": "Nahas, NA"}, {"planet": "SHMS", "status": "Sa'd Atsal, Dost"}, {"planet": "ZHRA", "status": "Mumtaziz, NA"},
      {"planet": "ATRD", "status": "Nahas Atsal, Dost"}, {"planet": "QMAR", "status": "Sa'd Atsal"}, {"planet": "JAHL", "status": "Nahas, NA"}, {"planet": "MSTR", "status": "Sa'd Atsal, NA"}, {"planet": "MRKH", "status": "Bad, NA"}, {"planet": "SHMS", "status": "Sa'd Atsal, Dost"}
    ],
    "NIGHT": [
      {"planet": "MSTR", "status": "Sa'd Atsal"}, {"planet": "MRKH", "status": "Sad Anfasal"}, {"planet": "SHMS", "status": "Sa'd Atsal,"}, {"planet": "ZHRA", "status": "Nahas Atsa"}, {"planet": "ATRD", "status": "Sa'd Atsal,"}, {"planet": "QMAR", "status": "Mumtaziz"},
      {"planet": "JAHL", "status": "Nahas Atsal"}, {"planet": "MSTR", "status": "Sa'd Atsal"}, {"planet": "MRKH", "status": "Nahas Anfasal"}, {"planet": "SHMS", "status": "Sa'd Atsal,"}, {"planet": "ZHRA", "status": "Nahas Anfasal"}, {"planet": "ATRD", "status": "Sad Atsal"}
    ]
  },
  "MANGAL": {
    "DAY": [
      {"planet": "MRKH", "status": "Sa'd"}, {"planet": "SHMS", "status": "Nahas, Dost"}, {"planet": "ZHRA", "status": "Sa'd Atsal, NA"}, {"planet": "ATRD", "status": "Sa'd, Dushman"}, {"planet": "QMAR", "status": "Nahas, Dost"}, {"planet": "JAHL", "status": "Bad, NA"},
      {"planet": "MSTR", "status": "Sa'd Atsal, Dost"}, {"planet": "MRKH", "status": "Nahas"}, {"planet": "SHMS", "status": "Sa'd Atsal, Dost"}, {"planet": "ZHRA", "status": "Nahas, NA"}, {"planet": "ATRD", "status": "Sa'd Anfasal, Dushman"}, {"planet": "QMAR", "status": "Nahas, Dost"}
    ],
    "NIGHT": [
      {"planet": "ZHRA", "status": "Nahas Anfasal"}, {"planet": "ATRD", "status": "Nahas, Dost"}, {"planet": "QMAR", "status": "Sa'd Atsal, NA"}, {"planet": "JAHL", "status": "Sa'd, Dushman"}, {"planet": "MSTR", "status": "Nahas, Dost"}, {"planet": "MRKH", "status": "Nahas Atsal, NA"},
      {"planet": "SHMS", "status": "Sa'd Atsal, Dost"}, {"planet": "ZHRA", "status": "Bad"}, {"planet": "ATRD", "status": "Sa'd Atsal, Dost"}, {"planet": "QMAR", "status": "Nahas, NA"}, {"planet": "JAHL", "status": "Sa'd Anfasal, Dushman"}, {"planet": "MSTR", "status": "Nahas Atsal, Dost"}
    ]
  },
  "BUDH": {
    "DAY": [
      {"planet": "ATRD", "status": "Sa'd Atsal"}, {"planet": "QMAR", "status": "Nahas, Dushman"}, {"planet": "JAHL", "status": "Bad Atsal, NA"}, {"planet": "MSTR", "status": "Sa'd, NA"}, {"planet": "MRKH", "status": "Nahas, NA"}, {"planet": "SHMS", "status": "Sa'd Anfsal, Dost"},
      {"planet": "ZHRA", "status": "Sa'd Atsal, Dost"}, {"planet": "ATRD", "status": "Sa'd Anfsal"}, {"planet": "QMAR", "status": "Nahas, Dushman"}, {"planet": "JAHL", "status": "Sa'd Atsal, NA"}, {"planet": "MSTR", "status": "Sa'd Atsal, NA"}, {"planet": "MRKH", "status": "Nahas, NA"}
    ],
    "NIGHT": [
      {"planet": "JAHL", "status": "Sa'd Atsal"}, {"planet": "MSTR", "status": "Nahas, Dushman"}, {"planet": "MRKH", "status": "Bad Atsal, NA"}, {"planet": "SHMS", "status": "Sa'd, NA"}, {"planet": "ZHRA", "status": "Bad, NA"}, {"planet": "ATRD", "status": "Sa'd Anfsal, Dost"},
      {"planet": "QMAR", "status": "Sa'd Atsal, Dost"}, {"planet": "JAHL", "status": "Sa'd Anfsal"}, {"planet": "MSTR", "status": "Bad,"}, {"planet": "MRKH", "status": "Sa'd Atsal, NA"}, {"planet": "SHMS", "status": "Sa'd Atsal, NA"}, {"planet": "ZHRA", "status": "Bad Atsal,"}
    ]
  },
  "JUMERAAT": {
    "DAY": [
      {"planet": "MSTR", "status": "Sa'd Atsal"}, {"planet": "MRKH", "status": "Bad Atsal, Dost"}, {"planet": "SHMS", "status": "Sa'd Atsal, Dost"}, {"planet": "ZHRA", "status": "Sa'd Atsal, Dushman"}, {"planet": "ATRD", "status": "Sa'd Atsal, Dushman"}, {"planet": "QMAR", "status": "Sa'd Anfasal, Dost"},
      {"planet": "JAHL", "status": "Nahas, NA"}, {"planet": "MSTR", "status": "Sa'd Atsal"}, {"planet": "MRKH", "status": "Sa'd Atsal, Dost"}, {"planet": "SHMS", "status": "Sa'd Atsal, Dost"}, {"planet": "ZHRA", "status": "Sa'd Atsal, Dushman"}, {"planet": "ATRD", "status": "Nahas, Dushman"}
    ],
    "NIGHT": [
      {"planet": "SHMS", "status": "Sa'd Atsal"}, {"planet": "ZHRA", "status": "Bad Atsal, Dost"}, {"planet": "ATRD", "status": "Sa'd Atsal, Dost"}, {"planet": "QMAR", "status": "Sa'd Atsal, Dushman"}, {"planet": "JAHL", "status": "Sa'd Atsal, Dushman"}, {"planet": "MSTR", "status": "Sa'd Anfasal, Dost"},
      {"planet": "MRKH", "status": "Nahas Atsal, NA"}, {"planet": "SHMS", "status": "Sa'd Atsal"}, {"planet": "ZHRA", "status": "Sa'd Atsal, Dost"}, {"planet": "ATRD", "status": "Sa'd, Dost"}, {"planet": "QMAR", "status": "Sa'd Atsal, Dushman"}, {"planet": "JAHL", "status": "Nahas, Dushman"}
    ]
  }
}

ABJAD_MAP = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9, 'ی': 10,
    'ک': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100,
    'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 80, 'g': 3, 'h': 8, 'i': 10, 'j': 3,
    'k': 20, 'l': 30, 'm': 40, 'n': 50, 'o': 6, 'p': 2, 'q': 100, 'r': 200, 's': 60,
    't': 400, 'u': 6, 'v': 6, 'w': 6, 'x': 60, 'y': 10, 'z': 7
}

ACTION_PROFILES = {
    "MSTR": "💰 Financial signatures, massive trades, expansions, or asking high officers for support.",
    "ZHRA": "❤️ Emotional harmony reconciliation, buying jewelry/luxuries, or hosting events.",
    "SHMS": "🏛️ Corporate presentations, brand launches, public outreach, and high prominence tasks.",
    "ATRD": "📝 Software debugging, mathematical data compiling, writing, and negotiating contracts.",
    "QMAR": "🌊 Short local travel loops, domestic configurations, culinary operations, or reflection.",
    "MRKH": "💪 Intense physical activity, removing unviable nodes, and breaking tough habits.",
    "JAHL": "⏳ Cold file archiving, detail auditing, tedious records cleanup, and endurance tasks."
}

def compute_abjad(text_in):
    return sum(ABJAD_MAP.get(c, 0) for char in text_in.lower() for c in char) or 100

# --- SYSTEM PARAMETERS ---
current_city = "Biswan, Uttar Pradesh, India"
current_lat, current_lon = 27.4925, 81.0003
current_timezone_str = "Asia/Kolkata"

loc_tz = pytz.timezone(current_timezone_str)
now = datetime.datetime.now(loc_tz)

# Calculate Solar System Vectors
obs = Observer(latitude=current_lat, longitude=current_lon, elevation=0.0)
s = sun(obs, date=now.date(), tzinfo=loc_tz)
tuloo, guroob = s['sunrise'], s['sunset']

s_next = sun(obs, date=now.date() + datetime.timedelta(days=1), tzinfo=loc_tz)
next_tuloo = s_next['sunrise']
s_prev = sun(obs, date=now.date() - datetime.timedelta(days=1), tzinfo=loc_tz)
prev_guroob = s_prev['sunset']

is_day = tuloo <= now < guroob
if is_day:
    period_key, base_start, total_sec = "DAY", tuloo, (guroob - tuloo).total_seconds()
else:
    period_key = "NIGHT"
    base_start, total_sec = (guroob, (next_tuloo - guroob).total_seconds()) if now >= guroob else (prev_guroob, (tuloo - prev_guroob).total_seconds())

hour_interval = total_sec / 12
elapsed_sec = (now - base_start).total_seconds()
current_idx = min(max(int(elapsed_sec // hour_interval), 0), 11)

days_map = {0: "PEER", 1: "MANGAL", 2: "BUDH", 3: "JUMERAAT", 4: "JUMA", 5: "HAFTA", 6: "ITWAAR"}
current_day_str = days_map[now.weekday()]

saat_start_time = base_start + datetime.timedelta(seconds=current_idx * hour_interval)
saat_end_time = base_start + datetime.timedelta(seconds=(current_idx + 1) * hour_interval)
progress_percent = min(max((now - saat_start_time).total_seconds() / hour_interval, 0.0), 1.0)

# 3-Part Micro-Hour Segment Splitting
one_third = hour_interval / 3
part_1_end = saat_start_time + datetime.timedelta(seconds=one_third)
part_2_end = saat_start_time + datetime.timedelta(seconds=2 * one_third)

if now < part_1_end:
    active_part, part_desc = "First Part", "🌱 Inception / Dawn Phase — Wavelength settling. Prepare and organize."
    p1_s, p2_s, p3_s = "⚡ RUNNING NOW", "⏳ Waiting", "⏳ Waiting"
elif now < part_2_end:
    active_part, part_desc = "Middle Part", "🔥 Zenith Peak — Pure celestial concentration. Maximum force window!"
    p1_s, p2_s, p3_s = "✅ Done", "⚡ RUNNING NOW", "⏳ Waiting"
else:
    active_part, part_desc = "Last Part", "🍂 Transition Phase — Energy fading. Wrap up, wind down, and clear residue."
    p1_s, p2_s, p3_s = "✅ Done", "✅ Done", "⚡ RUNNING NOW"

active_day_list = SAAT_DATABASE[current_day_str][period_key]
current_saat = active_day_list[current_idx]
last_saat = active_day_list[current_idx - 1] if current_idx > 0 else {"planet": "None", "status": "N/A"}
next_saat = active_day_list[current_idx + 1] if current_idx < 11 else {"planet": "None", "status": "N/A"}

# --- DASHBOARD RENDERING ---
st.title("🌌 Sa'at Strategic Action Planner")
st.caption(f"📍 Node: {current_city} | 🕒 Local Watch Time: {now.strftime('%I:%M:%S %p')}")

col_tulu, col_guroob = st.columns(2)
col_tulu.info(f"🌅 **Tuloo Aftab (Sunrise):** {tuloo.strftime('%I:%M:%S %p')}")
col_guroob.info(f"🌇 **Guroob Aftab (Sunset):** {guroob.strftime('%I:%M:%S %p')}")

# Numerological Affinity Calculator Panel
st.markdown("---")
st.markdown("### 🧬 Jazbul Quloob Affinity Decoder")
col_s, col_t = st.columns(2)
seeker_name = col_s.text_input("Seeker Name (You):", "Ali")
target_name = col_t.text_input("Target Objective (Person/Venture):", "Enterprise")

v_seeker = compute_abjad(seeker_name)
v_target = compute_abjad(target_name)
affinity_metric = int(((v_seeker + v_target) % 35) + 65)

st.markdown(f"""
<div style='background-color: #1e222a; padding: 10px; border-radius: 8px; text-align: center; color: white;'>
    🔢 Abjad Seeker: <b>{v_seeker}</b> | 🔢 Abjad Target: <b>{v_target}</b> | 🔮 Attraction Affinity: <span style='color: #00ffcc; font-weight: bold;'>{affinity_metric}% Vector Match</span>
</div>
""", unsafe_allow_html=True)

# Main Active Clock Interface
st.markdown("---")
st.markdown(f"## 🪐 Active Hour State ({current_day_str})")

status_str = current_saat['status'].lower()
bg, border = ("#D4EDDA", "#155724") if "sa'd" in status_str or "sad" in status_str else (("#F8D7DA", "#721C24") if "nahas" in status_str or "bad" in status_str else ("#FFF3CD", "#856404"))

st.markdown(f"""
<div style='background-color: {bg}; border: 2px solid {border}; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px;'>
    <h1 style='color: {border}; margin: 0; font-size: 34px;'>{current_saat['planet']} Hour</h1>
    <p style='color: {border}; font-size: 19px; font-weight: bold; margin: 8px 0;'>📊 Evaluation: {current_saat['status']}</p>
    <div style='color: {border}; font-size: 15px; font-weight: bold; border-top: 1px dashed {border}; padding-top: 8px;'>
        📌 Phase Status: {active_part.upper()} — {part_desc}
    </div>
</div>
""", unsafe_allow_html=True)

st.write(f"💡 **Action Guide:** {ACTION_PROFILES.get(current_saat['planet'])}")

c_s, c_e = st.columns(2)
c_s.metric("🕒 Sa'at Hour Commenced At", saat_start_time.strftime("%I:%M:%S %p"))
c_e.metric("⏳ Sa'at Hour Concludes At", saat_end_time.strftime("%I:%M:%S %p"))

st.write(f"**Total Block Progress Matrix:** {int(progress_percent * 100)}% complete")
st.progress(progress_percent)

# Dynamic Phase Matrix Representation
st.markdown("### 🕒 Triple-Phase Micro Blocks")
cp1, cp2, cp3 = st.columns(3)
with cp1:
    b1 = "3px solid #ff4b4b" if "RUNNING" in p1_s else "1px solid #ddd"
    st.markdown(f"<div style='background:#f9f9f9; padding:8px; border-radius:6px; border:{b1}; text-align:center;'><small><b>1st Third</b><br/>{p1_s}</small></div>", unsafe_allow_html=True)
with cp2:
    b2 = "3px solid #ff4b4b" if "RUNNING" in p2_s else "1px solid #ddd"
    st.markdown(f"<div style='background:#f9f9f9; padding:8px; border-radius:6px; border:{b2}; text-align:center;'><small><b>Mid Third (Peak)</b><br/>{p2_s}</small></div>", unsafe_allow_html=True)
with cp3:
    b3 = "3px solid #ff4b4b" if "RUNNING" in p3_s else "1px solid #ddd"
    st.markdown(f"<div style='background:#f9f9f9; padding:8px; border-radius:6px; border:{b3}; text-align:center;'><small><b>Last Third</b><br/>{p3_s}</small></div>", unsafe_allow_html=True)

# Context Cards Lookahead
st.markdown("<br/>### 🗺️ Context Sequence Map", unsafe_allow_html=True)
col_l, col_n = st.columns(2)
with col_l:
    st.markdown(f"<div style='background-color:#f0f2f6; padding:10px; border-radius:8px; border-left:5px solid #6c757d;'>⏮️ <b>LAST HOUR</b><br/><h4>{last_saat['planet']}</h4><small>{last_saat['status']}</small></div>", unsafe_allow_html=True)
with col_n:
    st.markdown(f"<div style='background-color:#f0f2f6; padding:10px; border-radius:8px; border-left:5px solid #007bff;'>⏭️ <b>COMING NEXT</b><br/><h4>{next_saat['planet']}</h4><small>{next_saat['status']}</small></div>", unsafe_allow_html=True)

# Full Matrix Layout Table Block
st.markdown("---")
st.markdown(f"### 📅 Complete {period_key} Schedule Matrix")
full_schedule_table = []
for index, item in enumerate(active_day_list):
    h_start = base_start + datetime.timedelta(seconds=index * hour_interval)
    h_end = base_start + datetime.timedelta(seconds=(index + 1) * hour_interval)
    full_schedule_table.append({
        "Hour": f"Hour {index + 1}",
        "Start Time": h_start.strftime("%I:%M %p"),
        "End Time": h_end.strftime("%I:%M %p"),
        "Planet Ruler": item['planet'],
        "Evaluation": item['status'],
        "Live Status": "🎯 ACTIVE NOW" if index == current_idx else "⏳ Waiting"
    })
st.table(full_schedule_table)
st.button("🔄 Force Real-Time Synchronization")
