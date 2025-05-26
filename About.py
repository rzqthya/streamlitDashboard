# import streamlit as st

# # Menampilkan gambar di sidebar atas
# st.sidebar.image("assets/Dinas_Sosial.png", width=150)

# st.title("Tentang Aplikasi")
    
# st.write("""
# #### Gambaran Aplikasi    

# Aplikasi ini dirancang untuk menganalisis teks aduan masyarakat yang terdisposisi ke Dinas Sosial Jawa Timur, 
# baik melalui website resmi (https://dinsos.jatimprov.go.id/), aplikasi LAPOR!, maupun website CETTAR. 
# Analisis dilakukan menggunakan Topic Modeling untuk 
# mengidentifikasi topik utama dari setiap aduan yang masuk.
# Proses identifikasi topik dilakukan dengan melatih model menggunakan corpus berupa kumpulan teks aduan 
# yang telah dikumpulkan dan diproses sebelumnya. Corpus ini menjadi dasar pembelajaran bagi model untuk 
# mengenali pola dan mengelompokkan aduan berdasarkan kesamaan topik.

# Jumlah data aduan yang diproses sejumlah **1583 Data**, dari tahun 2022-2023 yang telah melalui proses pembersihan data.
# """)

# st.write("""
# #### Ringkasan Pemrosesan Data
# Aduan berupa data teks mentah akan diolah menjadi informasi topik yang dengan alur seperti berikut.
# """)

# st.image("assets/Flow.jpg", width=750)

# # st.write("""
# # ### Ringkasan Pemrosesan Data
# # Untuk mengubah aduan mentah menjadi informasi topik yang dapat dianalisis, aplikasi ini melalui beberapa tahapan.

# # **Preprocessing Teks**

# # Membersihkan data dengan menghapus karakter khusus, angka, tanda baca, kata kata-kata umum yang tidak 
# # membawa makna signifikan (stopwords). Menormalisasi kata slang, typo, mengubah kata tidak baku menjadi baku
# # serta mengubahnya ke huruf kecil.
# # Tujuannya supaya mengurangi variasi kata yang tidak relevan serta mempermudah proses analisis selanjutnya

# # **Named Entity Recognition (NER) dan Latent Dirichlet Allocation (LDA)**

# # NER digunakan untuk memberikan kontekstual informasi pada aduan dengan menandainya dalam entitas bernama. 
# # **STATUS** adalah status dari bantuan atau kondisi yang dilaporkan, **PROGRAM** adalah program bantuan sosial 
# # yang disebutkan, **PIHAK** adalah pihak terkait yang disebutkan. Model NER dilatih dengan data yang telah dianotasi secara manual.

# # Semakin tinggi nilai koheren, semakin baik model dalam menghasilkan topik yang koheren dan mudah dipahami oleh manusia
# # Secara umum, semakin rendah nilai perplexity, semakin baik model dalam merepresentasikan data.
# # Perplexity bernilai negatif karena log-likelihood digunakan dalam perhitungannya.

# # Sedangkan, LDA digunakan sebagai proses lanjutan untuk mengidentifikasi topik dalam teks aduan.
# # """)
    
# st.write("""
# #### Pengukuran Kinerja Model

# - Coherence Score : **0,7672 atau 76,72%**

# Metrik ini mengevaluasi topik dengan menilai tingkat kesamaan semantik antar kata (semantic similarity) yang terdapat dalam suatu topik.

# - Perplexity Score : **-4,15** 

# Metrik ini mengukur seberapa baik model memprediksi distribusi kata baru dari aduan.
# """)
    
# st.image("assets/Metrics Evaluation Edit.png", width=950)

# st.write("""
# Sehingga, jumlah topik optimal yang digunakan adalah **7 Topik**.
# Pemilihan jumlah topik ini penting agar informasi yang dihasilkan tidak terlalu sedikit (kurang representatif) atau terlalu banyak (terlalu tersebar dan sulit diinterpretasikan)
# """)
    
# st.markdown("""
#     #### Tim Pengembang
    
#     [Made with ❤️ by Rizqy Athiyya Nafi'atus Sa'idah]
    
#     Dengan dukungan dari:
#     - Dinas Sosial Jawa Timur
#     - Telkom University Surabaya
# """)

import streamlit as st

# Sidebar logo
st.sidebar.image("assets/Dinas_Sosial.png", width=150)

st.title("📘 Tentang Aplikasi")
st.markdown("Pelajari fungsi dan tujuan aplikasi ini secara singkat.")

# GAMBARA UMUM APLIKASI
st.write("""
#### Gambaran Umum Aplikasi

Aplikasi ini dibuat untuk membantu menganalisis isi utama dari aduan masyarakat yang masuk ke Dinas Sosial Jawa Timur, tanpa perlu membaca satu per satu.
Sumber data bisa berasal dari Website resmi Dinas Sosial, Aplikasi LAPOR!, dan website CETTAR.
Tujuan dari aplikasi ini adalah untuk mengidentifikasi topik utama dari setiap aduan yang masuk, sehingga bisa lebih cepat dan sistematis dalam memahami serta menanggapi kebutuhan masyarakat.
""")

# MENU PENJELASAN
st.write("""
#### Penjelasan Menu Aplikasi

Berikut penjelasan fungsi dari setiap menu:

- **Tentang Aplikasi**: Menjelaskan tujuan dan cara kerja aplikasi ini
- **Analisis Teks**: Untuk mengecek topik dari satu aduan secara langsung, cukup dengan memasukkan teks aduan.
- **Eksplorasi Hasil Model**: Untuk melihat ringkasan topik yang berhasil ditemukan dari semua aduan yang sudah dianalisis
- **Persebaran Topik**: Untuk melihat kata-kata penting dalam setiap topik, sehingga memudahkan memahami topik aduan secara umum.
""")

# PROSES DATA
st.write("""
#### Ringkasan Pemrosesan Data

Proses identifikasi topik dilakukan dengan melatih model menggunakan **corpus**, yaitu kumpulan teks aduan yang telah dikumpulkan dan diproses sebelumnya.
Corpus ini membantu model untuk belajar mengenali pola-pola kata dalam aduan, sehingga bisa mengelompokkan aduan yang memiliki kesamaan topik.
Jumlah data aduan yang dianalisis sebanyak **1583 aduan**, dari tahun **2022–2023**, yang sudah melalui proses pembersihan teks terlebih dahulu.
""")

st.image("assets/Flow.jpg", width=750)

# KINERJA MODEL
st.write("""
#### Pengukuran Kinerja Model
Kami menggunakan metode pembelajaran mesin (machine learning) untuk melatih model analisis topik. Hasil pelatihan model ini cukup baik.

Model berhasil mencapai nilai **Nilai Koherensi sebesar 76,72%**, yang menunjukkan bahwa topik-topik yang dihasilkan cukup relevan dan mudah dipahami. Selain itu, model juga memperoleh **nilai Perplexity sebesar -4,15**, yang berarti model cukup baik dalam memahami pola kata-kata dalam aduan.

Dengan hasil ini, sistem mampu mengenali dan mengelompokkan 7 topik utama dari ribuan aduan yang telah dianalisis.
""")

st.image("assets/Metrics Evaluation Edit.png", width=950)

# TIM PENGEMBANG
st.write("""
#### Tim Pengembang

[by Rizqy Athiyya Nafi'atus Sa'idah]  
Dengan dukungan dari:
- Dinas Sosial Jawa Timur  
- Telkom University Surabaya
""")
