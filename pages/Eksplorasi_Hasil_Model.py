# import streamlit as st
# import pandas as pd
# from utils.analysis import load_models, visualize_topic_distribution_from_file
# from utils.preprocess import read_text_file

# st.sidebar.image("assets/Dinas_Sosial.png", width=150)

# # """Display the Visualization page."""
# st.title("Upload Data File Aduan")
    
#     # Load models
# try:
#     with st.spinner("Memuat model..."):
#         ner_model, lda_model, dictionary = load_models()
        
#     if ner_model is None or lda_model is None or dictionary is None:
#         st.error("Gagal memuat model. Pastikan file model tersedia di direktori models/")
#         st.stop()
# except Exception as e:
#     st.error(f"Error: {str(e)}")
#     st.stop()
    
#     # File uploader
# # st.subheader("Upload File Teks")
# st.write("Upload file teks dengan setiap baris berisi satu teks untuk dianalisis.")
# uploaded_file = st.file_uploader("Pilih file teks", type=["txt"])
    
#     # Option to show preprocessing details
# show_preprocessing = st.checkbox("Tampilkan detail preprocessing", value=False)
    
# if uploaded_file is not None:
#         # Read the file
#     file_content = read_text_file(uploaded_file)
        
#     if file_content:
#         with st.spinner("Menganalisis file..."):
#             # Process the file and visualize topic distribution
#             chart, df, preproc_df = visualize_topic_distribution_from_file(file_content, ner_model, lda_model, dictionary)
                
#             if chart:
#                 st.subheader("Distribusi Topik Dominan")
#                 st.altair_chart(chart, use_container_width=True)
                    
#                     # Show the preprocessing details if checked
#                 if show_preprocessing and preproc_df is not None:
#                     st.subheader("Detail Preprocessing")
#                     for idx, row in preproc_df.iterrows():
#                         with st.expander(f"Teks #{idx+1}: {row['original_text'][:50]}..."):
#                             st.write("**Teks Asli:**")
#                             st.write(row['original_text'])
                                
#                             st.write("**Setelah Preprocessing:**")
#                             st.write(row['preprocessed_text'])
                                
#                             st.write("**Tokens:**")
#                             st.write(', '.join(row['tokens']) if row['tokens'] else "Tidak ada tokens")
                    
#                 # Show the data
#                 st.subheader("Data")
#                 st.dataframe(df)
                    
#                 # Group by topic to get count and average probability
#                 topic_stats = df.groupby('topic').agg({
#                     'probability': ['mean', 'count']
#                 }).reset_index()
#                 topic_stats.columns = ['Topik', 'Probabilitas Rata-rata', 'Jumlah']
                    
#                 st.subheader("Statistik Topik")
#                 st.dataframe(topic_stats)
#             else:
#                 st.warning("Tidak dapat mengekstrak topik dari file. Pastikan file berisi teks yang valid.")
#     else:
#         st.error("File tidak dapat dibaca atau kosong.")
    
#     # Example data
# st.subheader("Contoh Format File")
# st.code("""Saya belum menerima bantuan PKH
# Bantuan sosial tidak tepat sasaran oleh RT dan RW
# Pengajuan bantuan di dinas sosial surabaya gagal
# Bagaimana cara mendaftarkan diri untuk program bantuan pemerintah?""")

import streamlit as st
import pandas as pd
import altair as alt
import os
from utils.analysis import load_models, analyze_text, get_topic_words
from utils.preprocess import read_text_file, full_preprocessing_pipeline

st.sidebar.image("assets/Dinas_Sosial.png", width=150)

st.title("📂 Unggah File Aduan")
st.markdown("Unggah file aduan untuk melihat hasil analisis topik.")
    
# Load models
try:
    with st.spinner("Memuat model..."):
        ner_model, lda_model, dictionary, cv = load_models()
        
    if ner_model is None or lda_model is None or dictionary is None or cv is None:
        st.error("Gagal memuat model. Pastikan file model tersedia di direktori models/")
        st.stop()
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.stop()
    
# File uploader with multiple file types
uploaded_file = st.file_uploader("Pilih file", type=["txt", "xlsx", "xls"])
    
# Option to show preprocessing details
show_preprocessing = st.checkbox("Tampilkan detail preprocessing", value=False)

