import pickle
import os
import spacy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import streamlit as st
from utils.preprocess import full_preprocessing_pipeline
from custom_vectorizer_utils import dummy_tokenizer, dummy_preprocessor

# Safely import gensim and other dependencies
try:
    from gensim import matutils
    from gensim.models import LdaModel
    from scipy.sparse import csr_matrix
    from sklearn.feature_extraction.text import CountVectorizer
except ImportError:
    st.error("Missing required dependencies. Please install them with: pip install gensim scipy scikit-learn")

from custom_vectorizer_utils import dummy_tokenizer, dummy_preprocessor

# Path to the models
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

@st.cache_resource
def load_models():
    """Load the trained models."""
    try:
        # Load NER model
        ner_model_path = os.path.join(MODEL_DIR, "ner_model")
        ner_model = spacy.load(ner_model_path)
        
        # Load LDA model
        lda_model_path = os.path.join(MODEL_DIR, "lda_model.pkl")
        with open(lda_model_path, 'rb') as f:
            lda_model = pickle.load(f)
            
        # Load dictionary
        dictionary_path = os.path.join(MODEL_DIR, "dictionary.pkl")
        with open(dictionary_path, 'rb') as f:
            dictionary = pickle.load(f)

        # Load CountVectorizer (Tambahkan baris ini)
        cv_path = os.path.join(MODEL_DIR, "cv2.pkl")
        with open(cv_path, 'rb') as f:
            cv = pickle.load(f)
            
        return ner_model, lda_model, dictionary, cv
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None, None, None

# Function to preprocess text for LDA
def preprocess_for_lda(text, ner_model):
    """Process text for LDA by identifying named entities"""
    # Ensure input is properly handled
    if not text or not isinstance(text, str):
        return []
    
    # Process with NER model
    doc = ner_model(text)
    tokens = []
    
    # Create tokens with entity labels
    for ent in doc.ents:
        tokens.append(f"{ent.text.lower()}_{ent.label_}")
    
    return tokens

# Function to analyze text
def analyze_text(text, ner_model, lda_model, dictionary, cv):
    """Analyze text using NER and LDA models."""
    try:
        # Handle non-string input
        if not isinstance(text, str):
            if text is None:
                text = ""
            else:
                text = str(text)
                
        # First, apply the full preprocessing pipeline
        preprocessing_result = full_preprocessing_pipeline(text)
        preprocessed_text = preprocessing_result['processed_text']
        
        # Recognize entities on the preprocessed text
        doc = ner_model(preprocessed_text)
        entities = {
            'STATUS': [],
            'PROGRAM': [],
            'PIHAK': []
        }
        
        # Extract entities
        for ent in doc.ents:
            if ent.label_ in entities:
                # Add entity if not already in list
                if ent.text.lower() not in [e.lower() for e in entities[ent.label_]]:
                    entities[ent.label_].append(ent.text)
        
        # Preprocess for topic modeling
        processed_text = preprocess_for_lda(preprocessed_text, ner_model)
        
        # Create vectorizer (similar to what was used in training)
        # cv = CountVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x, token_pattern=None)
        
        # Only train on the current document (we can't access the original CV)
        if processed_text:
            # cv.fit([processed_text])
            data_cv = cv.transform([processed_text])
            bow = matutils.Sparse2Corpus(csr_matrix(data_cv.transpose()))
            
            # Get document topic distribution
            if list(bow):
                topic_distribution = list(lda_model.get_document_topics(list(bow)[0]))
                dominant_topic = max(topic_distribution, key=lambda x: x[1]) if topic_distribution else None
            else:
                topic_distribution = []
                dominant_topic = None
        else:
            topic_distribution = []
            dominant_topic = None
        
        return {
            'text': text,
            'preprocessed_text': preprocessed_text,
            'tokens': preprocessing_result['tokens'],
            'entities': entities,
            'processed_tokens': processed_text,
            'topics': topic_distribution,
            'dominant_topic': dominant_topic
        }
    except Exception as e:
        st.error(f"Error analyzing text: {str(e)}")
        # Return default structure even when error occurs
        return {
            'text': text,
            'preprocessed_text': text,
            'tokens': [],
            'entities': {'STATUS': [], 'PROGRAM': [], 'PIHAK': []},
            'processed_tokens': [],
            'topics': [],
            'dominant_topic': None
        }

