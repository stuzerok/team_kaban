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
# ВКЛАДКИ
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Coverage Metrics",
    "🔥 Register Heatmap",
    "🔄 FSM Graph",
    "⏱️ Transaction Timeline"
])

with tab1:
    st.subheader("📊 Детальные метрики покрытия")

    col_detail1, col_detail2 = st.columns(2)

    with col_detail1:
        st.metric("Покрытие регистров", f"{data.get('coverage', 0)}%")
        st.metric("Pylint оценка", f"{data.get('pylint_score', 0)}/10")

        # Дополнительные метрики
        bugs_detailed = data.get('bugs_detailed', {})
        if bugs_detailed:
            st.write("**Детализация багов:**")
            for bug_type, count in bugs_detailed.items():
                if count > 0:
                    st.write(f"- {bug_type}: {count}")

    with col_detail2:
        st.metric("Найдено багов", f"{data.get('bugs_found', 0)}")
        st.metric("Пройдено тестов", f"{data.get('tests_passed', 0)}/{data.get('tests_total', 200)}")

        # Прогресс к цели YADRO
        st.write("**Прогресс к цели YADRO:**")
        yadro_progress = min(
            (data.get('coverage', 0) / 94) * 0.4 +
            (min(data.get('bugs_found', 0), 3) / 3) * 0.3 +
            (min(data.get('pylint_score', 0), 8.5) / 8.5) * 0.3,
            1.0
        )
        st.progress(yadro_progress)
        st.caption(f"Общий прогресс: {yadro_progress * 100:.0f}%")

with tab2:
    st.subheader("🔥 Register Access Heatmap")
    st.caption("Частота обращений к регистрам")

    register_stats = data.get('register_stats', {})
    if register_stats:
        df_heatmap = pd.DataFrame([
            {'address': addr, 'count': count}
            for addr, count in register_stats.items()
        ])

        if not df_heatmap.empty:
            fig = go.Figure(data=go.Heatmap(
                z=[df_heatmap['count'].values],
                x=df_heatmap['address'],
                colorscale='Viridis',
                text=[df_heatmap['count'].values],
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='<b>Address: %{x}</b><br>Accesses: %{z}<extra></extra>'
            ))
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                xaxis_title="Register Address",
                yaxis_showticklabels=False
            )
            st.plotly_chart(fig, use_container_width=True)

            # Топ активных регистров
            st.subheader("📊 Топ-5 самых активных регистров")
            top_regs = df_heatmap.nlargest(5, 'count')
            for i, (_, row) in enumerate(top_regs.iterrows(), 1):
                if row['address'] in ['0x0042', '0x0013', '0x0077']:
                    st.markdown(f"**{i}. {row['address']}** — 🔴 {row['count']} обращений (бажный адрес)")
                else:
                    st.markdown(f"{i}. {row['address']} — {row['count']} обращений")
    else:
        st.info("Нет данных о регистрах для отображения")

