import streamlit as st
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
import random


# ============================================
# ФУНКЦИЯ ДЛЯ ОТРИСОВКИ МАТРИЦЫ ПОКРЫТИЯ 10×32
# ============================================
def draw_coverage_matrix(matrix_data):
    """
    Рисует матрицу покрытия 10×32
    0 - красный квадрат (не покрыто)
    1 - зеленый квадрат (покрыто)
    """
    # Создаем тепловую карту с кастомными цветами
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        colorscale=[
            [0, '#ff4d4d'],  # красный для 0
            [1, '#4CAF50']  # зеленый для 1
        ],
        showscale=False,  # не показывать цветовую шкалу
        xgap=2,  # промежутки между ячейками
        ygap=2,
        hovertext=[[
                       f'Row {i}, Col {j}<br>Value: {matrix_data[i][j]}<br>{"✅ Covered" if matrix_data[i][j] == 1 else "❌ Not Covered"}'
                       for j in range(len(matrix_data[0]))] for i in range(len(matrix_data))],
        hoverinfo='text'
    ))

    # Настройка внешнего вида
    fig.update_layout(
        title="📊 Coverage Matrix 10×32",
        xaxis=dict(
            title="Bit Position (0-31)",
            tickmode='linear',
            tick0=0,
            dtick=1,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Register (0-9)",
            tickmode='linear',
            tick0=0,
            dtick=1,
            tickfont=dict(size=10),
            autorange='reversed'  # чтобы 0 был сверху
        ),
        height=400,
        width=800,
        plot_bgcolor='white'
    )

    # Добавляем линии сетки для лучшей читаемости
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    return fig


# ============================================
# ФУНКЦИЯ ДЛЯ ЧТЕНИЯ МАТРИЦЫ ИЗ ФАЙЛА КАПИТАНА
# ============================================
def get_captain_matrix():
    """
    Читает файл toggle_report.txt и преобразует его в матрицу 10x32.
    """
    file_path = 'toggle_report.txt'
    matrix = []

    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            st.warning(f"⚠️ Файл {file_path} не найден в корневой папке проекта.")
            return None

        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f):
                # Разделяем строку на числа по пробелам
                parts = line.strip().split()
                # Преобразуем каждую часть в целое число
                row = [int(x) for x in parts]

                # Проверяем, что в строке ровно 32 числа
                if len(row) == 32:
                    matrix.append(row)
                else:
                    st.warning(f"⚠️ Строка {line_num + 1}: ожидалось 32 элемента, получено {len(row)}. Пропущена.")

        # Проверяем, что получили 10 строк
        if len(matrix) == 10:
            st.success("✅ Матрица покрытия 10x32 успешно загружена из toggle_report.txt")
            return matrix
        else:
            st.warning(f"⚠️ Ожидалось 10 строк, получено {len(matrix)}. Проверьте файл.")
            return None

    except Exception as e:
        st.error(f"❌ Ошибка при чтении файла: {e}")
        return None


# Функция для расчета процента покрытия
def calculate_coverage_percentage(matrix):
    """Считает процент единиц в матрице"""
    total = len(matrix) * len(matrix[0])
    covered = sum(sum(row) for row in matrix)
    return (covered / total) * 100

# ============================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================
st.set_page_config(
    page_title="RISC-V Verifier | Team Alpha",
    page_icon="🔬",
    layout="wide"
)


# ============================================
# ФУНКЦИЯ ЗАГРУЗКИ ДАННЫХ
# ============================================
@st.cache_data(ttl=5)
def load_results():
    """Загружает данные из test_results/results.json"""
    file_path = 'test_results/results.json'

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                mod_time = os.path.getmtime(file_path)
                data['file_modified'] = datetime.fromtimestamp(mod_time).strftime('%H:%M:%S')
                return data
        except Exception as e:
            st.error(f"Ошибка чтения файла: {e}")
            return get_default_data()
    else:
        return get_default_data()


def get_default_data():
    """Возвращает данные по умолчанию"""
    return {
        "coverage": 25,
        "bugs_found": 0,
        "pylint_score": 7.5,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests_passed": 156,
        "tests_total": 200,
        "file_modified": "Файл не найден",
        "register_stats": {
            "0x0042": 156,
            "0x0013": 89,
            "0x0077": 45,
            "0x1000": 23,
            "0x1004": 67,
            "0x1008": 34
        },
        "transaction_log": []
    }


