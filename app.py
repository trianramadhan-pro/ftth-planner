import streamlit as st
import pandas as pd
import io
import json
import os
from datetime import datetime

# =========================================================
# DATABASE LOKAL (SISTEM PENYIMPANAN PERMANEN)
# =========================================================
DB_FILE = "proyek_ftth.json"

def load_projects():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return []
    return []

def save_projects(projects_list):
    with open(DB_FILE, "w") as f:
        json.dump(projects_list, f, indent=4)

# =========================================================
# VARIABEL SISTEM & CHANGELOG
# =========================================================
APP_VERSION = "v1.4.1 (UI Hotfix)"
CHANGELOG = """
**Catatan Rilis & Perbaikan (v1.4.1):**
- 🎨 **Fix (UI):** Tampilan daftar proyek telah dioptimalkan secara *native*. Sekarang mendukung **Dark Mode** & **Light Mode** secara otomatis.
- 📱 **Fix (Mobile):** Tombol "Buka/Edit" dan "Hapus" kini dipaksa tetap **berdampingan 50:50** di layar HP (tidak lagi bertumpuk raksasa ke bawah).
- 💾 **Fitur:** Data tersimpan secara permanen ke `proyek_ftth.json`.
- 🔄 **Routing:** Proyek dari Dashboard akan otomatis terbuka di fitur kalkulator asalnya (Auto/Advance).
"""

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(page_title="FTTH Planner", page_icon="🌐", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS UNTUK MOBILE & WARNA
# ---------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    div.stButton > button { border-radius: 8px; font-weight: 600; padding: 10px 0; }
    hr { margin: 15px 0 25px 0 !important; border-color: #555555; opacity: 0.3; }
    
    .timeline-node { border-left: 4px solid #007BFF; padding-left: 15px; margin-bottom: 25px; position: relative; }
    .timeline-node::before { content: ''; position: absolute; width: 14px; height: 14px; background: #007BFF; border-radius: 50%; left: -9px; top: 0; }
    .timeline-node.terminasi { border-left-color: #28A745; }
    .timeline-node.terminasi::before { background: #28A745; }
    
    /* Box warna cerah untuk hasil Kalkulator (Tetap statis karena kontras dengan tulisan putih) */
    .rx-box { padding: 4px 10px; border-radius: 5px; font-weight: bold; color: #ffffff !important; display: inline-block; margin-top: 4px; }
    .rx-aman { background-color: #2ECC71; } .rx-bahaya { background-color: #E74C3C; }
    
    /* =====================================================
       CSS HACK SUPER MOBILE: Memaksa st.columns tetap sejajar di HP!
       Ini akan mencegah tombol Buka & Hapus bertumpuk ke bawah.
       ===================================================== */
    @media screen and (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 10px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. KONSTANTA REDAMAN
# ---------------------------------------------------------
LOSS_RASIO = {
    "01:99": [20.20, 0.24], "02:98": [17.19, 0.29], "03:97": [15.43, 0.33], "04:96": [14.18, 0.38], "05:95": [13.21, 0.42], "06:94": [12.42, 0.47],
    "07:93": [11.75, 0.52], "08:92": [11.17, 0.56], "09:91": [10.66, 0.61], "10:90": [10.20, 0.66], "12:88": [9.41, 0.76],  "15:85": [8.44, 0.91],
    "18:82": [7.65, 1.06],  "20:80": [7.19, 1.17],  "22:78": [6.78, 1.28], "25:75": [6.22, 1.45],  "28:72": [5.73, 1.63],  "30:70": [5.43, 1.75],
    "35:65": [4.76, 2.07],  "40:60": [4.18, 2.42],  "45:55": [3.67, 2.80], "50:50": [3.21, 3.21]
}
LOSS_PLC = {"1:2": 3.25, "1:4": 7.00, "1:8": 10.00, "1:16": 13.50, "1:32": 17.00, "1:64": 20.00}
LOSS_KABEL_PER_KM = 0.3; LOSS_KONEKTOR = 0.3; LOSS_SPLICING = 0.03

# ---------------------------------------------------------
# 4. STATE MANAGEMENT
# ---------------------------------------------------------
if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
if 'saved_projects' not in st.session_state: st.session_state.saved_projects = load_projects()

if 'ap_generated' not in st.session_state: st.session_state.ap_generated = False
if 'ap_topologi' not in st.session_state: st.session_state.ap_topologi = []
if 'ap_summary' not in st.session_state: st.session_state.ap_summary = ""
if 'ap_params' not in st.session_state: st.session_state.ap_params = {}

def go_dashboard_and_reset():
    st.session_state.ap_generated = False
    st.session_state.page = 'Dashboard'
    st.rerun()

# ---------------------------------------------------------
# 5. HALAMAN: DASHBOARD
# ---------------------------------------------------------
def show_dashboard():
    st.title("🌐 FTTH Planner")
    
    # Changelog bisa dibuka tutup (Tersimpan di atas)
    with st.expander(f"🚀 Info Rilis & Changelog ({APP_VERSION})"):
        st.markdown(CHANGELOG)

    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    st.markdown("### 📡 Kalkulator Redaman")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Hitung loss instan untuk Spliter Rasio maupun PLC di 1 titik ODP.</p>", unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True, type="primary"): st.session_state.page = 'Kalkulator'; st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🔗 Auto Planner (Linear)")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Otomatisasi draf topologi ODP berantai lurus dari OLT ke tiang akhir.</p>", unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True, type="primary"): st.session_state.page = 'AutoPlanner'; st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🖧 Advance Planner")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Kanvas interaktif untuk modifikasi topologi kompleks.</p>", unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True, type="primary"): st.session_state.page = 'AdvancePlanner'; st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # -------------------------------------
    # RENDER DAFTAR PROYEK (NATIVE UI - SUPPORT DARK MODE)
    # -------------------------------------
    st.markdown("### 📁 Proyek Tersimpan")
    if len(st.session_state.saved_projects) > 0:
        for i, proj in enumerate(reversed(st.session_state.saved_projects)):
            real_index = len(st.session_state.saved_projects) - 1 - i
            
            # Menggunakan Native Container (Cocok untuk Dark Mode & Light Mode)
            with st.container(border=True):
                st.subheader(f"📂 {proj['nama']}")
                st.markdown(f"**Mode:** `{proj['tipe']}` &nbsp;|&nbsp; **Power:** `{proj['power']} dBm` &nbsp;|&nbsp; **Total:** `{proj['nodes']} ODP`")
                st.caption(f"🕒 Terakhir dimodifikasi: {proj['date']}")
                st.info(f"**Ringkasan Spliter:**\n{proj['summary']}")
                
                # Tombol Aksi Berdampingan (Di-handle CSS HACK agar tidak turun di HP)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✏️ Buka / Edit", key=f"edit_{real_index}", use_container_width=True):
                        st.session_state.ap_topologi = proj['data']
                        st.session_state.ap_params = proj['params']
                        st.session_state.ap_summary = proj['summary']
                        if proj['tipe'] == "Auto Planner":
                            st.session_state.ap_generated = True
                            st.session_state.page = 'AutoPlanner'
                        else:
                            st.session_state.page = 'AdvancePlanner'
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ Hapus Proyek", key=f"del_{real_index}", use_container_width=True):
                        st.session_state.saved_projects.pop(real_index)
                        save_projects(st.session_state.saved_projects) # Hapus dr JSON
                        st.rerun()
    else:
        st.info("Belum ada proyek. Gunakan Auto Planner untuk membuat draf baru yang akan tersimpan permanen.")

# ---------------------------------------------------------
# 6. HALAMAN: KALKULATOR REDAMAN
# ---------------------------------------------------------
def show_kalkulator():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali"): go_dashboard_and_reset()
    with col2: st.subheader("📡 Kalkulator Redaman")
    st.write("---")

    with st.expander("📊 Lihat Tabel Referensi"):
        tb1, tb2 = st.columns(2)
        with tb1:
            st.markdown("**Spliter Rasio**")
            st.dataframe(pd.DataFrame([{"Rasio": k, "Drop": v[0], "Pass": v[1]} for k, v in LOSS_RASIO.items()]), hide_index=True, use_container_width=True)
        with tb2:
            st.markdown("**Spliter PLC**")
            st.dataframe(pd.DataFrame([{"PLC": k, "Loss (dB)": v} for k, v in LOSS_PLC.items()]), hide_index=True, use_container_width=True)

    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50)
    pilihan = st.selectbox("Pilih Jenis Splitter", options=list(LOSS_RASIO.keys()) + ["--- PLC Splitter ---"] + list(LOSS_PLC.keys()), index=9)
    if pilihan == "--- PLC Splitter ---": return

    with st.expander("Redaman Jalur / Kabel (Opsional)"):
        jarak_km = st.number_input("Jarak Kabel (km)", value=0.0, step=0.1)
        jml_konektor = st.number_input("Konektor/Barel", value=0, step=1)
        jml_splicing = st.number_input("Splicing", value=0, step=1)
    
    loss_jalur = (jarak_km * LOSS_KABEL_PER_KM) + (jml_konektor * LOSS_KONEKTOR) + (jml_splicing * LOSS_SPLICING)
    power_sebelum_split = power_in - loss_jalur
    st.write("---")

    if pilihan in LOSS_RASIO:
        lk, lb = LOSS_RASIO[pilihan]
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div style="background:#E74C3C;color:white;padding:10px;border-radius:8px;text-align:center;"><small>Kaki Kecil ({pilihan.split(":")[0]}%)</small><br><b style="font-size:18px;">{(power_sebelum_split-lk):+.2f} dBm</b></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="background:#3498DB;color:white;padding:10px;border-radius:8px;text-align:center;"><small>Kaki Besar ({pilihan.split(":")[1]}%)</small><br><b style="font-size:18px;">{(power_sebelum_split-lb):+.2f} dBm</b></div>', unsafe_allow_html=True)
    elif pilihan in LOSS_PLC:
        st.markdown(f'<div style="background:#2ECC71;color:white;padding:15px;border-radius:8px;text-align:center;">Output Semua Port<br><b style="font-size:22px;">{(power_sebelum_split-LOSS_PLC[pilihan]):+.2f} dBm</b></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. HALAMAN: AUTO PLANNER
# ---------------------------------------------------------
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False)
    return output.getvalue()

def show_autoplanner():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali & Reset"): go_dashboard_and_reset()
    with col2: st.subheader("🔗 Auto Planner")
    
    loaded_params = st.session_state.get('ap_params', {})
    
    with st.expander("⚙️ Parameter Jaringan", expanded=True):
        p_in = st.number_input("Power OLT (dBm)", value=float(loaded_params.get("p_in", 7.00)), step=0.50)
        l_rx = st.number_input("Limit Rx (dBm)", value=float(loaded_params.get("l_rx", -25.00)), step=0.50)
        dist = st.number_input("Jarak Antar ODP (km)", value=float(loaded_params.get("dist", 0.10)), step=0.05)
        
        plc_keys = list(LOSS_PLC.keys())
        saved_plc = loaded_params.get("plc_type", "1:8")
        plc_idx = plc_keys.index(saved_plc) if saved_plc in plc_keys else 2
        plc_type = st.selectbox("PLC ODP", options=plc_keys, index=plc_idx)
        
        conn = st.number_input("Konektor/ODP", value=int(loaded_params.get("conn", 2)), step=1)

    if st.button("🚀 Generate Topologi", use_container_width=True, type="primary"):
        topologi = []
        curr_p = p_in
        total_d = 0.0
        idx = 1
        l_plc = LOSS_PLC[plc_type]
        l_extra = conn * LOSS_KONEKTOR
        rasio_counts = {}

        while True:
            total_d += dist
            p_tiang = curr_p - (dist * LOSS_KABEL_PER_KM) - l_extra
            best_r = None
            
            for r, loss in LOSS_RASIO.items():
                drop_kecil = p_tiang - loss[0]
                rx = drop_kecil - l_plc
                if rx >= l_rx:
                    best_r, drop_f, rx_f, p_next = r, drop_kecil, rx, p_tiang - loss[1]
                    break
            
            if best_r:
                topologi.append({"Node": f"ODP {idx}", "Tipe": "Rasio", "Rasio": best_r, "Drop_Kecil": round(drop_f,2), "Jarak": round(total_d,2), "Rx": round(rx_f,2), "Next": round(p_next,2)})
                rasio_counts[best_r] = rasio_counts.get(best_r, 0) + 1
                curr_p, idx = p_next, idx + 1
            else:
                rx_t = p_tiang - l_plc
                if rx_t >= l_rx:
                    topologi.append({"Node": f"ODP {idx}", "Tipe": "Terminasi", "Rasio": "Direct PLC", "Drop_Kecil": round(p_tiang,2), "Jarak": round(total_d,2), "Rx": round(rx_t,2), "Next": None})
                break

        if not topologi:
            st.error("Power tidak cukup untuk ditarik ke ODP pertama.")
            st.session_state.ap_generated = False
        else:
            summary_parts = [f"{count}x ({r})" for r, count in rasio_counts.items()]
            if topologi[-1]['Tipe'] == 'Terminasi': summary_parts.append("1x Terminasi")
            summary_text = ", ".join(summary_parts) + f" | Kotak PLC {plc_type}"

            st.session_state.ap_topologi = topologi
            st.session_state.ap_summary = summary_text
            st.session_state.ap_params = {"p_in": p_in, "l_rx": l_rx, "dist": dist, "plc_type": plc_type, "conn": conn, "l_plc": l_plc}
            st.session_state.ap_generated = True

    if st.session_state.ap_generated:
        topologi = st.session_state.ap_topologi
        st.write("---")
        st.success(f"✅ ESTIMASI: MAKSIMAL {len(topologi)} ODP")
        st.info(f"**Tipe Spliter:**\n{st.session_state.ap_summary}")
        
        st.markdown("**Simpan / Ekspor Hasil:**")
        nama_proyek = st.text_input("Nama Proyek:", placeholder="Contoh: Jalur Mawar", key="input_nama_proyek")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            df_export = pd.DataFrame(topologi).rename(columns={'Drop_Kecil': 'Input PLC (dBm)'})
            st.download_button("📊 Export Excel", data=to_excel(df_export), file_name="ftth_plan.xlsx", use_container_width=True)
        with btn_col2:
            if st.button("💾 Simpan Proyek", use_container_width=True):
                if nama_proyek.strip() == "":
                    st.warning("⚠️ Nama proyek tidak boleh kosong!")
                else:
                    new_project = {
                        "nama": nama_proyek, "tipe": "Auto Planner", "nodes": len(topologi),
                        "power": st.session_state.ap_params["p_in"], "summary": st.session_state.ap_summary,
                        "date": datetime.now().strftime("%d %b %Y, %H:%M"), "data": topologi, "params": st.session_state.ap_params
                    }
                    st.session_state.saved_projects.append(new_project)
                    save_projects(st.session_state.saved_projects) # Simpan JSON
                    st.success(f"Proyek disimpan secara permanen!")

        if st.button("✏️ Lanjut Edit di Advance Planner", use_container_width=True, type="primary"):
            st.session_state.page = 'AdvancePlanner'
            st.rerun()

        st.write("---")
        for d in topologi:
            is_t = d['Tipe'] == "Terminasi"
            cls = "timeline-node terminasi" if is_t else "timeline-node"
            rx_cls = "rx-aman" if d['Rx'] >= st.session_state.ap_params["l_rx"] else "rx-bahaya"
            
            info_rasio = f'🏁 <b style="color:#28A745;">TERMINASI JALUR</b><br>' if is_t else f'Rasio: <b>{d["Rasio"]}</b><br>'
            info_kaki_kecil = f'<span style="font-size: 13px; color: gray;">Out Kaki Kecil: {d["Drop_Kecil"]:+.2f} dBm</span><br>'
            info_lanjut = f'<br><span style="color:#007BFF; font-weight:bold; font-size:14px;">⚡ Power Lanjut: {d["Next"]:+.2f} dBm</span>' if not is_t else ''

            st.markdown(f'<div class="{cls}"><b>{d["Node"]}</b> ({d["Jarak"]} km)<br>{info_rasio}{info_kaki_kecil}<div class="rx-box {rx_cls}">{d["Rx"]:+.2f} dBm</div>{info_lanjut}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. HALAMAN: ADVANCE PLANNER
# ---------------------------------------------------------
def show_advance():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali"): go_dashboard_and_reset()
    with col2: st.subheader("🖧 Advance Planner")
    st.write("---")
    
    draf = st.session_state.get('ap_topologi', [])
    if not draf:
        st.info("Pilih proyek dari **Dashboard** atau buat draf di **Auto Planner** terlebih dahulu.")
        return

    st.markdown(f"**Sumber OLT Backbone:** `{st.session_state.ap_params.get('p_in', 0):+.2f} dBm`")
    st.info(f"**Tipe Spliter:**\n{st.session_state.ap_summary}")
    st.write("Daftar Node (Mode Edit Interaktif sedang dibangun):")
    
    for i, node in enumerate(draf):
        with st.container(border=True):
            status_warna = "green" if node['Rx'] >= st.session_state.ap_params.get('l_rx', -25) else "red"
            st.markdown(f"**{node['Node']}** <span style='font-size:12px; color:gray;'>({node['Jarak']} km)</span>", unsafe_allow_html=True)
            st.markdown(f"Spliter: `{node['Rasio']}`")
            st.markdown(f"<span style='color:{status_warna}; font-weight:bold; font-size: 16px;'>Rx ONT: {node['Rx']:+.2f} dBm</span>", unsafe_allow_html=True)

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard': show_dashboard()
elif st.session_state.page == 'Kalkulator': show_kalkulator()
elif st.session_state.page == 'AutoPlanner': show_autoplanner()
elif st.session_state.page == 'AdvancePlanner': show_advance()
