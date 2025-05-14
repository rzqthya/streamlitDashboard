# import pandas as pd
# import streamlit as st
# from io import StringIO
# import re
# import string
# import nltk
# from nltk.tokenize import word_tokenize
# import os
# import json

# # Download NLTK data if not already available
# @st.cache_resource
# def download_nltk_data():
#     """Download necessary NLTK data."""
#     try:
#         nltk.data.find('tokenizers/punkt_tab')
#     except LookupError:
#         nltk.download('punkt_tab')
    
#     try:
#         nltk.data.find('corpora/stopwords')
#     except LookupError:
#         nltk.download('stopwords')

# def read_text_file(uploaded_file):
#     """Read and process a text file."""
#     if uploaded_file is not None:
#         # To read file as string:
#         stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
#         string_data = stringio.read()
#         return string_data
#     return None

# def read_csv_file(uploaded_file):
#     """Read and process a CSV file."""
#     if uploaded_file is not None:
#         try:
#             df = pd.read_csv(uploaded_file)
#             return df
#         except Exception as e:
#             st.error(f"Error reading CSV file: {e}")
#     return None

# @st.cache_resource
# def load_slang_dict():
#     """Load slang dictionary from local file."""
#     # Path to the slang dictionary - Perbaikan path menggunakan os.path.join
#     dict_path = os.path.join("assets", "slang_words.txt")
    
#     # Check if file exists
#     if not os.path.exists(dict_path):
#         st.warning(f"File slang_words.txt tidak ditemukan di {dict_path}. Harap pastikan file tersebut berada di direktori yang sesuai.")
#         # Create a minimal dictionary if file doesn't exist
#         return {}
    
#     # Load the dictionary
#     try:
#         with open(dict_path, 'r', encoding='utf-8') as file:
#             slang_dict = json.load(file)
#         # st.success("Berhasil memuat kamus slang dari {dict_path}")
#         return slang_dict
#     except Exception as e:
#         st.error(f"Error saat memuat file slang dictionary: {str(e)}")
#         st.info("Pastikan format file slang_words.txt adalah JSON yang valid")
#         return {}

# @st.cache_data
# def get_stopwords():
#     """Get Indonesian stopwords with customizations."""
#     from nltk.corpus import stopwords
    
#     # Get stopword indonesia
#     list_stopwords = stopwords.words('indonesian')
    
#     # Custom stopwords to add
#     custom_stopwords = ["assallammualaikum", "assalamualaikum", "com", "assalam", "mualaikum", "asalamualaikum",
#                         "yth", "go", "mlah", "assalamu", "alaikum", "allahikum", "wallahi", "ass", "min", "gitu",
#                         "wassalamualaikum", "wrwb", "kq", "tdknya", "blaas", "lah", "nya", "terust", "assalamuallaikum",
#                         "wasalamuallaikum", "askum", "wr", "wb", "salam", "jt", "aamiin", "bawahsanya", "aaaaa", "iti",
#                         "didepan", "kedepan", "wassalamu", "dll", "pula", "salam", "pun", "blas", "blass", "mimin",
#                         "assallammualaikum", "aslammualaikum", "skalian", "allah", "alloh", "swt", "nah", "nggih",
#                         "masi", "baek", "sj", "plis", "plisssss", "mintol", "banget", "nget", "ngeeettt", "jangaaaannnn",
#                         "plis", "wasalammualikum", "nggeh", "asalamualaikum", "wallahu", "lam", "bish", "shawab", "kan",
#                         "an", "wassalam", "gae", "you", "aslm", "yah", "cuman", "sallam", "bm", "warahmatullahi"]
    
#     # Words to exclude from stopwords (keep these in the text)
#     exclude_stopwords = {'apa', 'apakah', 'dimana', 'kapan', 'mengapa', 'kenapa', 'siapa', 'bagaimana',
#                          'ada', 'adanya', 'agar', 'akan', 'akhir', 'akhirnya', 'apalagi', 'ataukah', 'ataupun',
#                          'awal', 'awalnya', 'balik', 'bekerja', 'benar', 'berada', 'berikan', 'beri', 'berkata',
#                          'bertanya', 'berupa', 'betul', 'boleh', 'buat', 'bisa', 'bukan', 'cara', 'caranya'}
    
#     # Add custom stopwords to the list
#     list_stopwords.extend(custom_stopwords)
    
