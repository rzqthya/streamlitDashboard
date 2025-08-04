import streamlit as st
import ntlk
from utils.analysis import load_models, analyze_text, visualize_topic_distribution, get_topic_words, visualize_entities

st.sidebar.image("assets/ComplainInsight.png", width=150)

# """Display the Text Analysis page."""
st.title("📝 Analisis Topik dari Aduan")
st.markdown("**Panduan**: Silakan masukkan teks aduan untuk dianalisis topiknya")
    
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
    
# Text input area
text_input = st.text_area("Input Teks", height=150, placeholder="Masukkan teks...")
    
if st.button("Analisis", type="primary"):
    if text_input:
        try:
            with st.spinner("Menganalisis teks..."):
                # Analyze the input text
                result = analyze_text(text_input, ner_model, lda_model, dictionary, cv)
                    
                # Display results
                st.write("**Hasil Analisis**")
                    
                # Display entities
                st.write("**Informasi Kata Kunci yang Di ekstrak berupa Entitas**")
                entities = result['entities']
                    
                # Check if any entities were found
                if any(entities.values()):
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            st.write(f"{entity_type}: {', '.join(entity_list)}")
                else:
                    st.info("Tidak ada informasi yang terdeteksi relevan.")
                    
                    # Display topic distribution
                st.write("**Hasil Analisis Topik**")
                if result['topics']:
                        
                        # Dictionary penjelasan topik
                        topic_descriptions = {
                            0: "Persepsi Ketimpangan Akses Bantuan",
                            1: "Kendala Penyaluran Bantuan",
                            2: "Kendala Status dan Validasi Kepesertaan",
                            3: "Kendala Pendaftaran Bantuan",
                            4: "Persepsi Kinerja Instansi",
                            5: "Keterbatasan Pendataan dan Akses Informasi",
                            6: "Kurangnya Pemahaman Prosedur",
                        }

                        # Display dominant topic
                        if result['dominant_topic']:
                            topic_idx, topic_prob = result['dominant_topic']
                            st.info(f"Aduan tersebut masuk dalam: Topik {topic_idx + 1} (dengan probabilitas: {topic_prob * 100:.2f}%). Membicarakan tentang topik : {topic_descriptions[topic_idx]}")

                        else:
                            st.info("Tidak dapat membuat visualisasi topik.")
                else:
                    st.info("Tidak dapat menentukan distribusi topik. Mungkin tidak ada entitas yang relevan terdeteksi.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat menganalisis teks: {str(e)}")
            st.info("Silakan coba lagi dengan teks yang berbeda atau hubungi administrator sistem.")
    else:
        st.warning("Silakan masukkan teks untuk dianalisis.")

st.markdown("""---""")  # garis pemisah

st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: gray;'>
        © Sistem Analisis Topik Aduan | 2025
    </div>
    """,
    unsafe_allow_html=True
)

# import streamlit as st
# from utils.analysis import load_models, analyze_text, visualize_topic_distribution, get_topic_words, visualize_entities

# def show():
#     """Display the Text Analysis page."""
#     st.title("Analisis Teks")

#     # Load models
#     try:
#         with st.spinner("Memuat model..."):
#             ner_model, lda_model, dictionary, selected_topics = load_models()

#         if ner_model is None or lda_model is None or dictionary is None:
#             st.error("Gagal memuat model. Pastikan file model tersedia di direktori models/")
#             return
#     except Exception as e:
#         st.error(f"Error: {str(e)}")
#         return

#     # Display information about the model
#     # with st.expander("Informasi Model"):
#     #     st.write("Model ini menggunakan 7 topik tertentu (Topik 1-7) dari total 30 topik yang dilatih.")
#     #     st.write(f"Topik yang dianalisis: {', '.join([f'Topik #{t+1}' for t in selected_topics])}")

#     # Text input area
#     st.subheader("Masukkan Teks untuk Dianalisis")
#     text_input = st.text_area("Input Teks", height=150, placeholder="Contoh: Saya belum menerima bantuan PKH, bagaimana cara mendaftar?")

#     if st.button("Analisis", type="primary"):
#         if text_input:
#             try:
#                 with st.spinner("Menganalisis teks..."):
#                     # Analyze the input text with selected topics
#                     result = analyze_text(text_input, ner_model, lda_model, dictionary, selected_topics)

#                     # Display results
#                     st.subheader("Hasil Analisis")

#                     # Show preprocessing results
#                     with st.expander("Lihat Detail Preprocessing"):
#                         st.write("**Teks Asli:**")
#                         st.write(text_input)

#                         st.write("**Teks Setelah Preprocessing:**")
#                         st.write(result['preprocessed_text'])

#                         st.write("**Tokens Setelah Stopwords Removal:**")
#                         if result['tokens']:
#                             st.write(', '.join(result['tokens']))
#                         else:
#                             st.write("Tidak ada token yang tersisa setelah preprocessing.")

#                     # Display entities
#                     st.write("### Entitas Terdeteksi")
#                     entities = result['entities']

#                     # Check if any entities were found
#                     if any(entities.values()):
#                         for entity_type, entity_list in entities.items():
#                             if entity_list:
#                                 st.write(f"**{entity_type}**: {', '.join(entity_list)}")
#                     else:
#                         st.info("Tidak ada entitas yang terdeteksi.")

#                     # Display topic distribution
#                     st.write("### Distribusi Topik")
#                     if result['topics']:
#                         chart = visualize_topic_distribution(result['topics'])
#                         if chart:
#                             st.altair_chart(chart, use_container_width=True)

#                             # Display dominant topic
#                             if result['dominant_topic']:
#                                 topic_idx, topic_prob = result['dominant_topic']
#                                 st.write(f"**Topik Dominan**: Topik #{topic_idx + 1} (Probabilitas: {topic_prob:.4f})")

#                                 # Get words for the dominant topic
#                                 topics = get_topic_words(lda_model)
#                                 dominant_topic_words = topics[f"Topik #{topic_idx + 1}"]

#                                 st.write("**Kata-kata dalam Topik Dominan:**")
#                                 words_table = []
#                                 for item in dominant_topic_words[:5]:  # Show top 5 words
#                                     word = item['word']
#                                     entity_type = item['entity_type']
#                                     prob = item['prob']
#                                     if entity_type:
#                                         words_table.append(f"{word} ({entity_type}): {prob:.4f}")
#                                     else:
#                                         words_table.append(f"{word}: {prob:.4f}")

#                                 st.write(", ".join(words_table))
#                         else:
#                             st.info("Tidak dapat membuat visualisasi topik.")
#                     else:
#                         st.info("Tidak dapat menentukan distribusi topik. Mungkin tidak ada entitas yang relevan terdeteksi.")
#             except Exception as e:
#                 st.error(f"Terjadi kesalahan saat menganalisis teks: {str(e)}")
#                 st.info("Silakan coba lagi dengan teks yang berbeda atau hubungi administrator sistem.")
#         else:
#             st.warning("Silakan masukkan teks untuk dianalisis.")