# Function to visualize topic distribution
def visualize_topic_distribution(topic_distribution):
    """Create a visualization of topic distribution"""
    if not topic_distribution:
        return None
        
    topic_df = pd.DataFrame(
        [(f"Topik #{topic[0]+1}", topic[1]) for topic in topic_distribution],
        columns=["Topik", "Probabilitas"]
    )
    
    # Create bar chart with Altair
    chart = alt.Chart(topic_df).mark_bar().encode(
        x=alt.X('Topik:N', sort=None),
        y=alt.Y('Probabilitas:Q'),
        color=alt.Color('Topik:N', legend=None),
        tooltip=['Topik', 'Probabilitas']
    ).properties(
        title='Distribusi Topik',
        width=400,
        height=300
    )
    
    return chart

# Function to get topic words
# def get_topic_words(lda_model, num_topics=7, num_words=10):
#     """Get the most relevant words for each topic"""
#     topics = {}
#     for topic_idx in range(num_topics):
#         topic_words = lda_model.show_topic(topic_idx, topn=num_words)
#         topics[f"Topik #{topic_idx+1}"] = [
#             {"word": word.split('_')[0] if '_' in word else word, 
#              "entity_type": word.split('_')[1] if '_' in word else None,
#              "prob": prob}
#             for word, prob in topic_words
#         ]
#     return topics

def get_topic_words(lda_model, num_topics=7, num_words=10):
    topics = {}
    for topic_idx in range(num_topics):
        topic_words = lda_model.show_topic(topic_idx, topn=num_words)
        topics[f"Topik #{topic_idx+1}"] = [
                {"word": word.split('_')[0] if '_' in word else word, 
                "entity_type": word.split('_')[1] if '_' in word else None,
                "prob": prob}
            for word, prob in topic_words
        ]
    return topics


# Function to create entity visualization
def visualize_entities(entities_list, title="Entitas Terdeteksi"):
    """Create a visualization of named entities"""
    # Flatten entities dictionary to list of tuples
    flat_entities = []
    for label, terms in entities_list.items():
        for term in terms:
            flat_entities.append({"Label": label, "Term": term})
    
    if flat_entities:
        df = pd.DataFrame(flat_entities)
        
        # Create colored display of entities
        st.subheader(title)
        
        # Use Altair to create a visualization
        if not df.empty:
            chart = alt.Chart(df).mark_bar().encode(
                x='count():Q',
                y=alt.Y('Term:N', sort='-x'),
                color='Label:N',
                tooltip=['Term', 'Label']
            ).properties(
                height=max(100, min(30 * len(df), 400))
            )
            
            return chart
        else:
            return None
    else:
        return None

# Function to visualize topic distribution from file
def visualize_topic_distribution_from_file(file_content, ner_model, lda_model, dictionary):
    """
    Analyze multiple lines of text from a file and visualize topic distribution.
    """
    if not file_content or not isinstance(file_content, str):
        return None, None, None
        
    lines = file_content.strip().split('\n')
    all_results = []
    preprocessing_details = []
    
    for line in lines:
        if line.strip():  # Skip empty lines
            result = analyze_text(line, ner_model, lda_model, dictionary)
            
            # Add preprocessing details
            preprocessing_details.append({
                'original_text': line,
                'preprocessed_text': result['preprocessed_text'],
                'tokens': result['tokens']
            })
            
            if result['dominant_topic']:
                all_results.append({
                    'text': result['text'][:50] + '...' if len(result['text']) > 50 else result['text'],
                    'topic': f"Topik #{result['dominant_topic'][0]+1}",
                    'probability': result['dominant_topic'][1],
                    'entities': result['entities']
                })
    
    if all_results:
        df = pd.DataFrame(all_results)
        preproc_df = pd.DataFrame(preprocessing_details)
        
        # Create a chart showing dominant topics across texts
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('topic:N', title='Topik Dominan'),
            y=alt.Y('count():Q', title='Jumlah Teks'),
            color=alt.Color('topic:N', legend=None),
            tooltip=['topic', 'count()']
        ).properties(
            title='Distribusi Topik Dominan',
            width=600,
            height=400
        )
        
        return chart, df, preproc_df
    else:
        return None, None, None

