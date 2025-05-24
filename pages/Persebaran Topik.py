import streamlit as st
import altair as alt
import pandas as pd
import pickle
from utils.analysis import get_topic_words

st.sidebar.image("assets/Dinas_Sosial.png", width=150)
st.title("🔍 Top Words per Topik")

@st.cache_resource
def load_model():
    with open("models/lda_model.pkl", "rb") as f:
        return pickle.load(f)

lda_model = load_model()
num_words = st.slider("Jumlah Kata Teratas", 3, 15, 5)
top_words_per_topic = get_topic_words(lda_model, num_words=num_words)

topic_titles = {
    0: "Ketimpangan dalam Akses Bantuan",
    1: "Hambatan dalam Penyaluran Bantuan",
    2: "Masalah Validasi dan Status Kepesertaan",
    3: "Kendala Proses Pendaftaran",
    4: "Ketidakpuasan terhadap Kinerja Instansi",
    5: "Keterbatasan Pendataan dan Akses Informasi",
    6: "Respons Pengawasan dan Kebingungan Sistem",
}

topic_descriptions = {
    0: "Topik ini membahas masalah ketimpangan distribusi bantuan sosial yang dialami masyarakat...",
    1: "Hambatan yang ditemui selama proses penyaluran bantuan, termasuk birokrasi dan kendala teknis...",
    2: "Validasi data dan status kepesertaan menjadi masalah utama yang menyebabkan ketidakjelasan bantuan...",
    3: "Proses pendaftaran yang rumit dan kurang sosialisasi menyebabkan banyak warga kesulitan...",
    4: "Ketidakpuasan masyarakat terhadap kinerja instansi yang dianggap lambat dan kurang transparan...",
    5: "Terbatasnya pendataan dan akses informasi membuat banyak warga tidak mendapatkan bantuan tepat waktu...",
    6: "Pengawasan yang tidak konsisten dan kebingungan sistem membuat proses distribusi menjadi tidak efektif...",
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
