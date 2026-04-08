import streamlit as st
import pandas as pd
import io

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
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
        position: absolute; width: 14px; height: 14px;
        background: #007BFF; border-radius: 50%;
        left: -9px; top: 0;
    }
    .timeline-node.terminasi { border-left-color: #28A745; }
    .timeline-node.terminasi::before { background: #28A745; }

    .rx-box {
        padding: 4px 10px; border-radius: 5px; font-weight: bold;
        color: #000000 !important; display: inline-block; margin-top: 4px;
    }
    .rx-aman { background-color: #2ECC71; }
    .rx-bahaya { background-color: #E74C3C; }
    
    /* CSS Khusus Advance Planner Node Card */
    .adv-node-card {
        background-color: #f8f9fa; border: 1px solid #e9ecef;
        border-radius: 8px; padding: 15px; margin-bottom: 10px;
        border-left: 5px solid #6c757d;
    }
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
# 4. STATE MANAGEMENT (MEMORI APLIKASI)
# ---------------------------------------------------------
if 'page' not in st.session_state: 
    st.session_state.page = 'Dashboard'
if 'draf_topologi' not in st.session_state: 
    st.session_state.draf_topologi = [] # Untuk menyimpan hasil Auto Planner
if 'global_params' not in st.session_state:
    st.session_state.global_params = {} # Menyimpan power awal dll

def change_page(page_name): 
    st.session_state.page = page_name

# ---------------------------------------------------------
# 5. HALAMAN: DASHBOARD
# ---------------------------------------------------------
def show_dashboard():
    st.title("🌐 FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    st.markdown("### 📡 Kalkulator Redaman")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Hitung loss instan di 1 titik ODP.</p>", unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True, type="primary"): 
        change_page('Kalkulator'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🔗 Auto Planner (Linear)")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Draf topologi ODP berantai otomatis.</p>", unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True, type="primary"): 
        change_page('AutoPlanner'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🖧 Advance Planner")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Modifikasi topologi kompleks (ODC/Cabang).</p>", unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True, type="primary"): 
        change_page('AdvancePlanner'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📁 Proyek Terakhir")
    if len(st.session_state.draf_topologi) > 0:
        st.success(f"Terdapat draf aktif dengan {len(st.session_state.draf_topologi)} node. Lanjutkan di Advance Planner.")
    else:
        st.info("Belum ada proyek yang disimpan.")

# ---------------------------------------------------------
# 6. HALAMAN: KALKULATOR REDAMAN
# ---------------------------------------------------------
def show_kalkulator():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("📡 Kalkulator Redaman")
    st.write("---")

    with st.expander("📊 Lihat Tabel Referensi"):
        tb1, tb2 = st.columns(2)
        with tb1: st.dataframe(pd.DataFrame([{"Rasio": k, "Drop": v[0], "Pass": v[1]} for k, v in LOSS_RASIO.items()]), hide_index=True)
        with tb2: st.dataframe(pd.DataFrame([{"PLC": k, "Loss": v} for k, v in LOSS_PLC.items()]), hide_index=True)

    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50, format="%.2f")
    opsi_splitter = list(LOSS_RASIO.keys()) + ["--- PLC Splitter ---"] + list(LOSS_PLC.keys())
    pilihan = st.selectbox("Pilih Jenis Splitter", options=opsi_splitter, index=9)
    if pilihan == "--- PLC Splitter ---": return

    with st.expander("Redaman Jalur / Kabel (Opsional)"):
        jarak_km = st.number_input("Jarak Kabel (km)", value=0.0, step=0.1)
        jml_konektor = st.number_input("Konektor/Barel", value=0, step=1)
        jml_splicing = st.number_input("Splicing", value=0, step=1)
    
    loss_jalur = (jarak_km * LOSS_KABEL_PER_KM) + (jml_konektor * LOSS_KONEKTOR) + (jml_splicing * LOSS_SPLICING)
    power_sebelum_split = power_in - loss_jalur
    st.write("---")

    if pilihan in LOSS_RASIO:
        lk, lb = LOSS_RASIO[pilihan][0], LOSS_RASIO[pilihan][1]
        ok, ob = power_sebelum_split - lk, power_sebelum_split - lb
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div style="background:#E74C3C;color:white;padding:10px;border-radius:8px;text-align:center;"><small>Kaki Kecil ({pilihan.split(":")[0]}%)</small><br><b>{ok:+.2f} dBm</b><br><small>Loss: {lk}</small></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="background:#3498DB;color:white;padding:10px;border-radius:8px;text-align:center;"><small>Kaki Besar ({pilihan.split(":")[1]}%)</small><br><b>{ob:+.2f} dBm</b><br><small>Loss: {lb}</small></div>', unsafe_allow_html=True)
    elif pilihan in LOSS_PLC:
        l_plc = LOSS_PLC[pilihan]
        st.markdown(f'<div style="background:#2ECC71;color:white;padding:15px;border-radius:8px;text-align:center;">Output ({pilihan})<br><b style="font-size:22px;">{(power_sebelum_split - l_plc):+.2f} dBm</b></div>', unsafe_allow_html=True)

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
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("🔗 Auto Planner")
    
    with st.expander("⚙️ Parameter", expanded=True):
        p_in = st.number_input("Power OLT (dBm)", value=7.00, step=0.50)
        l_rx = st.number_input("Limit Rx (dBm)", value=-25.00, step=0.50)
        dist = st.number_input("Jarak Antar ODP (km)", value=0.10, step=0.05)
        plc_type = st.selectbox("PLC ODP", options=list(LOSS_PLC.keys()), index=2)
        conn = st.number_input("Konektor/ODP", value=2, step=1)

    if st.button("🚀 Generate Topologi", use_container_width=True, type="primary"):
        st.write("---")
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
            for r, loss in LOSS_RASIO.items():
                drop_kecil = p_tiang - loss[0]
                rx = drop_kecil - l_plc
                if rx >= l_rx:
                    best_r, drop_f, rx_f, p_next = r, drop_kecil, rx, p_tiang - loss[1]
                    break
            
            if best_r:
                topologi.append({
                    "id": idx, "Node": f"ODP {idx}", "Tipe": "Rasio", "Rasio": best_r, 
                    "Drop_Kecil": round(drop_f,2), "Jarak_Tiang": dist, "Jarak_Total": round(total_d,2), 
                    "PLC": plc_type, "Konektor": conn, "Rx": round(rx_f,2), "Next": round(p_next,2)
                })
                curr_p, idx = p_next, idx + 1
            else:
                rx_t = p_tiang - l_plc
                if rx_t >= l_rx:
                    topologi.append({
                        "id": idx, "Node": f"ODP {idx}", "Tipe": "Terminasi", "Rasio": "Direct PLC", 
                        "Drop_Kecil": round(p_tiang,2), "Jarak_Tiang": dist, "Jarak_Total": round(total_d,2), 
                        "PLC": plc_type, "Konektor": conn, "Rx": round(rx_t,2), "Next": None
                    })
                break

        if not topologi:
            st.error("Gagal generate. Coba ubah parameter.")
        else:
            # 1. SIMPAN KE STATE UNTUK ADVANCE PLANNER
            st.session_state.draf_topologi = topologi
            st.session_state.global_params = {"p_in": p_in, "l_rx": l_rx, "l_plc": l_plc}

            st.success(f"✅ ESTIMASI: MAKSIMAL {len(topologi)} ODP")
            
            df_export = pd.DataFrame(topologi)[["Node", "Tipe", "Rasio", "Drop_Kecil", "Jarak_Total", "Rx"]]
            st.download_button("📊 Export Excel", data=to_excel(df_export), file_name="ftth_plan.xlsx", use_container_width=True)
            
            # 2. TOMBOL PINDAH KE ADVANCE PLANNER
            st.write("")
            if st.button("✏️ Edit Draf ini di Advance Planner", use_container_width=True):
                change_page('AdvancePlanner')
                st.rerun()
            st.write("---")
            
            for d in topologi:
                is_t = d['Tipe'] == "Terminasi"
                cls = "timeline-node terminasi" if is_t else "timeline-node"
                rx_cls = "rx-aman" if d['Rx'] >= l_rx else "rx-bahaya"
                info_r = f'🏁 <b style="color:#28A745;">TERMINASI</b><br>' if is_t else f'Rasio: <b>{d["Rasio"]}</b><br>'
                info_k = f'<span style="font-size:13px;color:gray;">Out Kaki Kecil: {d["Drop_Kecil"]:+.2f} dBm</span><br>'
                st.markdown(f'<div class="{cls}"><b>{d["Node"]}</b> ({d["Jarak_Total"]} km)<br>{info_r}{info_k}<div class="rx-box {rx_cls}">Rx ONT: {d["Rx"]:+.2f} dBm</div></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. HALAMAN: ADVANCE PLANNER (PROGRES TAHAP 1)
# ---------------------------------------------------------
def show_advance():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("🖧 Advance Planner")
    st.write("---")
    
    # Cek apakah ada data di memori
    draf = st.session_state.draf_topologi
    if not draf:
        st.warning("Belum ada draf topologi.")
        st.info("Silakan buat draf otomatis di menu **Auto Planner** terlebih dahulu, lalu klik 'Edit di Advance Planner'.")
        return

    # Tampilkan Header Info
    p_in = st.session_state.global_params.get("p_in", 0)
    st.markdown(f"**Sumber OLT / Backbone:** `{p_in:+.2f} dBm`")
    st.markdown("Berikut adalah rantai *node* jaringan Anda. Klik **Edit** untuk mengubah rasio/PLC pada tiang tertentu.")
    st.write("")

    # Loop menampilkan Node sebagai Kartu Interaktif
    for i, node in enumerate(draf):
        is_t = node['Tipe'] == "Terminasi"
        status_warna = "green" if node['Rx'] >= st.session_state.global_params.get("l_rx", -25) else "red"
        
        st.markdown(f"""
        <div class="adv-node-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{node['Node']}</strong> <span style="color:gray; font-size:12px;">(Jarak: {node['Jarak_Total']} km)</span><br>
                    <span style="font-size: 14px;">Spliter: {node['Rasio']} + {node['PLC']}</span><br>
                    <span style="color:{status_warna}; font-weight:bold; font-size: 14px;">Rx: {node['Rx']:+.2f} dBm</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tombol aksi diletakkan menggunakan kolom asli Streamlit agar bisa diklik
        col_act1, col_act2, col_act3 = st.columns([2, 2, 4])
        with col_act1:
            if st.button("✏️ Edit", key=f"edit_{i}", use_container_width=True):
                st.toast(f"Fitur edit untuk {node['Node']} sedang dibangun.")
        with col_act2:
            if st.button("➕ ODC", key=f"add_{i}", use_container_width=True, help="Sisipkan ODC sebelum tiang ini"):
                st.toast("Fitur sisip ODC sedang dibangun.")

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard': show_dashboard()
elif st.session_state.page == 'Kalkulator': show_kalkulator()
elif st.session_state.page == 'AutoPlanner': show_autoplanner()
elif st.session_state.page == 'AdvancePlanner': show_advance()