# import pickle
# import os
# import spacy
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import altair as alt
# import streamlit as st
# from utils.preprocess import full_preprocessing_pipeline

# # Safely import gensim and other dependencies
# try:
#     from gensim import matutils
#     from gensim.models import LdaModel
#     from scipy.sparse import csr_matrix
#     from sklearn.feature_extraction.text import CountVectorizer
# except ImportError:
#     st.error("Missing required dependencies. Please install them with: pip install gensim scipy scikit-learn")

# # Path to the models
# MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

# @st.cache_resource
# def load_models():
#     """Load the trained models."""
#     try:
#         # Load NER model
#         ner_model_path = os.path.join(MODEL_DIR, "ner_model")
#         ner_model = spacy.load(ner_model_path)

#         # Load LDA model (model dengan 30 topik)
#         lda_model_path = os.path.join(MODEL_DIR, "lda_model.pkl")
#         with open(lda_model_path, 'rb') as f:
#             lda_model = pickle.load(f)

#         # Load dictionary
#         dictionary_path = os.path.join(MODEL_DIR, "dictionary.pkl")
#         with open(dictionary_path, 'rb') as f:
#             dictionary = pickle.load(f)

#         # Tetapkan 7 topik pertama untuk digunakan dalam analisis
#         # Ini adalah 7 topik yang akan kita fokuskan (topik 0-6, yang ditampilkan sebagai topik 1-7)
#         selected_topics = list(range(7))  # Topik 0-6 (akan ditampilkan sebagai Topik 1-7)

#         return ner_model, lda_model, dictionary, selected_topics
#     except Exception as e:
#         st.error(f"Error loading models: {str(e)}")
#         return None, None, None, None

# # Function to preprocess text for LDA
# def preprocess_for_lda(text, ner_model):
#     """Process text for LDA by identifying named entities"""
#     # Ensure input is properly handled
#     if not text or not isinstance(text, str):
#         return []

#     # Process with NER model
#     doc = ner_model(text)
#     tokens = []

#     # Create tokens with entity labels
#     for ent in doc.ents:
#         tokens.append(f"{ent.text.lower()}_{ent.label_}")

#     return tokens

# # Function to analyze text using only selected topics
# def analyze_text(text, ner_model, lda_model, dictionary, selected_topics):
#     """Analyze text using NER and LDA models, hanya menggunakan 7 topik tertentu."""
#     try:
#         # Handle non-string input
#         if not isinstance(text, str):
#             if text is None:
#                 text = ""
#             else:
#                 text = str(text)

#         # First, apply the full preprocessing pipeline
#         preprocessing_result = full_preprocessing_pipeline(text)
#         preprocessed_text = preprocessing_result['processed_text']

#         # Recognize entities on the preprocessed text
#         doc = ner_model(preprocessed_text)
#         entities = {
#             'STATUS': [],
#             'PROGRAM': [],
#             'PIHAK': []
#         }

#         # Extract entities
#         for ent in doc.ents:
#             if ent.label_ in entities:
#                 # Add entity if not already in list
#                 if ent.text.lower() not in [e.lower() for e in entities[ent.label_]]:
#                     entities[ent.label_].append(ent.text)

#         # Preprocess for topic modeling
#         processed_text = preprocess_for_lda(preprocessed_text, ner_model)