with tab3:
    st.subheader("🔄 FSM State Graph")
    st.caption("Граф состояний конечного автомата")

    # Создаем граф
    G = nx.DiGraph()
    states = ['IDLE', 'READ', 'WRITE', 'WAIT', 'DEADLOCK', 'STALE']
    for state in states:
        G.add_node(state)

    transitions = [
        ('IDLE', 'READ'), ('IDLE', 'WRITE'),
        ('READ', 'WAIT'), ('WRITE', 'WAIT'),
        ('WAIT', 'IDLE'), ('READ', 'STALE'),
        ('WRITE', 'DEADLOCK'), ('DEADLOCK', 'IDLE'),
        ('STALE', 'READ')
    ]

    for src, dst in transitions:
        G.add_edge(src, dst)

    # Определяем текущее состояние по количеству багов
    bugs_count = data.get('bugs_found', 0)
    if bugs_count == 0:
        current_state = 'IDLE'
    elif bugs_count == 1:
        current_state = 'STALE'
    elif bugs_count == 2:
        current_state = 'DEADLOCK'
    else:
        current_state = 'WAIT'

    pos = nx.spring_layout(G, k=2, seed=42)

    # Рисуем рёбра
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=1, color='#888'),
            mode='lines',
            hoverinfo='none'
        ))

    # Рисуем узлы
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_colors = ['red' if node == current_state else 'lightblue' for node in G.nodes()]
    node_sizes = [40 if node == current_state else 30 for node in G.nodes()]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='black')
        ),
        text=list(G.nodes()),
        textposition="top center",
        hoverinfo='text',
        hovertext=[f"State: {node}" for node in G.nodes()]
    )

    fig_fsm = go.Figure(
        data=edge_trace + [node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=450,
            title=f"Текущее состояние: **{current_state}** (багов: {bugs_count})"
        )
    )

    st.plotly_chart(fig_fsm, use_container_width=True)

    with st.expander("ℹ️ Что означают состояния FSM"):
        st.markdown("""
        | Состояние | Описание |
        |-----------|----------|
        | **IDLE** | Шина свободна, ожидание команд |
        | **READ** | Выполняется чтение из регистра |
        | **WRITE** | Выполняется запись в регистр |
        | **WAIT** | Ожидание подтверждения от памяти |
        | **DEADLOCK** | 🔴 Взаимоблокировка (баг #2) |
        | **STALE** | 🟡 Устаревшие данные (баг #1) |
        """)

with tab4:
    st.subheader("⏱️ Transaction Timeline")
    st.caption("Интерактивная временная шкала транзакций (как в профессиональных инструментах)")

    transactions = data.get('transaction_log', [])
    if transactions:
        fig_timeline = draw_transaction_timeline(transactions)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)

            with st.expander("ℹ️ Как читать Timeline"):
                st.markdown("""
                - **READ** (синий): операция чтения из регистра
                - **WRITE** (фиолетовый): операция записи в регистр
                - **Красные пунктирные линии**: транзакции с бажными адресами (0x42, 0x13, 0x77)
                - **Длительность полосы**: время выполнения операции

                Это аналог профессиональных инструментов отладки System-on-Chip (ProtoLens).
                """)

            # Фильтры
            st.subheader("🔍 Фильтры")
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                show_read = st.checkbox("Показать READ", value=True)
            with col_f2:
                show_write = st.checkbox("Показать WRITE", value=True)
            with col_f3:
                show_bugs_only = st.checkbox("Только бажные адреса", value=False)

            # Применяем фильтры
            filtered_transactions = []
            for t in transactions:
                addr = t.get('address', '')
                op = t.get('operation', '')

                if show_bugs_only and addr not in ['0x0042', '0x0013', '0x0077']:
                    continue
                if not show_read and op == 'READ':
                    continue
                if not show_write and op == 'WRITE':
                    continue
                filtered_transactions.append(t)

            if filtered_transactions and len(filtered_transactions) != len(transactions):
                st.info(f"Показано {len(filtered_transactions)} из {len(transactions)} транзакций")
                fig_filtered = draw_transaction_timeline(filtered_transactions)
                if fig_filtered:
                    st.plotly_chart(fig_filtered, use_container_width=True)
    else:
        st.info("Нет данных о транзакциях. Запустите generate_results.py для сбора данных.")

        # Демо-кнопка для создания тестовых данных
        if st.button("🎲 Создать демо-данные для Timeline"):
            demo_transactions = []
            for i in range(20):
                addr = random.choice([0x42, 0x13, 0x77, 0x1000, 0x2000])
                demo_transactions.append({
                    'time': i * 0.2,
                    'operation': random.choice(['READ', 'WRITE']),
                    'address': f'0x{addr:04X}',
                    'value': f'0x{random.randint(0, 0xFFFFFFFF):08X}',
                    'component': random.choice(['CPU', 'DMA']),
                    'duration': 0.1 if addr in [0x42, 0x13, 0x77] else 0.05
                })
            data['transaction_log'] = demo_transactions
            st.rerun()

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