#     # Convert list to set for faster operations
#     list_stopwords = set(list_stopwords)
    
#     # Remove excluded stopwords
#     list_stopwords = list_stopwords - exclude_stopwords
    
#     return list_stopwords

# def preprocess_text(text):
#     """Apply all preprocessing steps to text."""
#     # Ensure text is a string
#     if not isinstance(text, str):
#         if text is None:
#             return ""
#         try:
#             text = str(text)
#         except:
#             return ""
    
#     # Step 1: Case folding (lowercase)
#     text = text.lower()
    
#     # Step 2: Remove special characters
#     text = remove_word_special(text)
    
#     # Step 3: Remove numbers
#     text = remove_number(text)
    
#     # Step 4: Remove punctuation
#     text = remove_punctuation(text)
    
#     # Step 5: Remove whitespace
#     text = remove_whitespace_LT(text)
#     text = remove_whitespace_multiple(text)
    
#     # Step 6: Remove single characters
#     text = remove_singl_char(text)
    
#     # Step 7: Normalize slang words
#     slang_dict = load_slang_dict()
#     text = normalize_text_nltk(text, slang_dict)
    
#     return text

# def tokenize_and_remove_stopwords(text):
#     """Tokenize text and remove stopwords."""
#     # Ensure NLTK data is downloaded
#     download_nltk_data()
    
#     # Tokenize
#     tokens = word_tokenize(text)
    
#     # Get stopwords
#     list_stopwords = get_stopwords()
    
#     # Remove stopwords
#     filtered_tokens = [word for word in tokens if word not in list_stopwords]
    
#     return filtered_tokens

# # Helper functions for text preprocessing
# def remove_word_special(text):
#     # Remove tab, new line, and back slice
#     text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"")
#     # Remove non ASCII (emoticon, chinese word, etc.)
#     text = text.encode('ascii', 'replace').decode('ascii')
#     # Remove mention, link, hashtag
#     text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
#     # Remove incomplete URL
#     return text.replace("http://", " ").replace("https://", " ")

# def remove_number(text):
#     return re.sub(r"\d+", " ", text)

# def remove_punctuation(text):
#     return re.sub(f"[{re.escape(string.punctuation)}]", " ", text)

# def remove_whitespace_LT(text):
#     return text.strip()

# def remove_whitespace_multiple(text):
#     return re.sub('\s+',' ',text)

# def remove_singl_char(text):
#     return re.sub(r"\b[a-zA-Z]\b", "", text)

# def normalize_text_nltk(text, slang_dict):
#     # Ensure we have nltk downloaded
#     download_nltk_data()
#     # Tokenize and normalize
#     words = word_tokenize(text)
#     normalized_words = [slang_dict.get(word, word) for word in words]
#     return " ".join(normalized_words)

# def full_preprocessing_pipeline(text):
#     """Complete preprocessing pipeline."""
#     # Apply text preprocessing
#     processed_text = preprocess_text(text)
    
#     # Tokenize and remove stopwords
#     tokens = tokenize_and_remove_stopwords(processed_text)
    
#     return {
#         'processed_text': processed_text,
#         'tokens': tokens,
#         'tokens_joined': ' '.join(tokens)
#     }

import pandas as pd
import streamlit as st
from io import StringIO
import re
import string
import nltk
from nltk.tokenize import word_tokenize
import os
import json