#         # Create vectorizer (similar to what was used in training)
#         cv = CountVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x, token_pattern=None)

#         # Only train on the current document (we can't access the original CV)
#         if processed_text:
#             cv.fit([processed_text])
#             data_cv = cv.transform([processed_text])
#             bow = matutils.Sparse2Corpus(csr_matrix(data_cv.transpose()))

#             # Get document topic distribution
#             if list(bow):
#                 # Dapatkan distribusi topik lengkap (semua 30 topik)
#                 full_topic_distribution = list(lda_model.get_document_topics(list(bow)[0], minimum_probability=0))

#                 # Filter hanya untuk 7 topik yang dipilih (0-6, ditampilkan sebagai 1-7)
#                 selected_distribution = []
#                 for topic_id, prob in full_topic_distribution:
#                     if topic_id in selected_topics:
#                         selected_distribution.append((topic_id, prob))

#                 # Cukup tentukan topik dominan dengan mencari maksimum
#                 if selected_distribution:
#                     # Ambil topik dominan tanpa mengubah urutan selected_distribution
#                     dominant_topic = max(selected_distribution, key=lambda x: x[1])
                    
#                     # Gunakan distribusi asli tanpa perubahan
#                     topic_distribution = selected_distribution
#                 else:
#                     topic_distribution = []
#                     dominant_topic = None

#                 return {
#                     'text': text,
#                     'preprocessed_text': preprocessed_text,
#                     'tokens': preprocessing_result['tokens'],
#                     'entities': entities,
#                     'processed_tokens': processed_text,
#                     'topics': topic_distribution,
#                     'dominant_topic': dominant_topic
#                 }
#             else:
#                 topic_distribution = []
#                 dominant_topic = None
#         else:
#             topic_distribution = []
#             dominant_topic = None

#         return {
#             'text': text,
#             'preprocessed_text': preprocessed_text,
#             'tokens': preprocessing_result['tokens'],
#             'entities': entities,
#             'processed_tokens': processed_text,
#             'topics': [],
#             'dominant_topic': None
#         }

#     except Exception as e:
#         st.error(f"Error analyzing text: {str(e)}")
#         # Return default structure even when error occurs
#         return {
#             'text': text,
#             'preprocessed_text': text,
#             'tokens': [],
#             'entities': {'STATUS': [], 'PROGRAM': [], 'PIHAK': []},
#             'processed_tokens': [],
#             'topics': [],
#             'dominant_topic': None
#         }

# # Function to visualize topic distribution
# def visualize_topic_distribution(topic_distribution):
#     """Create a visualization of topic distribution"""
#     if not topic_distribution:
#         return None

#     topic_df = pd.DataFrame(
#         [(f"Topik #{topic[0]+1}", topic[1]) for topic in topic_distribution],
#         columns=["Topik", "Probabilitas"]
#     )

#     # Create bar chart with Altair
#     chart = alt.Chart(topic_df).mark_bar().encode(
#         x=alt.X('Topik:N', sort=None),
#         y=alt.Y('Probabilitas:Q'),
#         color=alt.Color('Topik:N', legend=None),
#         tooltip=['Topik', 'Probabilitas']
#     ).properties(
#         title='Distribusi Topik',
#         width=400,
#         height=300
#     )

#     return chart

# # Function to get topic words
# def get_topic_words(lda_model, num_words=10):
#     """Get the most relevant words for each topic"""
#     topics = {}
#     # Ambil jumlah topik dari model (30 topik)
#     num_topics = lda_model.num_topics

#     for topic_idx in range(num_topics):
#         topic_words = lda_model.show_topic(topic_idx, topn=num_words)
#         topics[f"Topik #{topic_idx+1}"] = [
#             {"word": word.split('_')[0] if '_' in word else word,
#              "entity_type": word.split('_')[1] if '_' in word else None,
#              "prob": prob}
#             for word, prob in topic_words
#         ]
#     return topics

