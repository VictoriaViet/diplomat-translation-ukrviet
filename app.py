import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

st.set_page_config(page_title="Дипломатичний переклад: В'єтнамсько-український", layout="wide")

# 1. Завантаження лексики з CSV
@st.cache_data
def load_data():
    df = pd.read_csv("lexics.csv")
    df.columns = ["vi", "uk"]
    return df.dropna()

df = load_data()

st.title("🏛️ Тренажер дипломатичного перекладу (VI-UK)")

# 2. Налаштування безкоштовного Gemini API Key
api_key = st.sidebar.text_input("Введіть Gemini API Key (для генерації речень):", type="password")

tab1, tab2 = st.tabs(["📇 Картки лексики", "📝 Генератор речень та контекстів"])

# Таб 1: Інтерактивні картки
with tab1:
    st.subheader("Вивчення термінології")
    if "card_idx" not in st.session_state:
        st.session_state.card_idx = 0

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Випадковий термін"):
            st.session_state.card_idx = random.randint(0, len(df) - 1)
        
        row = df.iloc[st.session_state.card_idx]
        st.info(f"**В'єтнамська:** {row['vi']}")
        
        if st.checkbox("Показати переклад"):
            st.success(f"**Українська:** {row['uk']}")

# Таб 2: Генерація зв'язного тексту для перекладу
with tab2:
    st.subheader("Практика перекладу зв'язного повідомлення")
    
    selected_num = st.slider("Кількість термінів у реченні:", 1, 3, 2)
    sample_terms = df.sample(selected_num)
    
    st.write("**Терміни для включення у речення:**")
    for _, r in sample_terms.iterrows():
        st.write(f"- {r['vi']} (*{r['uk']}*)")

    if st.button("🚀 Згенерувати дипломатичне речення"):
        if not api_key:
            st.warning("Будь ласка, додайте безкоштовний Gemini API key у бічній панелі.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            terms_vi = ", ".join(sample_terms['vi'].tolist())
            prompt = f"""
            Ти викладач дипломатичного перекладу в'єтнамської мови.
            Склади 1-2 дипломатичні речення в'єтнамською мовою (стиль офіційно-діловий, новини Bộ Ngoại giao або Nhan Dan),
            використовуючи обов'язково такі терміни: {terms_vi}.
            
            Надай відповідь у форматуванні:
            1. Текст в'єтнамською мовою.
            2. Еталонний переклад українською мовою.
            3. Короткий коментар щодо складної лексики чи граматики.
            """
            
            response = model.generate_content(prompt)
            st.markdown(response.text)