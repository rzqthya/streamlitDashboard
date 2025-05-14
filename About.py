import streamlit as st

# Menampilkan gambar di sidebar atas
st.sidebar.image("assets/Dinas_Sosial.png", width=150)

st.title("Tentang Aplikasi")
    
st.write("""
### Gambaran Aplikasi    

Aplikasi ini dirancang untuk menganalisis teks aduan masyarakat yang terdisposisi ke Dinas Sosial Jawa Timur, 
baik melalui website resmi (https://dinsos.jatimprov.go.id/), aplikasi LAPOR!, maupun website CETTAR. 
Analisis dilakukan menggunakan teknik Natural Language Processing (NLP) dan Topic Modeling untuk 
mengidentifikasi topik utama dari setiap aduan yang masuk.
Proses identifikasi topik dilakukan dengan melatih model menggunakan corpus berupa kumpulan teks aduan 
yang telah dikumpulkan dan diproses sebelumnya. Corpus ini menjadi dasar pembelajaran bagi model untuk 
mengenali pola dan mengelompokkan aduan berdasarkan kesamaan topik.

Jumlah data aduan yang diproses sejumlah **1583 Data**, dari tahun 2022-2023 yang telah melalui proses cleaning (data duplikat).
    
### Ringkasan Alur Pemrosesan Data
Untuk mengubah aduan mentah menjadi informasi topik yang dapat dianalisis, aplikasi ini melalui beberapa tahapan.

**Preprocessing Teks**

Membersihkan data dengan menghapus karakter khusus, angka, tanda baca, kata kata-kata umum yang tidak 
membawa makna signifikan (stopwords). Menormalisasi kata slang, typo, mengubah kata tidak baku menjadi baku
serta mengubahnya ke huruf kecil.
Tujuannya supaya mengurangi variasi kata yang tidak relevan serta mempermudah proses analisis selanjutnya

**Named Entity Recognition (NER) dan Latent Dirichlet Allocation (LDA)**

NER digunakan untuk memberikan kontekstual informasi pada aduan dengan menandainya dalam entitas bernama. 
**STATUS** adalah status dari bantuan atau kondisi yang dilaporkan, **PROGRAM** adalah program bantuan sosial 
yang disebutkan, **PIHAK** adalah pihak terkait yang disebutkan. Model NER dilatih dengan data yang telah dianotasi secara manual.

Sedangkan, LDA digunakan sebagai proses lanjutan untuk mengidentifikasi topik dalam teks aduan.
""")
    
st.write("""
### Pengukuran Kinerja Model

- Coherence Score : **0,7672 atau 76,72%**

(Metrik ini mengevaluasi topik dengan menilai tingkat kesamaan semantik antar kata (semantic similarity) yang terdapat dalam suatu topik. 
Semakin tinggi nilai koheren, semakin baik model dalam menghasilkan topik yang  koheren dan mudah dipahami oleh manusia)

- Perplexity Score : **-4,15** 

(Metrik ini digunakan untuk mengukur seberapa baik model memprediksi kumpulan kata dalam dokumen.
Secara umum, semakin rendah nilai perplexity, semakin baik model dalam merepresentasikan data.
Perplexity bernilai negatif karena log-likelihood digunakan dalam perhitungannya.)
""")
    
st.image("assets/Metrics Evaluation Edit.png", width=950)

st.write("""
Sehingga, jumlah topik optimal yang digunakan adalah **7 Topik**.
Pemilihan jumlah topik ini penting agar informasi yang dihasilkan tidak terlalu sedikit (kurang representatif) atau terlalu banyak (terlalu tersebar dan sulit diinterpretasikan)
""")
    
st.markdown("""
    ### Tim Pengembang
    
    [Made with ❤️ by Rizqy Athiyya Nafi'atus Sa'idah]
    
    Dengan dukungan dari:
    - Dinas Sosial Jawa Timur
    - Telkom University Surabaya
""")