# # Function to create entity visualization
# def visualize_entities(entities_list, title="Entitas Terdeteksi"):
#     """Create a visualization of named entities"""
#     # Flatten entities dictionary to list of tuples
#     flat_entities = []
#     for label, terms in entities_list.items():
#         for term in terms:
#             flat_entities.append({"Label": label, "Term": term})

#     if flat_entities:
#         df = pd.DataFrame(flat_entities)

#         # Create colored display of entities
#         st.subheader(title)

#         # Use Altair to create a visualization
#         if not df.empty:
#             chart = alt.Chart(df).mark_bar().encode(
#                 x='count():Q',
#                 y=alt.Y('Term:N', sort='-x'),
#                 color='Label:N',
#                 tooltip=['Term', 'Label']
#             ).properties(
#                 height=max(100, min(30 * len(df), 400))
#             )

#             return chart
#         else:
#             return None
#     else:
#         return None

# # Function to visualize topic distribution from file
# def visualize_topic_distribution_from_file(file_content, ner_model, lda_model, dictionary, selected_topics):
#     """
#     Analyze multiple lines of text from a file and visualize topic distribution.
#     """
#     if not file_content or not isinstance(file_content, str):
#         return None, None, None

#     lines = file_content.strip().split('\n')
#     all_results = []
#     preprocessing_details = []

#     for line in lines:
#         if line.strip():  # Skip empty lines
#             result = analyze_text(line, ner_model, lda_model, dictionary, selected_topics)

#             # Add preprocessing details
#             preprocessing_details.append({
#                 'original_text': line,
#                 'preprocessed_text': result['preprocessed_text'],
#                 'tokens': result['tokens']
#             })

#             if result['dominant_topic']:
#                 all_results.append({
#                     'text': result['text'][:50] + '...' if len(result['text']) > 50 else result['text'],
#                     'topic': f"Topik #{result['dominant_topic'][0]+1}",
#                     'probability': result['dominant_topic'][1],
#                     'entities': result['entities']
#                 })

#     if all_results:
#         df = pd.DataFrame(all_results)
#         preproc_df = pd.DataFrame(preprocessing_details)

#         # Create a chart showing dominant topics across texts
#         chart = alt.Chart(df).mark_bar().encode(
#             x=alt.X('topic:N', title='Topik Dominan'),
#             y=alt.Y('count():Q', title='Jumlah Teks'),
#             color=alt.Color('topic:N', legend=None),
#             tooltip=['topic', 'count()']
#         ).properties(
#             title='Distribusi Topik Dominan',
#             width=600,
#             height=400
#         )

#         return chart, df, preproc_df
#     else:
#         return None, None, None

# import pickle
# import os
# import spacy
# import pandas as pd
# import numpy as np
# import altair as alt
# import streamlit as st
# from utils.preprocess import full_preprocessing_pipeline

# # Safely import gensim and other dependencies
# try:
#     from gensim import matutils
#     from gensim.models import LdaModel
#     from scipy.sparse import csr_matrix
#     from sklearn.feature_extraction.text import CountVectorizer
# except ImportError:
#     st.error("Missing required dependencies. Please install them with: pip install gensim scipy scikit-learn")

# # Path to the models
# MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

# @st.cache_resource
# def load_models():
#     """Load the trained models."""
#     try:
#         # Load NER model
#         ner_model_path = os.path.join(MODEL_DIR, "ner_model")
#         ner_model = spacy.load(ner_model_path)
        
#         # Load LDA model
#         lda_model_path = os.path.join(MODEL_DIR, "lda_model.pkl")
#         with open(lda_model_path, 'rb') as f:
#             lda_model = pickle.load(f)
            
#         # Load dictionary
#         dictionary_path = os.path.join(MODEL_DIR, "dictionary.pkl")
#         with open(dictionary_path, 'rb') as f:
#             dictionary = pickle.load(f)
            
