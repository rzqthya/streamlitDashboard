import streamlit as st
import altair as alt
import pandas as pd
import pickle
from utils.analysis import get_topic_words

st.sidebar.image("assets/Dinas_Sosial.png", width=150)

st.title("🔍 Rincian Topik")
st.markdown("Berikut adalah topik-topik yang berhasil diidentifikasi oleh model.")

@st.cache_resource
def load_model():
    with open("models/lda_model.pkl", "rb") as f:
        return pickle.load(f)

lda_model = load_model()
num_words = st.slider("Jumlah Kata Teratas", 3, 15, 5)
top_words_per_topic = get_topic_words(lda_model, num_words=num_words)

topic_titles = {
    0: "Persepsi Ketimpangan Akses Bantuan",
    1: "Kendala Penyaluran Bantuan",
    2: "Kendala Status dan Validasi Kepesertaan",
    3: "Kendala Pendaftaran Bantuan",
    4: "Persepsi Kinerja Instansi",
    5: "Keterbatasan Pendataan dan Akses Informasi",
    6: "Kurangnya Pemahaman Prosedur",
}

topic_descriptions = {
    0: "Masyarakat merasa mereka seharusnya menerima bantuan karena sudah memenuhi syarat, tetapi ternyata tidak terdaftar. Mereka baru menyadari hal ini setelah melihat bantuan sudah dibagikan kepada orang lain. Situasi ini menimbulkan rasa tidak adil dalam proses distribusi bantuan.",
    1: "Masyarakat mengalami kendala data, seperti masalah NIK atau syarat yang belum lengkap. Akibatnya, pengajuan bantuan mereka terhambat. Masalah ini terjadi setelah pengajuan bantuan dilakukan, namun belum masuk tahap distribusi.",
    2: "Pengajuan bantuan sering ditolak atau gagal diverifikasi. Ada juga yang statusnya masih pending atau tidak aktif, sehingga tidak mendapat bantuan. Masalah ini muncul setelah proses pendaftaran dan saat verifikasi.",
    3: "Masyarakat mencoba mendaftar bantuan, ada juga yang ditolak meskipun sudah melengkapi syarat. Ini menunjukkan adanya hambatan di awal proses pendaftaran.",
    4: "Masyarakat mengeluhkan penolakan bantuan tanpa alasan yang jelas. Mereka merasa proses verifikasi tidak transparan dan tidak adil, padahal datanya sudah masuk atau terdaftar.",
    5: "Banyak warga kesulitan mengajukan bantuan karena kurangnya pendataan dan informasi dari instansi terkait. Beberapa juga mengalami kendala teknis, seperti akun yang diblokir.",
    6: "Warga sudah berusaha menghubungi Dinas Sosial atau Petugas terkait, tapi merasa tidak mendapatkan jawaban memuaskan. Mereka juga bingung dengan cara kerja pendaftaran.",
}

cols = st.columns(2)

for idx, (topic_name, words) in enumerate(top_words_per_topic.items()):
    word_df = pd.DataFrame(words)
    col = cols[idx % 2]
    with col:
        # Pakai idx sebagai nomor topik supaya konsisten
        top_num = idx
        
        # Tampilkan judul topik dengan nomor dan ringkasannya
        title = topic_titles.get(top_num, f"Topik {top_num}")
        st.write(f"**Topik #{top_num + 1} — {title}**")
        
        # Tampilkan chart
        chart = alt.Chart(word_df).mark_bar().encode(
            x=alt.X('word:N', title='Kata', sort=None),
            y=alt.Y('prob:Q', title='Bobot'),
            tooltip=['word', 'prob']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        
        # Tampilkan penjelasan singkat
        desc = topic_descriptions.get(top_num, "")
        if desc:
            st.markdown(f"{desc}")

st.markdown("""---""")  # garis pemisah

st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: gray;'>
        © Sistem Analisis Topik Aduan | 2025
    </div>
    """,
    unsafe_allow_html=True
)