if uploaded_file is not None:
    # Process based on file type
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'txt':
        # Read the text file
        file_content = read_text_file(uploaded_file)
        
        if file_content:
            # Split text file into lines
            texts = file_content.strip().split('\n')
            st.success(f"Berhasil membaca {len(texts)} data dari file teks.")
        else:
            st.error("File tidak dapat dibaca atau kosong.")
            st.stop()
    
    elif file_extension in ['xlsx', 'xls']:
        try:
            # Read Excel file
            df_excel = pd.read_excel(uploaded_file)
            
            # Check for expected column format
            if 'Isi Laporan Akhir' in df_excel.columns:
                # Filter out rows with empty complaints
                df_excel = df_excel[df_excel['Isi Laporan Akhir'].notna()]
                # Convert to list of strings
                texts = df_excel['Isi Laporan Akhir'].astype(str).tolist()
                total_data = len(texts)
                st.success(f"Berhasil membaca {total_data} data dari file Excel.")
            else:
                st.error("Format Excel tidak sesuai. Pastikan terdapat kolom 'Isi Laporan Akhir'.")
                columns_str = ", ".join(df_excel.columns.tolist())
                st.info(f"Kolom yang tersedia: {columns_str}")
                st.stop()
        except Exception as e:
            st.error(f"Error membaca file Excel: {str(e)}")
            st.stop()
    
    # Process the texts
    with st.spinner("Menganalisis data..."):
        # Create a list to store results
        all_results = []
        preprocessing_details = []
        skipped_data = 0
        
        # Process each text
        for idx, text in enumerate(texts):
            if text and not text.isspace():  # Skip empty lines
                # Analyze the text
                result = analyze_text(text, ner_model, lda_model, dictionary, cv)
                
                # Apply full preprocessing pipeline for detailed preprocessing view
                preproc_result = full_preprocessing_pipeline(text)
                
                # Add preprocessing details
                preprocessing_details.append({
                    'original_text': text,
                    'preprocessed_text': preproc_result['tokens_joined'],
                    # 'tokens': preproc_result['tokens']
                })
                
                # Check if a dominant topic was found
                if result['dominant_topic']:
                    # Format entity text for display
                    entity_text = ""
                    for entity_type, entities in result['entities'].items():
                        if entities:
                            entity_text += f"{entity_type}: {', '.join(entities)}; "
                    
                    # Add to results
                    all_results.append({
                        'text': text[:50] + '...' if len(text) > 50 else text,
                        'topic': f"Topik #{result['dominant_topic'][0]+1}",
                        'probability': round(result['dominant_topic'][1], 4),
                        'entities': entity_text
                    })
                else:
                    # Data tidak memiliki topik dominan
                    skipped_data += 1
            else:
                # Data kosong atau hanya spasi
                skipped_data += 1
        
        # Create DataFrame from results
        if all_results:
            df = pd.DataFrame(all_results)
            preproc_df = pd.DataFrame(preprocessing_details)
            
            # Create two columns layout for metrics and pie chart
            col1, col2 = st.columns(2)
            
            # 1. Jumlah data yang masuk (in first column)
            with col1:
                st.subheader("Jumlah Data Yang Masuk")
                st.metric("Total Data", len(df))
                # Tampilkan informasi data yang dilewati
                if skipped_data > 0:
                    st.info(f"Catatan: {skipped_data} data dilewati karena kosong atau tidak memiliki topik dominan.")
            
            # 2. Distribusi topik dominan dengan pie chart (in second column)
            with col2:
                if not df.empty:
                    st.subheader("Identifikasi Topik")
                    
                    # Create pie chart using Altair
                    topic_counts = df['topic'].value_counts().reset_index()
                    topic_counts.columns = ['topic', 'count']
                    
                    pie_chart = alt.Chart(topic_counts).mark_arc().encode(
                        theta=alt.Theta(field="count", type="quantitative"),
                        color=alt.Color(field="topic", type="nominal", scale=alt.Scale(scheme='category10')),
                        tooltip=['topic', 'count']
                    ).properties(
                        width=300,
                        height=300
                    )
                    
                    st.altair_chart(pie_chart, use_container_width=True)
            
            # 3. Detail preprocessing sebagai tabel
            if show_preprocessing and preproc_df is not None:
                st.subheader("Detail Preprocessing")
                
                # Convert to a clean table format
                preproc_table = pd.DataFrame({
                    'Teks Asli': preproc_df['original_text'],
                    'Setelah Preprocessing': preproc_df['preprocessed_text'],
                    # 'Token': preproc_df['tokens'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
                })
                
                st.dataframe(preproc_table)
            
            # 4. Menampilkan Data dengan header yang diminta
            st.subheader("Data")
            
            # Add row numbers and rename columns
            display_df = df.copy().reset_index()
            display_df.columns = ['No', 'Teks', 'Topik', 'Probability', 'Entitas']
            display_df['No'] = display_df['No'] + 1  # Start from 1 instead of 0
            
            st.dataframe(display_df)
            
            # # 5. Top words per topic dengan bar chart
            # st.subheader("Kata Teratas per Topik")
            
            # # Get top words per topic
            # top_words_per_topic = get_topic_words(lda_model, num_words=5)
            
            # # Get unique topics in the data
            # unique_topics = df['topic'].unique()
            
            # # Get list of topic IDs that appear in data
            # topic_ids = []
            # for topic_id in range(lda_model.num_topics):
            #     topic_name = f"Topik #{topic_id+1}"
            #     if topic_name in unique_topics:
            #         topic_ids.append(topic_id)
            
            # # Create 3 columns layout
            # cols = st.columns(3)
            
            # # Display topics in the columns (round-robin style)
            # for idx, topic_id in enumerate(topic_ids):
            #     topic_name = f"Topik #{topic_id+1}"
            #     col_idx = idx % 3  # Determine which column to use (0, 1, or 2)
                
            #     words = top_words_per_topic.get(topic_name, [])
                
            #     if words:
            #         # Create DataFrame for visualization
            #         word_df = pd.DataFrame([
            #             {'word': word['word'], 'weight': word['prob']}
            #             for word in words
            #         ])
                    
            #         with cols[col_idx]:
            #             # Create bar chart
            #             topic_chart = alt.Chart(word_df).mark_bar().encode(
            #                 x=alt.X('weight:Q', title='Weight'),
            #                 y=alt.Y('word:N', title='Word', sort='-x')
            #             ).properties(
            #                 title=f'Top Words in {topic_name}',
            #                 height=200
            #             )
                        
            #             st.altair_chart(topic_chart, use_container_width=True)
        else:
            st.warning("Tidak dapat mengekstrak topik dari data. Pastikan data valid.")