# ============================================
# ФУНКЦИЯ ДЛЯ ОТРИСОВКИ TIMELINE
# ============================================
def draw_transaction_timeline(transactions):
    """Рисует интерактивную временную шкалу транзакций"""
    if not transactions:
        return None

    df_timeline = pd.DataFrame(transactions)

    # Создаем временные метки
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    df_timeline['Start'] = df_timeline['time'].apply(
        lambda t: (base_time + timedelta(seconds=float(t))).strftime('%Y-%m-%d %H:%M:%S')
    )
    df_timeline['Finish'] = df_timeline.apply(
        lambda row: (base_time + timedelta(seconds=float(row['time']) + float(row.get('duration', 0.05)))).strftime(
            '%Y-%m-%d %H:%M:%S'),
        axis=1
    )

    # Определяем цвета
    color_map = {
        'READ': '#2E86AB',
        'WRITE': '#A23B72',
        'CPU': '#F18F01',
        'DMA': '#C73E1D'
    }

    # Создаем timeline
    fig = px.timeline(
        df_timeline,
        x_start="Start",
        x_end="Finish",
        y="component",
        color="operation",
        hover_data={
            'address': True,
            'value': True,
            'time': ':.2f'
        },
        color_discrete_map=color_map,
        title="📊 Transaction Timeline (как в профессиональных тулах)"
    )

    fig.update_layout(
        height=500,
        showlegend=True,
        hoverlabel=dict(bgcolor="white", font_size=12)
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickformat="%H:%M:%S", tickangle=45)

    # Добавляем маркеры для бажных адресов
    bug_addresses = ['0x0042', '0x0013', '0x0077']
    for i, row in df_timeline.iterrows():
        if row['address'] in bug_addresses:
            fig.add_vline(
                x=row['Start'],
                line_width=2,
                line_dash="dash",
                line_color="red",
                opacity=0.5
            )

    return fig


# ============================================
# ЗАГРУЗКА ДАННЫХ
# ============================================
data = load_results()

