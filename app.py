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
# 2. INJEKSI CUSTOM CSS UNTUK CLICKABLE CARDS
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Menyembunyikan menu bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* TRIK CSS: 
       Mengubah semua tombol utama Streamlit menjadi bentuk Kartu/Bar 
       yang lebar, rapi, dan responsif saat diketuk.
    */
    div.stButton > button {
        width: 100%;
        height: auto;
        padding: 20px 15px;
        border-radius: 12px;
        text-align: left;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 6px solid #007BFF; /* Aksen warna tepi kiri */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        transition: all 0.2s ease-in-out;
    }
    
    /* Efek saat tombol ditekan/disentuh */
    div.stButton > button:hover, div.stButton > button:active {
        border-left: 6px solid #0056b3;
        background-color: #f8f9fa;
        transform: scale(0.98);
    }
    
    /* Memperbesar ukuran teks ikon dan judul di dalam tombol */
    div.stButton > button p {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #333333;
        margin-bottom: 5px;
    }
    
    /* Deskripsi proyek di bawah layar */
    .proyek-item {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #eeeeee;
    }
    </style>
""", unsafe_allow_html=True)

# ... [BAGIAN 3 & 4 (KONSTANTA DAN STATE) TETAP SAMA SEPERTI SEBELUMNYA] ...

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

def change_page(page_name):
    st.session_state.page = page_name

# ---------------------------------------------------------
# 5. HALAMAN: DASHBOARD (REVISI CLICKABLE BAR)
# ---------------------------------------------------------
def show_dashboard():
    st.title("🌐 FTTH Planner")
    st.markdown("Halo, **Engineer!**\nMari rencanakan *loss budget* jaringan hari ini.")
    st.write("---")
    
    # 1. Bar Kalkulator Rasio
    # Karena tombol Streamlit tidak bisa menerima multiline secara native dengan rapi,
    # kita gunakan format teks yang lugas dan tebal.
    if st.button("📡 Kalkulator Rasio \n\nHitung loss redaman instan di 1 titik ODP.", key="btn_kalkulator", use_container_width=True):
        change_page('Kalkulator')

    st.write("") # Spasi antar kartu

    # 2. Bar Auto Planner
    if st.button("🔗 Auto Planner (Linear) \n\nBuat draf topologi ODP berantai otomatis.", key="btn_auto", use_container_width=True):
        change_page('AutoPlanner')

    st.write("") # Spasi antar kartu

    # 3. Bar Advance Planner
    if st.button("🖧 Advance Planner \n\nKanvas visual untuk modifikasi ODC/ODP kompleks.", key="btn_advance", use_container_width=True):
        change_page('AdvancePlanner')

    st.write("---")
    
    # Bagian Proyek Terakhir (Tampilan Statis untuk Konsep)
    st.markdown("### 📁 Proyek Terakhir")
    st.markdown("""
        <div class="proyek-item">
            <strong>🔗 Jalur Distribusi Mawar</strong><br>
            <span style="color: gray; font-size: 14px;">Diperbarui: Hari ini | Status: <span style="color: green;">Aman</span></span>
        </div>
        <div class="proyek-item">
            <strong>🖧 Topologi Cluster Melati</strong><br>
            <span style="color: gray; font-size: 14px;">Diperbarui: Kemarin | Status: <span style="color: orange;">Warning</span></span>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# ROUTER SEMENTARA (HANYA UNTUK TESTING DASHBOARD)
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard':
    show_dashboard()
elif st.session_state.page == 'Kalkulator':
    st.success("Berhasil masuk ke halaman Kalkulator!")
    if st.button("⬅ Kembali"): change_page('Dashboard'); st.rerun()
elif st.session_state.page == 'AutoPlanner':
    st.success("Berhasil masuk ke halaman Auto Planner!")
    if st.button("⬅ Kembali"): change_page('Dashboard'); st.rerun()
elif st.session_state.page == 'AdvancePlanner':
    st.success("Berhasil masuk ke halaman Advance Planner!")
    if st.button("⬅ Kembali"): change_page('Dashboard'); st.rerun()
