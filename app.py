import streamlit as st

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN (MOBILE-FIRST)
# ---------------------------------------------------------
st.set_page_config(
    page_title="FTTH Planner",
    page_icon="⚡",
    layout="centered", # Menggunakan centered agar di desktop pun menyerupai tampilan mobile
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS UNTUK UI ELEGANT & MOBILE-FRIENDLY
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Menyembunyikan menu bawaan Streamlit agar lebih rapi */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Styling untuk Kartu Dashboard (Quick Access Cards) */
    .dash-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid;
    }
    .dash-card h4 { margin-top: 0; padding-top: 0; color: #333333; }
    .dash-card p { color: #666666; font-size: 14px; }
    
    /* Warna aksen tiap kartu */
    .card-kalkulator { border-color: #007BFF; }
    .card-auto { border-color: #28A745; }
    .card-advance { border-color: #FD7E14; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. DATABASE KONSTANTA REDAMAN (Sesuai Tabel)
# ---------------------------------------------------------
# Dictionary Rasio (Key: Rasio, Value: [Loss % Kecil, Loss % Besar])
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

# Dictionary PLC
LOSS_PLC = {
    "1:2": 3.25, "1:4": 7.00, "1:8": 10.00, 
    "1:16": 13.50, "1:32": 17.00, "1:64": 20.00
}

# Konstanta Fisik Lainnya
LOSS_KABEL_PER_KM = 0.3
LOSS_KONEKTOR = 0.3
LOSS_SPLICING = 0.03

# ---------------------------------------------------------
# 4. STATE MANAGEMENT (Navigasi Halaman)
# ---------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def change_page(page_name):
    st.session_state.page = page_name

# ---------------------------------------------------------
# 5. TAMPILAN DASHBOARD
# ---------------------------------------------------------
def show_dashboard():
    st.title("⚡ FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    # Render Kartu Kalkulator Rasio
    st.markdown("""
        <div class="dash-card card-kalkulator">
            <h4>🧮 Kalkulator Rasio</h4>
            <p>Hitung loss redaman instan di satu titik tiang secara akurat.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True):
        change_page('Kalkulator')

    # Render Kartu Auto Planner
    st.markdown("""
        <div class="dash-card card-auto">
            <h4>🪄 Auto Planner (Linear)</h4>
            <p>Buat draf topologi ODP berantai secara otomatis dengan kalkulasi power maksimal.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True):
        change_page('AutoPlanner')

    # Render Kartu Advance Planner
    st.markdown("""
        <div class="dash-card card-advance">
            <h4>🌳 Advance Planner</h4>
            <p>Kanvas visual interaktif untuk modifikasi topologi jaringan kompleks.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True):
        change_page('AdvancePlanner')

    st.write("---")
    st.subheader("📁 Proyek Terakhir")
    st.info("Fitur penyimpanan proyek akan diintegrasikan pada tahap akhir.")

# ---------------------------------------------------------
# 6. ROUTER HALAMAN UTAMA
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard':
    show_dashboard()
elif st.session_state.page == 'Kalkulator':
    st.title("🧮 Kalkulator Rasio")
    st.write("*(Fitur 1 sedang dalam pengembangan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')
elif st.session_state.page == 'AutoPlanner':
    st.title("🪄 Auto Planner")
    st.write("*(Fitur 2 sedang dalam pengembangan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')
elif st.session_state.page == 'AdvancePlanner':
    st.title("🌳 Advance Planner")
    st.write("*(Fitur 3 sedang dalam pengembangan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')