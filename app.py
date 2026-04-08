import streamlit as st

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
    /* Menyembunyikan menu bawaan Streamlit agar terasa seperti aplikasi native */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Styling khusus agar tombol utama terlihat seperti kotak menu aplikasi */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 0;
    }
    
    /* Memperhalus garis pemisah (divider) */
    hr {
        margin: 15px 0 25px 0 !important;
        border-color: #eeeeee;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. DATABASE KONSTANTA REDAMAN (Sesuai Tabel Referensi)
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
# 4. STATE MANAGEMENT (Navigasi Antar Halaman)
# ---------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def change_page(page_name):
    st.session_state.page = page_name

# ---------------------------------------------------------
# 5. HALAMAN: DASHBOARD (BERANDA UTAMA)
# ---------------------------------------------------------
def show_dashboard():
    st.title("🌐 FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    # KARTU 1: KALKULATOR RASIO
    st.markdown("### 📡 Kalkulator Redaman")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Hitung loss instan untuk Spliter Rasio maupun PLC di 1 titik ODP.</p>", unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True, type="primary"):
        change_page('Kalkulator')
        st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    # KARTU 2: AUTO PLANNER
    st.markdown("### 🔗 Auto Planner (Linear)")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Otomatisasi draf topologi ODP berantai lurus dari OLT ke tiang akhir.</p>", unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True, type="primary"):
        change_page('AutoPlanner')
        st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    # KARTU 3: ADVANCE PLANNER
    st.markdown("### 🖧 Advance Planner")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Kanvas interaktif untuk modifikasi topologi kompleks dan sisip sistem ODC.</p>", unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True, type="primary"):
        change_page('AdvancePlanner')
        st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # BAGIAN PROYEK TERAKHIR
    st.markdown("### 📁 Proyek Terakhir")
    st.info("Belum ada proyek yang disimpan. Data hasil export atau draf Anda akan muncul di sini nanti.")

# ---------------------------------------------------------
# 6. HALAMAN: KALKULATOR RASIO & PLC
# ---------------------------------------------------------
def show_kalkulator():
    # Header dengan tombol kembali
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali ke Dashboard"):
            change_page('Dashboard')
            st.rerun()
    with col2:
        st.subheader("📡 Kalkulator Redaman")
    
    st.write("---")

    # --- INPUT PARAMETER UTAMA ---
    st.markdown("**Parameter Utama**")
    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50, format="%.2f")
    
    # Dropdown gabungan untuk Rasio dan PLC
    opsi_splitter = list(LOSS_RASIO.keys()) + ["--- PLC Splitter ---"] + list(LOSS_PLC.keys())
    pilihan = st.selectbox("Pilih Jenis Splitter", options=opsi_splitter, index=9) # Default 10:90
    
    # Jika user hanya memilih garis pemisah
    if pilihan == "--- PLC Splitter ---":
        st.warning("Silakan pilih nilai rasio atau tipe PLC yang valid di bawahnya.")
        return

    # --- INPUT PARAMETER JALUR (OPSIONAL) ---
    with st.expander("Redaman Jalur / Kabel (Opsional)"):
        jarak_km = st.number_input("Jarak Kabel (km)", value=0.0, step=0.1, format="%.2f")
        jml_konektor = st.number_input("Jumlah Konektor/Barel", value=0, step=1)
        jml_splicing = st.number_input("Jumlah Splicing", value=0, step=1)
    
    # --- KALKULASI ---
    loss_jalur = (jarak_km * LOSS_KABEL_PER_KM) + (jml_konektor * LOSS_KONEKTOR) + (jml_splicing * LOSS_SPLICING)
    power_sebelum_split = power_in - loss_jalur

    # --- TAMPILAN HASIL ---
    st.write("---")
    st.markdown("### Hasil Output")

    # Logika jika yang dipilih adalah SPLITER RASIO
    if pilihan in LOSS_RASIO:
        loss_kecil = LOSS_RASIO[pilihan][0]
        loss_besar = LOSS_RASIO[pilihan][1]
        
        out_kecil = power_sebelum_split - loss_kecil
        out_besar = power_sebelum_split - loss_besar

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""
            <div style="background-color: #E74C3C; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                <div style="font-size: 14px;">Kaki Kecil ({pilihan.split(':')[0]}%)</div>
                <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">{out_kecil:+.2f} dBm</div>
                <div style="font-size: 12px; opacity: 0.9;">Loss: {loss_kecil} dB</div>
            </div>
            """, unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""
            <div style="background-color: #3498DB; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                <div style="font-size: 14px;">Kaki Besar ({pilihan.split(':')[1]}%)</div>
                <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">{out_besar:+.2f} dBm</div>
                <div style="font-size: 12px; opacity: 0.9;">Loss: {loss_besar} dB</div>
            </div>
            """, unsafe_allow_html=True)

    # Logika jika yang dipilih adalah SPLITER PLC
    elif pilihan in LOSS_PLC:
        loss_plc = LOSS_PLC[pilihan]
        out_plc = power_sebelum_split - loss_plc

        st.markdown(f"""
        <div style="background-color: #2ECC71; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
            <div style="font-size: 16px;">Output Semua Port ({pilihan})</div>
            <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">{out_plc:+.2f} dBm</div>
            <div style="font-size: 14px; opacity: 0.9;">Loss PLC: {loss_plc} dB</div>
        </div>
        """, unsafe_allow_html=True)

    # Keterangan tambahan jika ada loss kabel
    if loss_jalur > 0:
        st.caption(f"*Hasil di atas sudah termasuk akumulasi redaman jalur (kabel & konektor) sebesar **{loss_jalur:.2f} dB**.")

# ---------------------------------------------------------
# 7. ROUTER HALAMAN UTAMA (PENENTU TAMPILAN)
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard':
    show_dashboard()
elif st.session_state.page == 'Kalkulator':
    show_kalkulator()
elif st.session_state.page == 'AutoPlanner':
    st.title("🔗 Auto Planner")
    st.write("*(Algoritma generasi topologi sedang disiapkan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')
        st.rerun()
elif st.session_state.page == 'AdvancePlanner':
    st.title("🖧 Advance Planner")
    st.write("*(Kanvas interaktif sedang disiapkan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')
        st.rerun()