# Download NLTK data if not already available
@st.cache_resource
def download_nltk_data():
    """Download necessary NLTK data."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

def read_text_file(uploaded_file):
    """Read and process a text file."""
    if uploaded_file is not None:
        try:
            # To read file as string:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            return string_data
        except Exception as e:
            st.error(f"Error reading text file: {e}")
    return None

def read_excel_file(uploaded_file):
    """Read and process an Excel file."""
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            return df
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
    return None

@st.cache_resource
def load_slang_dict():
    """Load slang dictionary from local file."""
    # Path to the slang dictionary
    dict_path = os.path.join("assets", "slang_words.txt")
    
    # Check if file exists
    if not os.path.exists(dict_path):
        st.warning(f"File slang_words.txt tidak ditemukan di {dict_path}. Harap pastikan file tersebut berada di direktori yang sesuai.")
        # Create a minimal dictionary if file doesn't exist
        return {}
    
    # Load the dictionary
    try:
        with open(dict_path, 'r', encoding='utf-8') as file:
            slang_dict = json.load(file)
        return slang_dict
    except Exception as e:
        st.error(f"Error saat memuat file slang dictionary: {str(e)}")
        st.info("Pastikan format file slang_words.txt adalah JSON yang valid")
        return {}

@st.cache_data
def get_stopwords():
    """Get Indonesian stopwords with customizations."""
    from nltk.corpus import stopwords
    
    # Get stopword indonesia
    list_stopwords = stopwords.words('indonesian')
    
    # Custom stopwords to add
    custom_stopwords = ["assallammualaikum", "assalamualaikum", "com", "assalam", "mualaikum", "asalamualaikum",
                        "yth", "go", "mlah", "assalamu", "alaikum", "allahikum", "wallahi", "ass", "min", "gitu",
                        "wassalamualaikum", "wrwb", "kq", "tdknya", "blaas", "lah", "nya", "terust", "assalamuallaikum",
                        "wasalamuallaikum", "askum", "wr", "wb", "salam", "jt", "aamiin", "bawahsanya", "aaaaa", "iti",
                        "didepan", "kedepan", "wassalamu", "dll", "pula", "salam", "pun", "blas", "blass", "mimin",
                        "assallammualaikum", "aslammualaikum", "skalian", "allah", "alloh", "swt", "nah", "nggih",
                        "masi", "baek", "sj", "plis", "plisssss", "mintol", "banget", "nget", "ngeeettt", "jangaaaannnn",
                        "plis", "wasalammualikum", "nggeh", "asalamualaikum", "wallahu", "lam", "bish", "shawab", "kan",
                        "an", "wassalam", "gae", "you", "aslm", "yah", "cuman", "sallam", "bm", "warahmatullahi", "wasalamualaikum",
                        "assallamualaiku", "assalaamualaikum", "sekalu", "tsbt", "assallamuaikum", "kayak", "saking",
                        "seng", "has", "wasalam", "doang", "yaa", "ya", "bx", "asallamualikum", "sngt", "sbb", "dah",
                        "asalammualaikum", "nyaa", "assalammualikum", "rek", "asalama", "aikum", "sangt", "nih", "yaaa",
                        "yy", "halo", "ta", "sak", "hemh", "sja", "wahallualam", "ngiih", "yh", "dsb", "dirohmati",
                        "sing", "sll", "sih", "alhamdulillah", "wasskum", "td", "tjs", "dh", "loh", "dear", "nohp",
                        "assalamualikum", "bismilah", "hallo", "amiin", "mangkanya", "wal", "permisi", "yes", "lainya",
                        "ok", "insyaalloh", "asslkm", "assalamulaikum", "yanng", "wrb", "gini", "dst", "buuuu", "amin",
                        "assalammualaikum", "tuch", "ngira", "pengapunten", "nuwun", "sewu", "sebentuk", "sg", "al", "sj", "nya",
                        "assallamualaikum", "setidak", "berharga", "siapkan", "berhubung", "setelahnya", "kecilan", "afiat", "lakukan",
                        "besarnya", "kebaikan", "kebaikannya", "baiknya", "alangkah", "diadakan", "sejelas", "perjelas", "dijadikan",
                        "jadikan", "sehari", "harian", "keseharian", "kesehariannya", "harinya", "seharian"]
                        
    
    # Words to exclude from stopwords (keep these in the text)
    exclude_stopwords = {'apa', 'apakah', 'dimana', 'kapan', 'mengapa', 'kenapa', 'siapa', 'bagaimana',
                            'ada', 'adanya', 'agar', 'akan', 'akhir', 'akhirnya', 'apalagi', 'ataukah', 'ataupun',
                            'awal', 'awalnya', 'balik', 'bekerja', 'benar', 'berada', 'berikan', 'beri', 'berkata',
                            'bertanya', 'berupa', 'betul', 'boleh', 'buat', 'bisa', 'bukan', 'cara', 'caranya',
                            'cukup', 'datang', 'dibuat', 'didapat', 'didatangkan', 'digunakan', 'dijawab', 'dijelaskan',
                            'dikarenakan', 'diketahui', 'diminta', 'dimintai', 'dimulai', 'diperlukan', 'diri', 'ditanyakan',
                            'ibu', 'ingin', 'itu', 'jangan', 'jawab', 'jelas', 'dijelaskan', 'jika', 'kalau', 'kalaupun',
                            'kami', 'keadaan', 'keluar', 'kini', 'kita', 'kurang', 'lewat', 'mampu', 'memberi', 'melihat',
                            'membuat', 'memberikan', 'membuat', 'memerlukan', 'meminta', 'memperlihatkan', 'mempertanyakan',
                            'mempunyai', 'menanyakan',  'mendapat', 'mendapatkan', 'mendatangi', 'mengetahui', 'menjawab',
                            'menjelaskan', 'menunjukkan', 'menyatakan', 'meyampaikan', 'menyeluruh', 'minta', 'pantas', 'mempertanyakan',
                            'punya', 'rata', 'sampaikan', 'sebelum', 'sebelumnya', 'seberapa', 'segera', 'sedikit', 'sementara',
                            'sepanjang', 'sesudah', 'sesudahnya', 'supaya', 'tahun', 'tanpa', 'tanya', 'tanyakan', 'tanyanya',
                            'tempat', 'tepat', 'terakhir', 'terdapat', 'tersampaikan', 'hingga',  'atau', 'tidak', 'dapat',
                            'belum', 'tetapi', 'namun', 'jawaban', 'jawabnya', 'menggunakan', 'berakhir', 'kecil'}
    
    # Add custom stopwords to the list
    list_stopwords.extend(custom_stopwords)
    
    # Convert list to set for faster operations
    list_stopwords = set(list_stopwords)
    
    # Remove excluded stopwords
    list_stopwords = list_stopwords - exclude_stopwords
    
    return list_stopwords

def preprocess_text(text):
    """Apply all preprocessing steps to text."""
    # Ensure text is a string
    if not isinstance(text, str):
        if text is None:
            return ""
        try:
            text = str(text)
        except:
            return ""
    
    # Step 1: Case folding (lowercase)
    text = text.lower()
    
    # Step 2: Remove special characters
    text = remove_word_special(text)
    
    # Step 3: Remove numbers
    text = remove_number(text)
    
    # Step 4: Remove punctuation
    text = remove_punctuation(text)
    
    # Step 5: Remove whitespace
    text = remove_whitespace_LT(text)
    text = remove_whitespace_multiple(text)
    
    # Step 6: Remove single characters
    text = remove_singl_char(text)
    
    # Step 7: Normalize slang words
    slang_dict = load_slang_dict()
    text = normalize_text_nltk(text, slang_dict)
    
    return text

def tokenize_and_remove_stopwords(text):
    """Tokenize text and remove stopwords."""
    # Ensure NLTK data is downloaded
    download_nltk_data()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Get stopwords
    list_stopwords = get_stopwords()
    
    # Remove stopwords
    filtered_tokens = [word for word in tokens if word not in list_stopwords]
    
    return filtered_tokens

# Helper functions for text preprocessing
def remove_word_special(text):
    # Remove tab, new line, and back slice
    text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\',"")
    # Remove non ASCII (emoticon, chinese word, etc.)
    text = text.encode('ascii', 'replace').decode('ascii')
    # Remove mention, link, hashtag
    text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
    # Remove incomplete URL
    return text.replace("http://", " ").replace("https://", " ")

def remove_number(text):
    return re.sub(r"\d+", " ", text)

def remove_punctuation(text):
    return re.sub(f"[{re.escape(string.punctuation)}]", " ", text)

def remove_whitespace_LT(text):
    return text.strip()

def remove_whitespace_multiple(text):
    return re.sub('\s+',' ',text)

def remove_singl_char(text):
    return re.sub(r"\b[a-zA-Z]\b", "", text)

def normalize_text_nltk(text, slang_dict):
    # Ensure we have nltk downloaded
    download_nltk_data()
    # Tokenize and normalize
    words = word_tokenize(text)
    normalized_words = [slang_dict.get(word, word) for word in words]
    return " ".join(normalized_words)

def full_preprocessing_pipeline(text):
    """Complete preprocessing pipeline."""
    # Apply text preprocessing
    processed_text = preprocess_text(text)
    
    # Tokenize and remove stopwords
    tokens = tokenize_and_remove_stopwords(processed_text)
    
    return {
        'processed_text': processed_text,
        'tokens': tokens,
        'tokens_joined': ' '.join(tokens)
    }