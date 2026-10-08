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

st.title("🏛️ Тренажер дипломатичного перекладу")

# Перемикач напрямку перекладу для всього додатку
direction = st.sidebar.radio(
    "Оберіть напрямок перекладу:",
    ("З в'єтнамської на українську (VI ➔ UK)", "З української на в'єтнамську (UK ➔ VI)")
)

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
        
        if direction == "З в'єтнамської на українську (VI ➔ UK)":
            st.info(f"**Оригінал (в'єтнамська):** {row['vi']}")
            if st.checkbox("Показати переклад"):
                st.success(f"**Переклад (українська):** {row['uk']}")
        else:
            st.info(f"**Оригінал (українська):** {row['uk']}")
            if st.checkbox("Показати переклад"):
                st.success(f"**Переклад (в'єтнамська):** {row['vi']}")

# Таб 2: Генерація зв'язного тексту для перекладу
with tab2:
    st.subheader("Практика перекладу зв'язного повідомлення")
    
    selected_num = st.slider("Кількість термінів у реченні:", 1, 3, 2)
    sample_terms = df.sample(selected_num)
    
    st.write("**Терміни для включення у речення:**")
    for _, r in sample_terms.iterrows():
        st.write(f"- {r['vi']} (*{r['uk']}*)")

    if st.button("🚀 Згенерувати дипломатичне речення"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            st.error("Помилка: API ключ не знайдено в налаштуваннях Secrets Streamlit.")
        else:
            genai.configure(api_key=api_key)
            # Вказано актуальну назву моделі Gemini
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            terms_vi = ", ".join(sample_terms['vi'].tolist())
            terms_uk = ", ".join(sample_terms['uk'].tolist())
            
            if direction == "З в'єтнамської на українську (VI ➔ UK)":
                prompt = f"""
                Ти викладач дипломатичного перекладу.
                Склади 1-2 дипломатичні речення В'ЄТНАМСЬКОЮ МОВОЮ (офіційно-діловий стиль, дипломатичний протокол/новини),
                використовуючи обов'язково такі терміни: {terms_vi}.
                
                Формат відповіді:
                1. 📝 **Текст для перекладу (в'єтнамською):** [Завдання для студента]
                2. ✅ **Еталонний переклад (українською):** [Переклад]
                3. 💡 **Лексико-граматичний коментар:** [Пояснення]
                """
            else:
                prompt = f"""
                Ти викладач дипломатичного перекладу.
                Склади 1-2 дипломатичні речення УКРАЇНСЬКОЮ МОВОЮ (офіційно-діловий стиль, дипломатичні новини/заяви),
                використовуючи обов'язково такі терміни: {terms_uk}.
                
                Формат відповіді:
                1. 📝 **Текст для перекладу (українською):** [Завдання для студента]
                2. ✅ **Еталонний переклад (в'єтнамською):** [Переклад]
                3. 💡 **Лексико-граматичний коментар:** [Пояснення]
                """
            
            with st.spinner("Генеруємо дипломатичний контекст..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Помилка при зверненні до API: {e}")