#         return ner_model, lda_model, dictionary
#     except Exception as e:
#         st.error(f"Error loading models: {str(e)}")
#         return None, None, None

# # Function to preprocess text for LDA
# def preprocess_for_lda(text, ner_model):
#     """Process text for LDA by identifying named entities"""
#     # Ensure input is properly handled
#     if not text or not isinstance(text, str):
#         return []
    
#     # Process with NER model
#     doc = ner_model(text)
#     tokens = []
    
#     # Create tokens with entity labels
#     for ent in doc.ents:
#         tokens.append(f"{ent.text.lower()}_{ent.label_}")
    
#     return tokens

# # Function to analyze text
# def analyze_text(text, ner_model, lda_model, dictionary):
#     """Analyze text using NER and LDA models."""
#     try:
#         # Handle non-string input
#         if not isinstance(text, str):
#             if text is None:
#                 text = ""
#             else:
#                 text = str(text)
                
#         # First, apply the full preprocessing pipeline
#         preprocessing_result = full_preprocessing_pipeline(text)
#         preprocessed_text = preprocessing_result['processed_text']
        
#         # Recognize entities on the preprocessed text
#         doc = ner_model(preprocessed_text)
#         entities = {
#             'STATUS': [],
#             'PROGRAM': [],
#             'PIHAK': []
#         }
        
#         # Extract entities
#         for ent in doc.ents:
#             if ent.label_ in entities:
#                 # Add entity if not already in list
#                 if ent.text.lower() not in [e.lower() for e in entities[ent.label_]]:
#                     entities[ent.label_].append(ent.text)
        
#         # Preprocess for topic modeling
#         processed_text = preprocess_for_lda(preprocessed_text, ner_model)
        
#         # Create vectorizer (similar to what was used in training)
#         cv = CountVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x, token_pattern=None)
        
#         # Only train on the current document (we can't access the original CV)
#         if processed_text:
#             cv.fit([processed_text])
#             data_cv = cv.transform([processed_text])
#             bow = matutils.Sparse2Corpus(csr_matrix(data_cv.transpose()))
            
#             # Get document topic distribution
#             if list(bow):
#                 topic_distribution = list(lda_model.get_document_topics(list(bow)[0], minimum_probability=0))
#                 dominant_topic = max(topic_distribution, key=lambda x: x[1]) if topic_distribution else None
#             else:
#                 topic_distribution = []
#                 dominant_topic = None
#         else:
#             topic_distribution = []
#             dominant_topic = None
        
#         return {
#             'text': text,
#             'preprocessed_text': preprocessed_text,
#             'tokens': preprocessing_result['tokens'],
#             'entities': entities,
#             'processed_tokens': processed_text,
#             'topics': topic_distribution,
#             'dominant_topic': dominant_topic
#         }
#     except Exception as e:
#         st.error(f"Error analyzing text: {str(e)}")
#         # Return default structure even when error occurs
#         return {
#             'text': text,
#             'preprocessed_text': text,
#             'tokens': [],
#             'entities': {'STATUS': [], 'PROGRAM': [], 'PIHAK': []},
#             'processed_tokens': [],
#             'topics': [],
#             'dominant_topic': None
#         }

# # Function to get topic words
# def get_topic_words(lda_model, num_words=5):
#     """Get the most relevant words for each topic"""
#     top_words = {}
    
#     # Get the number of topics from the model
#     num_topics = lda_model.num_topics
    
#     for topic_idx in range(num_topics):
#         # Get the top words for this topic
#         topic_words = lda_model.show_topic(topic_idx, topn=num_words)
        
#         # Format the results
#         top_words[f"Topik #{topic_idx+1}"] = [
#             {"word": word.split('_')[0] if '_' in word else word, 
#              "entity_type": word.split('_')[1] if '_' in word else None,
#              "prob": prob}
#             for word, prob in topic_words
#         ]
    
#     return top_words

# # Function to visualize topic distribution
# def visualize_topic_distribution(topic_distribution):
#     """Create a visualization of topic distribution"""
#     if not topic_distribution:
#         return None
        