# ============================================
# ЗАГОЛОВОК
# ============================================
st.markdown(f"""
<div style='background: linear-gradient(90deg, #0a1929, #1e3a5f); 
            padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin:0;'>🔬 RISC-V Register Verifier - Team Alpha</h1>
    <p style='color: #ffd700; margin:5px 0 0 0;'>
        Данные обновлены: {data.get('last_update', 'Неизвестно')}
    </p>
    <p style='color: #aaa; font-size: 0.8em; margin:5px 0 0 0;'>
        Файл изменен: {data.get('file_modified', 'Нет данных')}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# МЕТРИКИ (ИСПРАВЛЕННЫЕ)
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    coverage = data.get('coverage', 0)
    st.metric(
        label="📊 Register Coverage",
        value=f"{coverage}%",
        delta=f"{94 - coverage}% до цели"
    )
    # ИСПРАВЛЕНО: защита от значений > 1.0
    st.progress(min(coverage / 100, 1.0))
    st.caption(f"Цель: 94%")

with col2:
    bugs = data.get('bugs_found', 0)
    delta_bugs = bugs - 3 if bugs > 3 else 3 - bugs
    delta_text = f"{delta_bugs} от цели" if bugs > 3 else f"{delta_bugs} осталось"

    st.metric(
        label="🐞 Bugs Found",
        value=f"{bugs}/3",
        delta=delta_text
    )
    # ИСПРАВЛЕНО: специальная обработка для багов > 3
    if bugs >= 3:
        st.progress(1.0)
        if bugs > 3:
            st.caption(f"🎉 УРА! Найдено {bugs} багов (больше чем в спецификации!)")
        else:
            st.caption(f"✅ Все 3 бага найдены!")
    else:
        st.progress(bugs / 3)
        st.caption(f"🔍 Найдено {bugs} из 3")

with col3:
    pylint = data.get('pylint_score', 0)
    st.metric(
        label="📝 Pylint Score",
        value=f"{pylint}/10",
        delta=f"{8.5 - pylint:.1f} до цели"
    )
    # ИСПРАВЛЕНО: защита от значений > 1.0
    st.progress(min(pylint / 10, 1.0))
    if pylint >= 8.5:
        st.caption("✅ Цель достигнута")
    else:
        st.caption(f"🎯 Нужно еще {8.5 - pylint:.1f}")

with col4:
    tests_passed = data.get('tests_passed', 0)
    tests_total = data.get('tests_total', 200)
    tests_percent = (tests_passed / tests_total) * 100
    st.metric(
        label="✅ Tests Passed",
        value=f"{tests_passed}/{tests_total}",
        delta=f"{tests_percent:.0f}%"
    )
    # ИСПРАВЛЕНО: защита от значений > 1.0
    st.progress(min(tests_passed / tests_total, 1.0))
    st.caption(f"Прогресс: {tests_percent:.0f}%")

# ============================================
# ВКЛАДКИ (ДОБАВЛЯЕМ ПЯТУЮ - Coverage Matrix)
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Coverage Metrics",
    "🔥 Register Heatmap",
    "🔄 FSM Graph",
    "⏱️ Transaction Timeline",
    "🔲 Coverage Matrix"  # НОВАЯ ВКЛАДКА
])

with tab1:
    # Весь код, который уже был внутри первой вкладки (НИЧЕГО НЕ МЕНЯЕМ)
    st.subheader("📊 Детальные метрики покрытия")
    # ... остальной твой код ...

with tab2:
    # Весь код, который уже был внутри второй вкладки (НИЧЕГО НЕ МЕНЯЕМ)
    st.subheader("🔥 Register Access Heatmap")
    # ... остальной твой код ...

with tab3:
    # Весь код, который уже был внутри третьей вкладки (НИЧЕГО НЕ МЕНЯЕМ)
    st.subheader("🔄 FSM State Graph")
    # ... остальной твой код ...

with tab4:
    # Весь код, который уже был внутри четвертой вкладки (НИЧЕГО НЕ МЕНЯЕМ)
    st.subheader("⏱️ Transaction Timeline")
    # ... остальной твой код ...

with tab5:
    st.subheader("🔲 Bit Coverage Matrix 10×32")
    st.caption("Зеленый = бит покрыт, Красный = бит не покрыт")

    # ЗАГРУЖАЕМ МАТРИЦУ ИЗ ФАЙЛА КАПИТАНА
    captain_matrix = get_captain_matrix()

    if captain_matrix is None:
        st.info("ℹ️ Использую демо-данные для примера.")
        # Создаем демо-матрицу (8 зеленых, остальное красное в первой строке)
        demo_matrix = [[1] * 8 + [0] * 24] + [[1] * 32 for _ in range(9)]
        fig_matrix = draw_coverage_matrix(demo_matrix)
        st.plotly_chart(fig_matrix, use_container_width=True)

        coverage_pct = calculate_coverage_percentage(demo_matrix)
        st.metric("Демо-покрытие битов", f"{coverage_pct:.1f}%")

    else:
        # ОТРИСОВЫВАЕМ РЕАЛЬНУЮ МАТРИЦУ
        fig_matrix = draw_coverage_matrix(captain_matrix)
        st.plotly_chart(fig_matrix, use_container_width=True)

        coverage_pct = calculate_coverage_percentage(captain_matrix)
        st.metric("Текущее покрытие битов", f"{coverage_pct:.1f}%")

        # Целевое покрытие 94%
        if coverage_pct >= 94:
            st.success("✅ Цель YADRO достигнута! Покрытие ≥94%")
        else:
            st.warning(f"🎯 Нужно еще {94 - coverage_pct:.1f}% до цели YADRO")

        # Покажем немного статистики
        with st.expander("📊 Статистика покрытия"):
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.write("**По строкам (регистрам):**")
                for i, row in enumerate(captain_matrix):
                    row_cov = sum(row) / 32 * 100
                    st.write(f"Register {i}: {row_cov:.0f}%")
            with col_stat2:
                st.write("**По столбцам (битам):**")
                # Покажем первые 8 бит для примера
                for j in range(8):
                    col_cov = sum(row[j] for row in captain_matrix) / 10 * 100
                    st.write(f"Bit {j}: {col_cov:.0f}%")

# ============================================
# ИНСТРУКЦИЯ ДЛЯ КОМАНДЫ
# ============================================
st.divider()
with st.expander("📋 Инструкция для команды", expanded=False):
    st.markdown("""
    ### 📁 Как обновлять данные
    1. **Запусти тесты:** `pytest tests/ --cov`
    2. **Запусти скрипт:** `python generate_results.py`
    3. **Введи количество найденных багов** (можно любое число!)
    4. **Дашборд обновится автоматически** через 10 секунд

    ### 📊 Метрики YADRO
    - **Register Coverage**: ≥94%
    - **Bugs Found**: 3/3 (можно больше!)
    - **Pylint Score**: ≥8.5/10

    ### 🎯 Наша цель
    Достичь всех метрик и найти как можно больше багов!
    """)

# ============================================
# СТАТУС ФАЙЛА И КНОПКА ОБНОВЛЕНИЯ
# ============================================
st.divider()
col_status, col_button = st.columns([3, 1])

with col_status:
    if os.path.exists('test_results/results.json'):
        file_size = os.path.getsize('test_results/results.json')
        mod_time = os.path.getmtime('test_results/results.json')
        mod_time_str = datetime.fromtimestamp(mod_time).strftime('%H:%M:%S')
        st.success(f"✅ Файл results.json существует (размер: {file_size} байт, изменен: {mod_time_str})")
    else:
        st.error("❌ Файл results.json не найден. Запустите generate_results.py")

with col_button:
    if st.button("🔄 Принудительно обновить", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================
# ФУТЕР
# ============================================
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 10px;'>
    <p>🔬 RISC-V Register Verifier - Team Alpha | МИФИ-Ядро | YADRO Methodology</p>
    <p style='font-size: 0.8em;'>Автообновление каждые 10 секунд | Баги могут быть любым числом!</p>
</div>
""", unsafe_allow_html=True)