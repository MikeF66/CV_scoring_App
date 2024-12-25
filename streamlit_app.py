import streamlit as st
import os
import openai
from dotenv import load_dotenv
from parse_hh import get_candidate_info, get_job_description

st.title("Приложение для оценки резюме")

# Загрузка ключа API из .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("API-ключ OpenAI не найден. Проверьте файл .env.")
    st.stop()

openai.api_key = OPENAI_API_KEY

client = openai.Client(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.

Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу.
Потом представь результат в виде оценки от 1 до 10.
""".strip()

def request_gpt(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при запросе к OpenAI API: {str(e)}"

# Поля для ввода ссылок
vacancy_url = st.text_input("Введите URL вакансии")
resume_url = st.text_input("Введите URL-адрес резюме")

if st.button("Оценка резюме"):
    with st.spinner("Fetching and Scoring..."):
        try:
            vacancy_md = get_job_description(vacancy_url)
            st.write("Вакансия:")
            st.write(vacancy_md)
            st.write("---------------------------------")
            resume_md = get_candidate_info(resume_url)
            st.write("Резюме кандидата:")
            st.write(resume_md)
            # Подготовка запроса
            user_prompt = f"# ВАКАНСИЯ\n{vacancy_md}\n\n# РЕЗЮМЕ\n{resume_md}"
            response = request_gpt(SYSTEM_PROMPT, user_prompt)

            # Вывод результата
            st.write(response)

        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