#     topic_df = pd.DataFrame(
#         [(f"Topik #{topic[0]+1}", topic[1]) for topic in topic_distribution],
#         columns=["Topik", "Probabilitas"]
#     )
    
#     # Create bar chart with Altair
#     chart = alt.Chart(topic_df).mark_bar().encode(
#         x=alt.X('Topik:N', sort=None),
#         y=alt.Y('Probabilitas:Q'),
#         color=alt.Color('Topik:N', legend=None),
#         tooltip=['Topik', 'Probabilitas']
#     ).properties(
#         title='Distribusi Topik',
#         width=400,
#         height=300
#     )
    
#     return chart

# # Function to create entity visualization
# def visualize_entities(entities_list, title="Entitas Terdeteksi"):
#     """Create a visualization of named entities"""
#     # Flatten entities dictionary to list of tuples
#     flat_entities = []
#     for label, terms in entities_list.items():
#         for term in terms:
#             flat_entities.append({"Label": label, "Term": term})
    
#     if flat_entities:
#         df = pd.DataFrame(flat_entities)
        
#         # Create colored display of entities
#         st.subheader(title)
        
#         # Use Altair to create a visualization
#         if not df.empty:
#             chart = alt.Chart(df).mark_bar().encode(
#                 x='count():Q',
#                 y=alt.Y('Term:N', sort='-x'),
#                 color='Label:N',
#                 tooltip=['Term', 'Label']
#             ).properties(
#                 height=max(100, min(30 * len(df), 400))
#             )
            
#             return chart
#         else:
#             return None
#     else:
#         return None

# # Function to visualize topic distribution from file (kept for backward compatibility)
# def visualize_topic_distribution_from_file(file_content, ner_model, lda_model, dictionary):
#     """
#     Analyze multiple lines of text from a file and visualize topic distribution.
#     This function is kept for backward compatibility with existing code.
#     """
#     # For text files that are strings
#     if isinstance(file_content, str):
#         lines = file_content.strip().split('\n')
#     # For Excel files that are already lists
#     elif isinstance(file_content, list):
#         lines = file_content
#     else:
#         return None, pd.DataFrame(), None
        
#     all_results = []
#     preprocessing_details = []
    
#     for line in lines:
#         if line and isinstance(line, str) and not line.isspace():  # Skip empty lines
#             result = analyze_text(line, ner_model, lda_model, dictionary)
            
#             # Add preprocessing details
#             preprocessing_details.append({
#                 'original_text': line,
#                 'preprocessed_text': result['preprocessed_text'],
#                 'tokens': result['tokens']
#             })
            
#             if result['dominant_topic']:
#                 # Format entity text for display
#                 entity_text = ""
#                 for entity_type, entities in result['entities'].items():
#                     if entities:
#                         entity_text += f"{entity_type}: {', '.join(entities)}; "
                
#                 all_results.append({
#                     'text': line[:50] + '...' if len(line) > 50 else line,
#                     'topic': f"Topik #{result['dominant_topic'][0]+1}",
#                     'probability': result['dominant_topic'][1],
#                     'entities': entity_text
#                 })
    
#     if all_results:
#         df = pd.DataFrame(all_results)
#         preproc_df = pd.DataFrame(preprocessing_details)
        
#         # Create a chart showing dominant topics across texts
#         chart = alt.Chart(df).mark_bar().encode(
#             x=alt.X('topic:N', title='Topik Dominan'),
#             y=alt.Y('count():Q', title='Jumlah Teks'),
#             color=alt.Color('topic:N', legend=None),
#             tooltip=['topic', 'count()']
#         ).properties(
#             title='Distribusi Topik Dominan',
#             width=600,
#             height=400
#         )
        
#         return chart, df, preproc_df
#     else:
#         # Return empty DataFrames instead of None to prevent warnings
#         return None, pd.DataFrame(), pd.DataFrame()