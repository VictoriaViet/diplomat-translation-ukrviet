import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

st.set_page_config(page_title="Дипломатичний переклад: В'єтнамсько-український", layout="wide")
st.cache_data.clear()
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

# Функція безпечної генерації
def run_generation(prompt_text, api_key_value):
    genai.configure(api_key=api_key_value)
    
    # Список моделей у порядку пріоритету
    available_models = [
        'gemini-1.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-pro'
    ]
    
    last_error_message = None
    for current_model_name in available_models:
        try:
            gen_model = genai.GenerativeModel(current_model_name)
            response_obj = gen_model.generate_content(prompt_text)
            if response_obj and response_obj.text:
                return response_obj.text, None
        except Exception as e:
            last_error_message = str(e)
            continue
            
    return None, last_error_message
    
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
            
            terms_vi = ", ".join(sample_terms['vi'].tolist())
            terms_uk = ", ".join(sample_terms['uk'].tolist())
            
            if direction == "З в'єтнамської на українську (VI ➔ UK)":
                prompt = f"""
                Ти викладач дипломатичного перекладу.
                Склади 1 дипломатичне речення В'ЄТНАМСЬКОЮ МОВОЮ (офіційно-діловий стиль, дипломатичний протокол/новини),
                використовуючи обов'язково такі терміни: {terms_vi}.
                
                Формат відповіді:
                1. 📝 **Текст для перекладу (в'єтнамською):** [речення в’єтнамською]
                2. ✅ **Еталонний переклад (українською):** [Переклад]
                3. 💡 **Лексико-граматичний коментар:** [Коротке пояснення]
                """
            else:
                prompt = f"""
                Ти викладач дипломатичного перекладу.
                Склади 1 дипломатичне речення УКРАЇНСЬКОЮ МОВОЮ (офіційно-діловий стиль, дипломатичні новини/заяви),
                використовуючи обов'язково такі терміни: {terms_uk}.
                
                Формат відповіді:
                1. 📝 **Текст для перекладу (українською):** [речення українською]
                2. ✅ **Еталонний переклад (в'єтнамською):** [Переклад]
                3. 💡 **Лексико-граматичний коментар:** [Коротке пояснення]
                """
            with st.spinner("Генеруємо завдання..."):
                output_text, error_info = run_generation(prompt, api_key)
                if output_text:
                    st.markdown(output_text)
                else:
                    st.error(f"Помилка при генерації: {error_info}")