st.subheader("Format File")

# Download Data
st.write("Unduh Data untuk Evaluasi")

# Path ke file contoh
example_file_path = "zData Dashboard\Data Aduan 2022-2023.xlsx"

# Cek apakah file tersedia
if os.path.exists(example_file_path):
    # Baca datanya untuk ditampilkan
    try:
        # Buka file dalam mode biner
        with open(example_file_path, "rb") as f:
            file_bytes = f.read()
            st.download_button(
                label="📥 Unduh File",
                data=file_bytes,
                file_name="data_aduan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Gagal membaca file contoh: {str(e)}")
else:
    st.warning("File contoh tidak ditemukan. Pastikan file 'data_aduan.xlsx' ada di folder 'data'.")

# Example format section
tab1, tab2 = st.tabs(["Format TXT", "Format Excel"])

with tab1:
    st.code("""Saya belum menerima bantuan PKH
Bantuan sosial tidak tepat sasaran oleh RT dan RW
Pengajuan bantuan di dinas sosial surabaya gagal
Bagaimana cara mendaftarkan diri untuk program bantuan pemerintah?""")

with tab2:
    df_example = pd.DataFrame({
        'Tracking ID': ['ID001', 'ID002', 'ID003', 'ID004'],
        'Isi Laporan Akhir': [
            'Saya belum menerima bantuan PKH',
            'Bantuan sosial tidak tepat sasaran oleh RT dan RW',
            'Pengajuan bantuan di dinas sosial surabaya gagal',
            'Bagaimana cara mendaftarkan diri untuk program bantuan pemerintah?'
        ]
    })
    st.dataframe(df_example)

