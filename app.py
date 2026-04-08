import streamlit as st
import pandas as pd
import io

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN (MOBILE-FIRST)
# ---------------------------------------------------------
st.set_page_config(
    page_title="FTTH Planner",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.stButton > button { border-radius: 8px; font-weight: 600; padding: 10px 0; }
    hr { margin: 15px 0 25px 0 !important; border-color: #eeeeee; }
    
    .timeline-node {
        border-left: 4px solid #007BFF;
        padding-left: 15px;
        margin-bottom: 25px;
        position: relative;
    }
    .timeline-node::before {
        content: '';
        position: absolute;
        width: 14px; height: 14px;
        background: #007BFF;
        border-radius: 50%;
        left: -9px; top: 0;
    }
    .timeline-node.terminasi { border-left-color: #28A745; }
    .timeline-node.terminasi::before { background: #28A745; }

    /* Box Hasil Rx dengan kontras tinggi */
    .rx-box {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        color: #000000 !important; /* Memastikan teks tetap hitam */
        display: inline-block;
        margin-top: 5px;
    }
    .rx-aman { background-color: #2ECC71; }
    .rx-bahaya { background-color: #E74C3C; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. DATABASE KONSTANTA REDAMAN
# ---------------------------------------------------------
LOSS_RASIO = {
    "01:99": [20.20, 0.24], "02:98": [17.19, 0.29], "03:97": [15.43, 0.33],
    "04:96": [14.18, 0.38], "05:95": [13.21, 0.42], "06:94": [12.42, 0.47],
    "07:93": [11.75, 0.52], "08:92": [11.17, 0.56], "09:91": [10.66, 0.61],
    "10:90": [10.20, 0.66], "12:88": [9.41, 0.76],  "15:85": [8.44, 0.91],
    "18:82": [7.65, 1.06],  "20:80": [7.19, 1.17],  "22:78": [6.78, 1.28],
    "25:75": [6.22, 1.45],  "28:72": [5.73, 1.63],  "30:70": [5.43, 1.75],
    "35:65": [4.76, 2.07],  "40:60": [4.18, 2.42],  "45:55": [3.67, 2.80],
    "50:50": [3.21, 3.21]
}

LOSS_PLC = {
    "1:2": 3.25, "1:4": 7.00, "1:8": 10.00, 
    "1:16": 13.50, "1:32": 17.00, "1:64": 20.00
}

LOSS_KABEL_PER_KM = 0.3
LOSS_KONEKTOR = 0.3
LOSS_SPLICING = 0.03

# ---------------------------------------------------------
# 4. STATE MANAGEMENT
# ---------------------------------------------------------
if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
def change_page(page_name): st.session_state.page = page_name

# ---------------------------------------------------------
# 5. DASHBOARD
# ---------------------------------------------------------
def show_dashboard():
    st.title("🌐 FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    if st.button("📡 Kalkulator Redaman", key="btn_kalkulator", use_container_width=True, type="primary"): 
        change_page('Kalkulator'); st.rerun()
    st.write("")
    if st.button("🔗 Auto Planner (Linear)", key="btn_auto", use_container_width=True, type="primary"): 
        change_page('AutoPlanner'); st.rerun()
    st.write("")
    if st.button("🖧 Advance Planner", key="btn_advance", use_container_width=True, type="primary"): 
        change_page('AdvancePlanner'); st.rerun()

    st.write("---")
    st.markdown("### 📁 Proyek Terakhir")
    st.info("Belum ada proyek yang disimpan.")

# ---------------------------------------------------------
# 6. KALKULATOR
# ---------------------------------------------------------
def show_kalkulator():
    if st.button("⬅ Kembali"): change_page('Dashboard'); st.rerun()
    st.subheader("📡 Kalkulator Redaman")
    st.write("---")

    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50)
    opsi = list(LOSS_RASIO.keys()) + ["--- PLC ---"] + list(LOSS_PLC.keys())
    pilihan = st.selectbox("Splitter", options=opsi, index=9)
    
    if "PLC" in pilihan and pilihan != "--- PLC ---":
        l_plc = LOSS_PLC[pilihan]
        out = power_in - l_plc
        st.success(f"Output: {out:+.2f} dBm (Loss: {l_plc} dB)")
    elif pilihan in LOSS_RASIO:
        lk, lb = LOSS_RASIO[pilihan]
        st.write(f"Kaki Kecil: **{(power_in-lk):+.2f} dBm** | Kaki Besar: **{(power_in-lb):+.2f} dBm**")

# ---------------------------------------------------------
# 7. AUTO PLANNER (FIX LOGIC & UI)
# ---------------------------------------------------------
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def show_autoplanner():
    if st.button("⬅ Kembali"): change_page('Dashboard'); st.rerun()
    st.subheader("🔗 Auto Planner")
    
    with st.expander("⚙️ Parameter", expanded=True):
        p_in = st.number_input("Power OLT (dBm)", value=7.00)
        l_rx = st.number_input("Limit Rx (dBm)", value=-25.00)
        dist = st.number_input("Jarak Antar ODP (km)", value=0.10)
        plc_type = st.selectbox("PLC ODP", options=list(LOSS_PLC.keys()), index=2)
        conn = st.number_input("Konektor/ODP", value=2)

    if st.button("🚀 Generate", use_container_width=True, type="primary"):
        topologi = []
        curr_p = p_in
        total_d = 0.0
        idx = 1
        l_plc = LOSS_PLC[plc_type]
        l_extra = conn * LOSS_KONEKTOR

        while True:
            total_d += dist
            p_tiang = curr_p - (dist * LOSS_KABEL_PER_KM) - l_extra
            
            best_r = None
            # Cari rasio dari 01:99 ke 50:50
            for r, loss in LOSS_RASIO.items():
                rx = p_tiang - loss[0] - l_plc
                if rx >= l_rx:
                    best_r, rx_f, p_next = r, rx, p_tiang - loss[1]
                    break
            
            if best_r:
                topologi.append({"Node": f"ODP {idx}", "Tipe": "Rasio", "Rasio": best_r, "Jarak": round(total_d,2), "Rx": round(rx_f,2), "Next": round(p_next,2)})
                curr_p, idx = p_next, idx + 1
            else:
                # Cek Terminasi
                rx_t = p_tiang - l_plc
                if rx_t >= l_rx:
                    topologi.append({"Node": f"ODP {idx}", "Tipe": "Terminasi", "Rasio": "Direct PLC", "Jarak": round(total_d,2), "Rx": round(rx_t,2), "Next": None})
                break

        if not topologi:
            st.error("Power tidak cukup untuk ODP pertama.")
        else:
            st.download_button("📊 Export Excel", data=to_excel(pd.DataFrame(topologi)), file_name="ftth_plan.xlsx", use_container_width=True)
            for d in topologi:
                is_t = d['Tipe'] == "Terminasi"
                cls = "timeline-node terminasi" if is_t else "timeline-node"
                # Logika Warna
                rx_cls = "rx-aman" if d['Rx'] >= l_rx else "rx-bahaya"
                
                st.markdown(f"""
                <div class="{cls}">
                    <b>{d['Node']}</b> ({d['Jarak']} km)<br>
                    { '🏁 <b>TERMINASI</b>' if is_t else f'Rasio: <b>{d["Rasio"]}</b>' }<br>
                    <div class="rx-box {rx_cls}">Rx ONT: {d['Rx']:+.2f} dBm</div><br>
                    { f'<small style="color:#007BFF">Lanjut: {d["Next"]:+.2f} dBm</small>' if not is_t else '' }
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard': show_dashboard()
elif st.session_state.page == 'Kalkulator': show_kalkulator()
elif st.session_state.page == 'AutoPlanner': show_autoplanner()
elif st.session_state.page == 'AdvancePlanner': 
    if st.button("⬅ Kembali"): change_page('Dashboard'); st.rerun()
    st.write("Advance Planner - Coming Soon")
