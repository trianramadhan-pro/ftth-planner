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
# 2. INJEKSI CUSTOM CSS UNTUK UI BERSIH
# ---------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.stButton > button { border-radius: 8px; font-weight: 600; padding: 10px 0; }
    hr { margin: 15px 0 25px 0 !important; border-color: #eeeeee; }
    
    /* Style untuk Timeline Node di Auto Planner */
    .timeline-node {
        border-left: 4px solid #007BFF;
        padding-left: 15px;
        margin-bottom: 20px;
        position: relative;
    }
    .timeline-node::before {
        content: '';
        position: absolute;
        width: 12px; height: 12px;
        background: #007BFF;
        border-radius: 50%;
        left: -8px; top: 0;
    }
    .timeline-node.terminasi { border-left-color: #28A745; }
    .timeline-node.terminasi::before { background: #28A745; }
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
# 5. HALAMAN: DASHBOARD
# ---------------------------------------------------------
def show_dashboard():
    st.title("🌐 FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    st.markdown("### 📡 Kalkulator Redaman")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Hitung loss instan untuk Spliter Rasio maupun PLC di 1 titik ODP.</p>", unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True, type="primary"): change_page('Kalkulator'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🔗 Auto Planner (Linear)")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Otomatisasi draf topologi ODP berantai lurus dari OLT ke tiang akhir.</p>", unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True, type="primary"): change_page('AutoPlanner'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🖧 Advance Planner")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Kanvas interaktif untuk modifikasi topologi kompleks dan sisip sistem ODC.</p>", unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True, type="primary"): change_page('AdvancePlanner'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📁 Proyek Terakhir")
    st.info("Belum ada proyek yang disimpan.")

# ---------------------------------------------------------
# 6. HALAMAN: KALKULATOR RASIO (Dari Revisi Sebelumnya)
# ---------------------------------------------------------
def show_kalkulator():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("📡 Kalkulator Redaman")
    st.write("---")

    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50, format="%.2f")
    opsi_splitter = list(LOSS_RASIO.keys()) + ["--- PLC Splitter ---"] + list(LOSS_PLC.keys())
    pilihan = st.selectbox("Pilih Jenis Splitter", options=opsi_splitter, index=9)
    if pilihan == "--- PLC Splitter ---": st.warning("Pilih rasio/PLC valid."); return

    with st.expander("Redaman Jalur / Kabel (Opsional)"):
        jarak_km = st.number_input("Jarak Kabel (km)", value=0.0, step=0.1, format="%.2f")
        jml_konektor = st.number_input("Jumlah Konektor", value=0, step=1)
        jml_splicing = st.number_input("Jumlah Splicing", value=0, step=1)
    
    loss_jalur = (jarak_km * LOSS_KABEL_PER_KM) + (jml_konektor * LOSS_KONEKTOR) + (jml_splicing * LOSS_SPLICING)
    power_sebelum_split = power_in - loss_jalur
    st.write("---")
    
    if pilihan in LOSS_RASIO:
        lk, lb = LOSS_RASIO[pilihan][0], LOSS_RASIO[pilihan][1]
        ok, ob = power_sebelum_split - lk, power_sebelum_split - lb
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div style="background:#E74C3C;color:white;padding:15px;border-radius:8px;text-align:center;">Kaki Kecil ({pilihan.split(":")[0]}%)<br><b style="font-size:24px;">{ok:+.2f} dBm</b><br><small>Loss: {lk} dB</small></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="background:#3498DB;color:white;padding:15px;border-radius:8px;text-align:center;">Kaki Besar ({pilihan.split(":")[1]}%)<br><b style="font-size:24px;">{ob:+.2f} dBm</b><br><small>Loss: {lb} dB</small></div>', unsafe_allow_html=True)
    elif pilihan in LOSS_PLC:
        l_plc = LOSS_PLC[pilihan]
        o_plc = power_sebelum_split - l_plc
        st.markdown(f'<div style="background:#2ECC71;color:white;padding:15px;border-radius:8px;text-align:center;">Output PLC ({pilihan})<br><b style="font-size:24px;">{o_plc:+.2f} dBm</b><br><small>Loss: {l_plc} dB</small></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. HALAMAN: AUTO PLANNER (LOGIKA INTI)
# ---------------------------------------------------------
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Topologi')
    return output.getvalue()

def show_autoplanner():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("🔗 Auto Planner")
    st.write("---")

    # --- FORM PARAMETER ---
    with st.expander("⚙️ Parameter Jaringan", expanded=True):
        power_in = st.number_input("Power SFP/OLT (dBm)", value=7.00, step=0.50, format="%.2f")
        limit_rx = st.number_input("Target Rx Minimum ONT (dBm)", value=-25.00, step=0.50, format="%.2f")
        jarak_antar_odp = st.number_input("Jarak rata-rata antar ODP (km)", value=0.10, step=0.05, format="%.2f")
        plc_odp = st.selectbox("Spliter di dalam ODP", options=list(LOSS_PLC.keys()), index=2) # Default 1:8
        
        st.markdown("**Pengaturan Loss Lanjutan:**")
        colA, colB = st.columns(2)
        with colA: konektor_per_odp = st.number_input("Konektor/ODP (pcs)", value=2, step=1, help="Barel/Fast Connector")
        with colB: splice_per_odp = st.number_input("Splicing/ODP (pcs)", value=0, step=1)

    if st.button("🚀 Generate Topologi", use_container_width=True, type="primary"):
        st.write("---")
        
        # Inisialisasi Variabel Looping
        topologi = []
        sisa_power = power_in
        jarak_akumulasi = 0.0
        odp_ke = 1
        loss_plc_val = LOSS_PLC[plc_odp]
        loss_node_tambahan = (konektor_per_odp * LOSS_KONEKTOR) + (splice_per_odp * LOSS_SPLICING)
        
        # ALGORITMA PENCARIAN
        while True:
            # 1. Hitung redaman kabel menuju tiang ini
            loss_kabel = jarak_antar_odp * LOSS_KABEL_PER_KM
            power_sampai_tiang = sisa_power - loss_kabel - loss_node_tambahan
            jarak_akumulasi += jarak_antar_odp
            
            rasio_terpilih = None
            
            # 2. Iterasi mencari rasio yang pas (dari 01:99 ke 50:50)
            for rasio, losses in LOSS_RASIO.items():
                loss_drop = losses[0]  # Kaki Kecil untuk pelanggan
                loss_pass = losses[1]  # Kaki Besar untuk lanjut
                
                rx_sementara = power_sampai_tiang - loss_drop - loss_plc_val
                
                # Jika rx pelanggan aman, kunci rasio ini!
                if rx_sementara >= limit_rx:
                    rasio_terpilih = rasio
                    rx_final = rx_sementara
                    power_lanjut = power_sampai_tiang - loss_pass
                    break
            
            # 3. Eksekusi Hasil Pencarian
            if rasio_terpilih:
                topologi.append({
                    "Node": f"ODP {odp_ke}",
                    "Tipe": "Rasio",
                    "Rasio/PLC": rasio_terpilih,
                    "Jarak_Total": round(jarak_akumulasi, 2),
                    "Power_In_Tiang": round(power_sampai_tiang, 2),
                    "Rx_ONT": round(rx_final, 2),
                    "Power_Lanjut": round(power_lanjut, 2)
                })
                sisa_power = power_lanjut
                odp_ke += 1
            else:
                # 4. Jika semua rasio gagal, cek apakah bisa langsung Terminasi ke PLC (End Node)
                rx_terminasi = power_sampai_tiang - loss_plc_val
                if rx_terminasi >= limit_rx:
                    topologi.append({
                        "Node": f"ODP {odp_ke}",
                        "Tipe": "Terminasi",
                        "Rasio/PLC": "Direct PLC",
                        "Jarak_Total": round(jarak_akumulasi, 2),
                        "Power_In_Tiang": round(power_sampai_tiang, 2),
                        "Rx_ONT": round(rx_terminasi, 2),
                        "Power_Lanjut": None
                    })
                # Apapun hasil terminasi, looping jalur utama berhenti di sini
                break
        
        # --- RENDER HASIL VISUAL ---
        if len(topologi) == 0:
            st.error("Gagal membuat topologi. Target Rx terlalu ketat atau Power awal terlalu kecil.")
        else:
            st.success(f"✅ ESTIMASI: MAKSIMAL {len(topologi)} ODP")
            
            # Tombol Export Excel
            df_export = pd.DataFrame(topologi)
            excel_data = to_excel(df_export)
            st.download_button(label="📊 Ekspor Data ke Excel", data=excel_data, file_name='Topologi_FTTH.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
            
            st.write("")
            
            # Render Timeline
            for data in topologi:
                is_terminasi = (data['Tipe'] == 'Terminasi')
                css_class = "timeline-node terminasi" if is_terminasi else "timeline-node"
                
                st.markdown(f"""
                <div class="{css_class}">
                    <b>{data['Node']}</b> ({data['Jarak_Total']} km)<br>
                    <span style="color: gray; font-size: 13px;">Power In: {data['Power_In_Tiang']:+.2f} dBm</span><br>
                    {'<span style="color: #28A745; font-weight: bold;">🏁 TERMINASI JALUR</span><br>' if is_terminasi else f"Pasang Rasio: <b>{data['Rasio/PLC']}</b><br>"}
                    <span style="background-color: #f8f9fa; padding: 2px 5px; border-radius: 4px;">Rx di ONT: <b>{data['Rx_ONT']:+.2f} dBm</b></span><br>
                    {"" if is_terminasi else f"<span style='color: #007BFF; font-size: 13px;'>Power Lanjut: {data['Power_Lanjut']:+.2f} dBm</span>"}
                </div>
                """, unsafe_allow_html=True)
            
            st.info("Pindah ke fitur **Advance Planner** untuk memodifikasi hasil draf ini secara manual (Segera Hadir).")

# ---------------------------------------------------------
# 8. HALAMAN: ADVANCE PLANNER
# ---------------------------------------------------------
def show_advance():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("🖧 Advance Planner")
    st.write("---")
    st.warning("Kanvas visual sedang disiapkan untuk tahap pengerjaan berikutnya.")

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard': show_dashboard()
elif st.session_state.page == 'Kalkulator': show_kalkulator()
elif st.session_state.page == 'AutoPlanner': show_autoplanner()
elif st.session_state.page == 'AdvancePlanner': show_advance()
