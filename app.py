import streamlit as st

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN (MOBILE-FIRST)
# ---------------------------------------------------------
st.set_page_config(
    page_title="FTTH Planner",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. INJEKSI CUSTOM CSS UNTUK UI ELEGANT & MOBILE-FRIENDLY
# ---------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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
    .card-kalkulator { border-color: #007BFF; }
    .card-auto { border-color: #28A745; }
    .card-advance { border-color: #FD7E14; }
    
    /* Styling untuk Hasil Kalkulator */
    .result-box {
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
        color: white;
    }
    .box-kecil { background-color: #E74C3C; } /* Merah/Oranye untuk Kaki Kecil */
    .box-besar { background-color: #3498DB; } /* Biru untuk Kaki Besar */
    .result-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
    .result-detail { font-size: 12px; opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. DATABASE KONSTANTA REDAMAN (Sesuai Tabel)
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

LOSS_KABEL_PER_KM = 0.3
LOSS_KONEKTOR = 0.3
LOSS_SPLICING = 0.03

# ---------------------------------------------------------
# 4. STATE MANAGEMENT
# ---------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def change_page(page_name):
    st.session_state.page = page_name

# ---------------------------------------------------------
# 5. HALAMAN: DASHBOARD
# ---------------------------------------------------------
def show_dashboard():
    st.title("⚡ FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan jaringan hari ini.")
    st.write("---")
    
    st.markdown("""
        <div class="dash-card card-kalkulator">
            <h4>🧮 Kalkulator Rasio</h4>
            <p>Hitung loss redaman instan di satu titik tiang secara akurat.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True):
        change_page('Kalkulator')

    st.markdown("""
        <div class="dash-card card-auto">
            <h4>🪄 Auto Planner (Linear)</h4>
            <p>Buat draf topologi ODP berantai secara otomatis dengan kalkulasi power maksimal.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True):
        change_page('AutoPlanner')

    st.markdown("""
        <div class="dash-card card-advance">
            <h4>🌳 Advance Planner</h4>
            <p>Kanvas visual interaktif untuk modifikasi topologi jaringan kompleks.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True):
        change_page('AdvancePlanner')

# ---------------------------------------------------------
# 6. HALAMAN: KALKULATOR RASIO
# ---------------------------------------------------------
def show_kalkulator():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali ke Dashboard"):
            change_page('Dashboard')
            st.rerun()
    with col2:
        st.subheader("🧮 Kalkulator Rasio")
    
    st.write("---")

    # --- INPUT PARAMETER UTAMA ---
    st.markdown("**Parameter Utama**")
    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50, format="%.2f")
    rasio_pilihan = st.selectbox("Pilih Rasio Spliter", options=list(LOSS_RASIO.keys()), index=9) # Default 10:90
    
    # --- INPUT PARAMETER JALUR (OPSIONAL) ---
    with st.expander("Redaman Jalur / Kabel (Opsional)"):
        jarak_km = st.number_input("Jarak Kabel (km)", value=0.0, step=0.1, format="%.2f")
        jml_konektor = st.number_input("Jumlah Konektor/Barel", value=0, step=1)
        jml_splicing = st.number_input("Jumlah Splicing", value=0, step=1)
    
    # --- KALKULASI MATEMATIKA ---
    # 1. Hitung total loss di jalur sebelum masuk spliter
    loss_jalur = (jarak_km * LOSS_KABEL_PER_KM) + (jml_konektor * LOSS_KONEKTOR) + (jml_splicing * LOSS_SPLICING)
    power_sebelum_split = power_in - loss_jalur
    
    # 2. Ambil nilai loss rasio dari database
    loss_kecil = LOSS_RASIO[rasio_pilihan][0]
    loss_besar = LOSS_RASIO[rasio_pilihan][1]
    
    # 3. Hitung output akhir
    out_kaki_kecil = power_sebelum_split - loss_kecil
    out_kaki_besar = power_sebelum_split - loss_besar

    # --- TAMPILAN HASIL (OUTPUT) ---
    st.write("---")
    st.markdown("### Hasil Redaman")
    
    # Mengambil persentase untuk label
    persen_kecil = rasio_pilihan.split(":")[0]
    persen_besar = rasio_pilihan.split(":")[1]

    # Menggunakan kolom agar sejajar di layar lebar, dan otomatis stack di HP
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.markdown(f"""
        <div class="result-box box-kecil">
            <div>Kaki Kecil ({persen_kecil}%)</div>
            <div class="result-value">{out_kaki_kecil:+.2f} dBm</div>
            <div class="result-detail">Loss Rasio: {loss_kecil} dB</div>
        </div>
        """, unsafe_allow_html=True)
        
    with res_col2:
        st.markdown(f"""
        <div class="result-box box-besar">
            <div>Kaki Besar ({persen_besar}%)</div>
            <div class="result-value">{out_kaki_besar:+.2f} dBm</div>
            <div class="result-detail">Loss Rasio: {loss_besar} dB</div>
        </div>
        """, unsafe_allow_html=True)
        
    if loss_jalur > 0:
        st.caption(f"*Catatan: Hasil di atas sudah dikurangi Loss Jalur sebesar **{loss_jalur:.2f} dB**.*")

# ---------------------------------------------------------
# ROUTER HALAMAN
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard':
    show_dashboard()
elif st.session_state.page == 'Kalkulator':
    show_kalkulator()
elif st.session_state.page == 'AutoPlanner':
    st.title("🪄 Auto Planner")
    st.write("*(Fitur 2 sedang dalam pengembangan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')
        st.rerun()
elif st.session_state.page == 'AdvancePlanner':
    st.title("🌳 Advance Planner")
    st.write("*(Fitur 3 sedang dalam pengembangan...)*")
    if st.button("⬅ Kembali ke Dashboard"):
        change_page('Dashboard')
        st.rerun()
