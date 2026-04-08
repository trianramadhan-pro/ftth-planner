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
    
    /* Tombol Utama */
    div.stButton > button { border-radius: 8px; font-weight: 600; padding: 10px 0; }
    hr { margin: 15px 0 25px 0 !important; border-color: #eeeeee; }
    
    /* Auto Planner Timeline */
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

    /* Box Hasil Rx Auto Planner (Kontras Hitam) */
    .rx-box {
        padding: 4px 10px;
        border-radius: 5px;
        font-weight: bold;
        color: #000000 !important; 
        display: inline-block;
        margin-top: 4px;
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
# 4. STATE MANAGEMENT (MEMORI APLIKASI)
# ---------------------------------------------------------
if 'page' not in st.session_state: 
    st.session_state.page = 'Dashboard'
if 'draf_topologi' not in st.session_state: 
    st.session_state.draf_topologi = []
if 'global_params' not in st.session_state:
    st.session_state.global_params = {}
if 'saved_projects' not in st.session_state:
    st.session_state.saved_projects = [] # Array untuk menyimpan banyak proyek

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
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Hitung loss instan untuk Spliter Rasio maupun PLC di 1 titik ODP.</p>", unsafe_allow_html=True)
    if st.button("Buka Kalkulator", key="btn_kalkulator", use_container_width=True, type="primary"): 
        change_page('Kalkulator'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🔗 Auto Planner (Linear)")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Otomatisasi draf topologi ODP berantai lurus dari OLT ke tiang akhir.</p>", unsafe_allow_html=True)
    if st.button("Buka Auto Planner", key="btn_auto", use_container_width=True, type="primary"): 
        change_page('AutoPlanner'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### 🖧 Advance Planner")
    st.markdown("<p style='color: gray; font-size: 14px; margin-top: -10px;'>Kanvas interaktif untuk modifikasi topologi kompleks (Segera Hadir).</p>", unsafe_allow_html=True)
    if st.button("Buka Advance Planner", key="btn_advance", use_container_width=True, type="primary"): 
        change_page('AdvancePlanner'); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Render Daftar Proyek Tersimpan
    st.markdown("### 📁 Proyek Terakhir")
    if len(st.session_state.saved_projects) > 0:
        # Menampilkan dari yang terbaru (reverse)
        for proj in reversed(st.session_state.saved_projects):
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #28A745; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <strong style="font-size:16px;">{proj['nama']}</strong><br>
                <span style="font-size: 13px; color: gray;">Total {proj['nodes']} ODP | Power OLT: {proj['power']} dBm</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Belum ada proyek yang disimpan. Gunakan Auto Planner untuk membuat proyek baru.")

# ---------------------------------------------------------
# 6. HALAMAN: KALKULATOR REDAMAN
# ---------------------------------------------------------
def show_kalkulator():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali"): change_page('Dashboard'); st.rerun()
    with col2:
        st.subheader("📡 Kalkulator Redaman")
    st.write("---")

    with st.expander("📊 Lihat Tabel Referensi Redaman"):
        tb1, tb2 = st.columns(2)
        with tb1:
            st.markdown("**Spliter Rasio**")
            df_r = pd.DataFrame([{"Rasio": k, "Drop": v[0], "Pass": v[1]} for k, v in LOSS_RASIO.items()])
            st.dataframe(df_r, hide_index=True, use_container_width=True)
        with tb2:
            st.markdown("**Spliter PLC**")
            df_p = pd.DataFrame([{"PLC": k, "Loss (dB)": v} for k, v in LOSS_PLC.items()])
            st.dataframe(df_p, hide_index=True, use_container_width=True)
            st.markdown("**Lainnya:**")
            st.write(f"• Kabel: {LOSS_KABEL_PER_KM} dB/km<br>• Konektor: {LOSS_KONEKTOR} dB", unsafe_allow_html=True)

    st.markdown("**Parameter Utama**")
    power_in = st.number_input("Power Input (dBm)", value=7.00, step=0.50, format="%.2f")
    opsi_splitter = list(LOSS_RASIO.keys()) + ["--- PLC Splitter ---"] + list(LOSS_PLC.keys())
    pilihan = st.selectbox("Pilih Jenis Splitter", options=opsi_splitter, index=9)
    
    if pilihan == "--- PLC Splitter ---": 
        return

    with st.expander("Redaman Jalur / Kabel (Opsional)"):
        jarak_km = st.number_input("Jarak Kabel (km)", value=0.0, step=0.1, format="%.2f")
        jml_konektor = st.number_input("Jumlah Konektor/Barel", value=0, step=1)
        jml_splicing = st.number_input("Jumlah Splicing", value=0, step=1)
    
    loss_jalur = (jarak_km * LOSS_KABEL_PER_KM) + (jml_konektor * LOSS_KONEKTOR) + (jml_splicing * LOSS_SPLICING)
    power_sebelum_split = power_in - loss_jalur

    st.write("---")
    st.markdown("### Hasil Output")

    if pilihan in LOSS_RASIO:
        loss_kecil = LOSS_RASIO[pilihan][0]
        loss_besar = LOSS_RASIO[pilihan][1]
        out_kecil = power_sebelum_split - loss_kecil
        out_besar = power_sebelum_split - loss_besar

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""
            <div style="background-color: #E74C3C; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 5px;">
                <div style="font-size: 13px;">Kaki Kecil ({pilihan.split(':')[0]}%)</div>
                <div style="font-size: 18px; font-weight: bold; margin: 5px 0;">{out_kecil:+.2f} dBm</div>
                <div style="font-size: 11px; opacity: 0.9;">Loss: {loss_kecil} dB</div>
            </div>
            """, unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""
            <div style="background-color: #3498DB; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 5px;">
                <div style="font-size: 13px;">Kaki Besar ({pilihan.split(':')[1]}%)</div>
                <div style="font-size: 18px; font-weight: bold; margin: 5px 0;">{out_besar:+.2f} dBm</div>
                <div style="font-size: 11px; opacity: 0.9;">Loss: {loss_besar} dB</div>
            </div>
            """, unsafe_allow_html=True)

    elif pilihan in LOSS_PLC:
        loss_plc = LOSS_PLC[pilihan]
        out_plc = power_sebelum_split - loss_plc
        st.markdown(f"""
        <div style="background-color: #2ECC71; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 5px;">
            <div style="font-size: 14px;">Output Semua Port ({pilihan})</div>
            <div style="font-size: 22px; font-weight: bold; margin: 5px 0;">{out_plc:+.2f} dBm</div>
            <div style="font-size: 12px; opacity: 0.9;">Loss PLC: {loss_plc} dB</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. HALAMAN: AUTO PLANNER (Dengan Fitur Save Project)
# ---------------------------------------------------------
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def show_autoplanner():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅", help="Kembali"): change_page('Dashboard'); st.rerun()
    with col2:
        st.subheader("🔗 Auto Planner")
    
    with st.expander("⚙️ Parameter Jaringan", expanded=True):
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
                    "Node": f"ODP {idx}", "Tipe": "Rasio", "Rasio": best_r, 
                    "Drop_Kecil": round(drop_f,2), "Jarak": round(total_d,2), 
                    "Rx": round(rx_f,2), "Next": round(p_next,2)
                })
                curr_p, idx = p_next, idx + 1
            else:
                rx_t = p_tiang - l_plc
                if rx_t >= l_rx:
                    topologi.append({
                        "Node": f"ODP {idx}", "Tipe": "Terminasi", "Rasio": "Direct PLC", 
                        "Drop_Kecil": round(p_tiang,2), "Jarak": round(total_d,2), 
                        "Rx": round(rx_t,2), "Next": None
                    })
                break

        if not topologi:
            st.error("Power tidak cukup untuk ditarik ke ODP pertama. Coba naikkan Power OLT atau turunkan limit Rx.")
        else:
            st.success(f"✅ ESTIMASI: MAKSIMAL {len(topologi)} ODP")
            
            # --- SIMPAN DRAF KE SESSION STATE ---
            st.session_state.draf_topologi = topologi
            st.session_state.global_params = {"p_in": p_in, "l_rx": l_rx, "l_plc": l_plc}

            # --- MANAJEMEN TOMBOL (EXPORT, SIMPAN, EDIT) ---
            st.markdown("**Simpan / Ekspor Hasil:**")
            nama_proyek = st.text_input("Nama Proyek:", placeholder="Contoh: Jalur Mawar (Arah Utara)")
            
            # Baris 1: Export dan Simpan berdampingan
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                df_export = pd.DataFrame(topologi).rename(columns={'Drop_Kecil': 'Input PLC (dBm)'})
                st.download_button("📊 Export Excel", data=to_excel(df_export), file_name="ftth_plan.xlsx", use_container_width=True)
            with btn_col2:
                if st.button("💾 Simpan Proyek", use_container_width=True):
                    if nama_proyek.strip() == "":
                        st.warning("⚠️ Nama proyek tidak boleh kosong!")
                    else:
                        st.session_state.saved_projects.append({
                            "nama": nama_proyek,
                            "nodes": len(topologi),
                            "power": p_in,
                            "data": topologi
                        })
                        st.success(f"Proyek '{nama_proyek}' disimpan ke Dashboard!")

            # Baris 2: Tombol Edit Advance Planner
            if st.button("✏️ Edit di Advance Planner", use_container_width=True, type="primary"):
                change_page('AdvancePlanner')
                st.rerun()

            st.write("---")
            
            # --- RENDER TIMELINE HASIL ---
            for d in topologi:
                is_t = d['Tipe'] == "Terminasi"
                cls = "timeline-node terminasi" if is_t else "timeline-node"
                rx_cls = "rx-aman" if d['Rx'] >= l_rx else "rx-bahaya"
                
                info_rasio = f'🏁 <b style="color:#28A745;">TERMINASI JALUR</b><br>' if is_t else f'Rasio: <b>{d["Rasio"]}</b><br>'
                info_kaki_kecil = f'<span style="font-size: 13px; color: gray;">Out Kaki Kecil: {d["Drop_Kecil"]:+.2f} dBm</span><br>'
                
                # MEMASTIKAN POWER LANJUT TAMPIL DENGAN JELAS
                info_lanjut = f'<br><span style="color:#007BFF; font-weight:bold; font-size:14px;">⚡ Power Lanjut: {d["Next"]:+.2f} dBm</span>' if not is_t else ''

                st.markdown(f"""
                <div class="{cls}">
                    <b>{d['Node']}</b> ({d['Jarak']} km)<br>
                    {info_rasio}
                    {info_kaki_kecil}
                    <div class="rx-box {rx_cls}">Rx ONT: {d['Rx']:+.2f} dBm</div>
                    {info_lanjut}
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. HALAMAN: ADVANCE PLANNER (PROGRES)
# ---------------------------------------------------------
def show_advance():
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅"): change_page('Dashboard'); st.rerun()
    with col2: st.subheader("🖧 Advance Planner")
    st.write("---")
    
    draf = st.session_state.draf_topologi
    if not draf:
        st.info("Buat draf otomatis di menu **Auto Planner** terlebih dahulu, lalu klik 'Edit di Advance Planner'.")
        return

    p_in = st.session_state.global_params.get("p_in", 0)
    st.markdown(f"**Sumber OLT:** `{p_in:+.2f} dBm`")
    st.write("Daftar Node (Mode Edit sedang dibangun):")
    
    for i, node in enumerate(draf):
        status_warna = "green" if node['Rx'] >= st.session_state.global_params.get("l_rx", -25) else "red"
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #6c757d;">
            <strong>{node['Node']}</strong> <span style="color:gray; font-size:12px;">(Jarak: {node['Jarak']} km)</span><br>
            <span style="font-size: 14px;">Spliter: {node['Rasio']}</span><br>
            <span style="color:{status_warna}; font-weight:bold; font-size: 14px;">Rx: {node['Rx']:+.2f} dBm</span>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
if st.session_state.page == 'Dashboard': show_dashboard()
elif st.session_state.page == 'Kalkulator': show_kalkulator()
elif st.session_state.page == 'AutoPlanner': show_autoplanner()
elif st.session_state.page == 'AdvancePlanner': show_advance()
