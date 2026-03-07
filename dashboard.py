import streamlit as st
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

# Настройка страницы
st.set_page_config(
    page_title="RISC-V Verifier | Team Alpha",
    page_icon="🔬",
    layout="wide"
)

# Функция для загрузки данных из JSON файла
def load_results():
    """Загружает результаты из test_results/results.json"""
    try:
        if os.path.exists('test_results/results.json'):
            with open('test_results/results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        else:
            # Если файла нет, возвращаем тестовые данные
            return {
                "coverage": 25,
                "bugs_found": 0,
                "pylint_score": 7.5,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tests_passed": 156,
                "tests_total": 200
            }
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None

# Загружаем данные
data = load_results()

# Заголовок
st.markdown(f"""
<div style='background: linear-gradient(90deg, #0a1929, #1e3a5f); 
            padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin:0;'>🔬 RISC-V Register Verifier - Team Alpha</h1>
    <p style='color: #ffd700; margin:5px 0 0 0;'>
        Данные обновлены: {data.get('last_update', 'Неизвестно')}
    </p>
</div>
""", unsafe_allow_html=True)

# Метрики в три колонки
col1, col2, col3 = st.columns(3)

with col1:
    coverage = data.get('coverage', 0)
    st.metric(
        label="📊 Register Coverage",
        value=f"{coverage}%",
        delta=f"{94 - coverage}% до цели"
    )
    st.progress(coverage / 100)

with col2:
    bugs = data.get('bugs_found', 0)
    st.metric(
        label="🐞 Bugs Found",
        value=f"{bugs}/3",
        delta=f"{3 - bugs} осталось"
    )
    st.progress(bugs / 3)

with col3:
    pylint = data.get('pylint_score', 0)
    st.metric(
        label="📝 Pylint Score",
        value=f"{pylint}/10",
        delta=f"{8.5 - pylint:.1f} до цели"
    )
    st.progress(pylint / 10)

# Дополнительная информация
st.divider()

col4, col5 = st.columns(2)

with col4:
    st.metric(
        "✅ Пройдено тестов",
        f"{data.get('tests_passed', 0)}/{data.get('tests_total', 200)}"
    )

with col5:
    # Кнопка обновления
    if st.button("🔄 Обновить данные", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Информация о файле данных
with st.expander("📁 Просмотр данных из results.json"):
    st.json(data)
    st.caption(f"Путь к файлу: test_results/results.json")

# Команды для запуска
st.code("""
# Запуск тестов
pytest tests/ --cov

# Запуск дашборда
streamlit run dashboard.py
""", language="bash")

# Футер
st.divider()
st.caption("""
**Метрики YADRO:** Register Coverage ≥94% | Bugs Found: 3/3 | Pylint ≥8.5/10  
**Team Alpha:** Данные берутся из test_results/results.json
""")