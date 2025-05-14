import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import tensorflow as tf  # Untuk TensorFlow
import torch  # Untuk PyTorch

# Library Needed
import pandas as pd
import numpy as np
import time

import warnings
warnings.filterwarnings('ignore')

# Visualization libraries
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", None)
# pd.set_option("display.max_row", None)

from wordcloud import WordCloud
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# ================================================================================================================

st.set_page_config(page_title="Monitoring Topik Dinas Sosial Jawa Timur", layout="wide", initial_sidebar_state="auto")


# Mendapatkan ID elemen root dari aplikasi Streamlit
root_container = st.container()

# Mengatur ukuran tampilan dengan CSS
root_container.markdown(
    f"""
    <style>
    .reportview-container .main .block-container{{
        max-width: 100%;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ================================================================================================================

# Sidebar
# st.sidebar.title("Dinas Sosial Jawa Timur")
# Menampilkan gambar dengan posisi di tengah (center)
st.sidebar.image('assets\Dinas_Sosial.png', width=80, use_container_width=False)  
st.sidebar.markdown("""
    <style>
        /* Center the logo */
        div.stSidebar > div:first-child {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        
        section[data-testid="stSidebar"] {
        background-color: #38B6FF; /* Ganti sesuai warna yang kamu mau */
        }

        /* Custom link style */
        .sidebar-menu a {
            text-decoration: none;
            color: #ffffff;
            font-size: 18px;
            padding: 8px 0;
            display: block;
            transition: 0.3s;
            font-weight: 500;
        }

        .sidebar-menu a:hover {
            color: #333333;
            font-weight: bold;
        }
    </style>

    <div class="sidebar-menu">
        <a href="#">Home</a>
        <a href="#analisis">Analisis Teks</a>
        <a href="#">Dashboard Topik</a>
    </div>
""", unsafe_allow_html=True)

# ================================================================================================================

# Menampilkan judul dengan dekorasi yang terpusat
st.markdown(
    """
    <h1 style='text-align: center; '>
        <span style='display: block;'>
            <strong>Monitoring Topik Aduan</strong>
        </span>
        <span style='display: block; font-size: medium;'>
            *Analisis Topik pada Teks Aduan Dinas Sosial Jawa Timur*
        </span>
    </h1>
    """,
    unsafe_allow_html=True
)

# ================================================================================================================

from transformers import pipeline

distilled_student_sentiment_classifier = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
    return_all_scores=True
)

# Streamlit layout
st.title("Sentiment Analysis")

# Input teks untuk prediksi
text_input = st.text_area("Masukkan teks untuk analisis sentimen:")

# Fungsi untuk melakukan prediksi sentimen
def predict_sentiment(text):
    scores = distilled_student_sentiment_classifier(text)[0]
    predicted_class = max(scores, key=lambda x: x['score'])['label']
    return predicted_class

# Melakukan prediksi dan menampilkan hasil
if st.button("Predict"):
    if text_input:
        prediction = predict_sentiment(text_input)
        st.write(f"Sentimen yang Diprediksi: {prediction}")

# ================================================================================================================

# Streamlit layout
st.title("Data File Reader.")

# Upload file Excel
uploaded_file = st.file_uploader("Upload your file here:", type=(["csv","txt","xlsx","xls"]))

st.warning("Warning: upload the data for give you the result!")
# Jika file sudah diunggah
if uploaded_file is not None:
    # Memuat file Excel menjadi DataFrame
    df = pd.read_excel(uploaded_file)
    
    # Prepocessing df-nya
    df.dropna(inplace = True) # drop saja, karena cuman satu data yang Nan.
    df.reset_index(drop = True, inplace = True)
    
    # Boolean to resize the dataframe, stored as a session state variable
    st.checkbox("Use container width", value=False, key="use_container_width")
    # Display the dataframe and allow the user to stretch the dataframe
    # across the full width of the container, based on the checkbox value
    st.write("Data from Excel file:") # Menampilkan DataFrame
    st.dataframe(df, use_container_width=st.session_state.use_container_width)

    # ================================================================================================================

    # Menghitung jumlah total program studi
    programs = df['Prodi'].unique()
    total_programs = len(programs)

    # Menghitung jumlah total saran yang diterima
    total_suggestions = len(df)

    # Menghitung jumlah total program studi
    fakultas = df['Fakultas'].unique()
    total_fakultas = len(fakultas)

    # Membagi layar menjadi dua kolom
    col1, col2, col3 = st.columns(3)

    # Menampilkan informasi jumlah program studi di kolom kiri
    with col1:
        st.metric(label="Total Program Studi:", value=total_programs, delta="🧑‍🚀")

    # Menampilkan informasi jumlah saran di kolom kanan
    with col2:
        st.metric(label="Total Saran Masuk:", value=total_suggestions, delta="🙏")

    # Menampilkan informasi jumlah saran di kolom kanan
    with col3:
        st.metric(label="Total Fakultas:", value=total_fakultas, delta="🏢")
        
    # ================================================================================================================

    # Melakukan operasi pada setiap DataFrame dalam list
    df['JAWABAN'] = df['JAWABAN'].apply(lambda x: x.lower() if isinstance(x, str) else x)

    # ================================================================================================================

    # Streamlit layout
    st.title("Select Saran Dari Mahasiswa by Index")

    # Pilihan slider untuk memilih indeks baris
    selected_row = st.slider("Select Row Index", 0, len(df) - 1, 0)

    # Menampilkan jawaban berdasarkan indeks yang dipilih
    st.write(f"Selected Row ({selected_row}):")
    st.write(df['JAWABAN'][selected_row])

    # ================================================================================================================
    # Lanjutkan Preprocessing Data
    # -------- Drop "Jawaban" tidak berguna --------
    # Daftar nilai yang ingin dihapus dari kolom 'JAWABAN' (case insensitive)
    values_to_drop = ['tidak ada', 'v', '-', '--', '---', 'belum ada', '.', 'tidak ada saran', 'belum ada saran', 'belom ada', 'n', 'tdk ada', 'nothing']
    # Mengonversi nilai-nilai dalam values_to_drop menjadi lowercase
    values_to_drop_lower = [value.lower() for value in values_to_drop]
    df = df[~df['JAWABAN'].str.lower().isin(values_to_drop_lower)]
    df.reset_index(drop = True, inplace = True)
    # -------- Menghapus angka --------
    import re
    # Fungsi untuk menghapus angka dari string
    def remove_numbers(text):
        if isinstance(text, str):  # Pastikan teks adalah string
            return re.sub(r'\d+', '', text)  # Menghapus angka dari teks
        else:
            return str(text)  # Mengonversi ke string jika tipe data lainnya
    # -------- Menghapus tanda baca --------
    # Menggunakan apply() pada kolom 'JAWABAN' untuk menghapus angka
    df['JAWABAN'] = df['JAWABAN'].apply(remove_numbers)
    # Fungsi untuk menghapus tanda baca dari string
    def remove_punctuation(text):
        return text.translate(str.maketrans("", "", string.punctuation))
    # Menggunakan apply() pada kolom 'JAWABAN' untuk menghapus tanda baca
    df['JAWABAN'] = df['JAWABAN'].apply(remove_punctuation)

    # ================================================================================================================

    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

    # -------- Mengambil stopwords dari NLTK --------
    stop_words_nltk = set(stopwords.words('indonesian'))
    stemmer = PorterStemmer()

    # -------- Mengambil stopwords dari Sastrawi --------
    stop_factory = StopWordRemoverFactory()
    stopword_remover = stop_factory.create_stop_word_remover()
    more_stopword = ['Kampus', 'surabaya', 'telkom', '...']  # Stopwords tambahan

    # -------- Menggabungkan Ssatrawi dan NLTK stopword --------
    stop_words_sastrawi = stop_factory.get_stop_words() + more_stopword
    stop_words_combined = stop_words_nltk.union(stop_words_sastrawi)
    stopword_id = list(stop_words_combined)

    # -------- Function untuk apply ke dataframe --------
    def preprocess_text(text):
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word.isalnum()]
        tokens = [word for word in tokens if word not in stopword_id]
        stemmed_words = [stemmer.stem(word) for word in tokens]
        return ' '.join(stemmed_words)

    # -------- Preprocessing ke kolom 'JAWABAN' --------
    df['JAWABAN'] = df['JAWABAN'].apply(preprocess_text)

    # ================================================================================================================

    # # -------- Mendapatkan list Prodi unik dan menambahkan opsi "Semua" -------- 
    # list_prodi = ['Semua'] + df['Prodi'].unique().tolist()

    # # -------- Tampilkan radio button untuk memilih Prodi -------- 
    # selected_prodi = st.sidebar.radio("Pilih Prodi:", list_prodi)

    # # -------- Logika untuk menangani pilihan "Semua" atau slicing DataFrame berdasarkan Prodi yang dipilih -------- 
    # if selected_prodi == 'Semua':
    #     filtered_df = df  # -------- Menampilkan keseluruhan DataFrame jika "Semua" dipilih -------- 
    # else:
    #     filtered_df = df[df['Prodi'] == selected_prodi]  # -------- Melakukan slicing DataFrame berdasarkan Prodi yang dipilih  ------

    # # -------- Tampilkan DataFrame hasil slicing atau keseluruhan DataFrame -------- 
    # st.write(f"Dataframe Berdasarkan Prodi '{selected_prodi}':")
    # st.write(filtered_df)

    # ================================================================================================================
    
    def main():
        st.title("Contoh Multi-Select dan Menampilkan DataFrame")
    
        list_prodi = df['Prodi'].unique().tolist()
    
        # Multi-select untuk memilih Prodi
        selected_prodi = st.sidebar.multiselect("Pilih Prodi:", list_prodi)
    
        # Logika untuk menampilkan keseluruhan DataFrame jika tidak ada yang dipilih
        if not selected_prodi:
            st.write("Dataframe Keseluruhan:")
            global filtered_df
            filtered_df = df.copy()
            st.write(filtered_df)
        else:
            # Slicing DataFrame berdasarkan Prodi yang dipilih
            filtered_df = df[df['Prodi'].isin(selected_prodi)]
            st.write(f"Dataframe Berdasarkan Prodi yang Dipilih:")
            st.write(filtered_df)
    
    if __name__ == "__main__":
        main()


    # -------- Menggabungkan semua teks dari kolom "JAWABAN" dalam satu string --------
    text_combined_df = ' '.join(filtered_df['JAWABAN'].astype(str).values)

    # -------- Pisahkan kembali menjadi list setiap kata yang ada --------
    text_separated_df = word_tokenize(text_combined_df)

    # -------- Cek kemunculan setiap kata yang ada --------
    kemunculan_df = nltk.FreqDist(text_separated_df)

    # -------- Mendapatkan 10 kata yang paling umum --------
    common_words = kemunculan_df.most_common(10)

    # -------- Menampilkan hasil dalam DataFrame --------
    df_common_words = pd.DataFrame(common_words, columns=['Kata', 'Kemunculan'])

    # ================================================================================================================

    # -------- Buat WordCloud untuk kemunculan kata-kata --------
    wordcloud_df = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(kemunculan_df)

    # -------- Tampilkan WordCloud di Streamlit --------
    st.title("Word Cloud untuk Kemunculan Kata-Kata")
    st.image(wordcloud_df.to_array(), use_container_width=True)

    # ================================================================================================================

    # -------- Mendapatkan 20 kata yang paling umum dan frekuensinya untuk plotting --------
    kata_df = kemunculan_df.most_common(20)
    kata_umum, frekuensi_umum = zip(*kata_df)

    st.title("Show frequently occurring words")
    # -------- Plot bar chart untuk kata-kata yang umum --------
    plt.figure(figsize=(10, 6))
    bars_umum = plt.bar(kata_umum, frekuensi_umum, color='skyblue')
    plt.xticks(rotation=90)  # -------- Mengatur rotasi label sumbu x agar lebih mudah dibaca --------
    plt.xlabel('Kata')
    plt.ylabel('Frekuensi')
    plt.title('20 Kata Paling Umum')
    plt.grid(True)

    # -------- Menambahkan label ke setiap bar pada kata-kata umum --------
    for bar, freq in zip(bars_umum, frekuensi_umum):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0, str(freq), ha='center', va='bottom')

    plt.tight_layout()

    # -------- Tampilkan grafik di Streamlit --------
    st.pyplot(plt)

    # ================================================================================================================

    # Streamlit layout
    st.title("Check Word in DataFrame")

    # Input teks dari pengguna
    input_word = st.text_input("Enter a word to search in 'JAWABAN':")

    # Memeriksa dan menampilkan kalimat yang mengandung kata tersebut
    result_sentences = df[df['JAWABAN'].str.contains(input_word, case=False)]['JAWABAN'].tolist()

    if input_word and result_sentences:
        st.write(f"Sentences containing '{input_word}':")
        for sentence in result_sentences:
            st.write(sentence)
    else:
        st.write(f"No sentences found containing '{input_word}' in 'JAWABAN'.")

    # ================================================================================================================