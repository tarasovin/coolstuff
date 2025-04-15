# Импортируем необходимые библиотеки
import streamlit as st              # библиотека для создания веб-приложения
import pandas as pd                 # библиотека для работы с табличными данными
import numpy as np                  # библиотека для математических операций
import plotly.express as px        # библиотека для создания интерактивных графиков
import plotly.graph_objects as go  # расширенные возможности plotly
from datetime import datetime, timedelta  # для работы с датами
from sklearn.cluster import KMeans  # для кластерного анализа
from sklearn.preprocessing import StandardScaler  # для стандартизации данных
from data_generator import generate_medical_data  # наш генератор данных

# Настраиваем страницу
st.set_page_config(
    page_title="Анализ медицинских данных",  # заголовок вкладки
    page_icon="🏥",                          # иконка вкладки
    layout="wide"                           # широкий layout
)

# Функция для загрузки данных
@st.cache_data  # кэшируем данные, чтобы не генерировать их каждый раз
def load_data():
    """
    Загружает и подготавливает данные для анализа.
    
    Returns:
    --------
    pd.DataFrame
        Подготовленный датафрейм с данными
    """
    # Генерируем данные
    df = generate_medical_data(n_regions=50, days=365)
    return df

# Загружаем данные
df = load_data()

# Создаем заголовок
st.title("🏥 Анализ факторов в здравоохранении")

# Добавляем описание
st.markdown("""
    Этот дашборд демонстрирует анализ различных факторов, влияющих на показатели в здравоохранении.
    Используются методы визуализации, статистического анализа и машинного обучения для выявления
    значимых зависимостей и паттернов в данных.
""")

# Создаем боковую панель с фильтрами
st.sidebar.header("📊 Параметры анализа")

# Выбор регионов
selected_regions = st.sidebar.multiselect(
    "Выберите регионы:",  # заголовок селектора
    options=sorted(df['region_id'].unique()),  # список регионов
    default=sorted(df['region_id'].unique())[:5]  # по умолчанию первые 5 регионов
)

# Выбор периода анализа
date_range = st.sidebar.date_input(
    "Выберите период:",  # заголовок виджета
    value=(  # значения по умолчанию
        df['date'].min().date(),
        df['date'].max().date()
    ),
    min_value=df['date'].min().date(),  # минимальная дата
    max_value=df['date'].max().date()   # максимальная дата
)

# Фильтруем данные
mask = (
    (df['region_id'].isin(selected_regions)) &
    (df['date'].dt.date >= date_range[0]) &
    (df['date'].dt.date <= date_range[1])
)
filtered_df = df[mask]

# Создаем вкладки
tab1, tab2, tab3 = st.tabs([
    "📈 Временной анализ",
    "🔍 Корреляции",
    "📊 Кластерный анализ"
])

# Вкладка временного анализа
with tab1:
    st.header("📈 Анализ временных рядов")
    
    # Выбор показателя для анализа
    metric = st.selectbox(
        "Выберите показатель для анализа:",
        options=[
            'vaccination_rate', 'medical_facilities', 'medical_staff',
            'awareness_index', 'accessibility_score'
        ],
        format_func=lambda x: {
            'vaccination_rate': 'Процент вакцинации',
            'medical_facilities': 'Количество медучреждений',
            'medical_staff': 'Медицинский персонал',
            'awareness_index': 'Индекс информированности',
            'accessibility_score': 'Оценка доступности'
        }[x]
    )
    
    # График временного ряда
    st.subheader("Динамика показателя во времени")
    st.markdown("""
        График показывает изменение выбранного показателя с течением времени для каждого региона.
        
        **Как читать график:**
        - Каждая линия представляет отдельный регион
        - По оси X отложены даты
        - По оси Y - значение выбранного показателя
        
        **Что анализировать:**
        - Общие тренды
        - Сезонные колебания
        - Различия между регионами
        - Аномальные значения
    """)
    
    fig = px.line(
        filtered_df,
        x='date',
        y=metric,
        color='region_id',
        title=f"Динамика показателя по регионам"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Статистика по регионам
    st.subheader("Статистика по регионам")
    st.markdown("""
        Таблица показывает основные статистические показатели для каждого региона.
        
        **Как читать таблицу:**
        - mean: среднее значение
        - std: стандартное отклонение (разброс значений)
        - min/max: минимальное и максимальное значения
    """)
    
    stats_df = filtered_df.groupby('region_id')[metric].agg([
        'mean', 'std', 'min', 'max'
    ]).round(2)
    st.dataframe(stats_df)

# Вкладка корреляций
with tab2:
    st.header("🔍 Корреляционный анализ")
    
    # Выбираем числовые колонки для корреляции
    numeric_cols = [
        'vaccination_rate', 'medical_facilities', 'medical_staff',
        'awareness_index', 'accessibility_score', 'income_level',
        'education_level', 'urbanization', 'elderly_population'
    ]
    
    # Создаем корреляционную матрицу
    st.subheader("Корреляционная матрица")
    st.markdown("""
        Тепловая карта показывает силу взаимосвязи между различными показателями.
        
        **Как читать матрицу:**
        - Цвет ячейки показывает силу корреляции:
          - Красный → сильная положительная корреляция (+1)
          - Синий → сильная отрицательная корреляция (-1)
          - Светлые оттенки → слабая корреляция (близко к 0)
        
        **Что анализировать:**
        - Сильные положительные и отрицательные корреляции
        - Группы связанных показателей
        - Независимые показатели
    """)
    
    corr_matrix = filtered_df[numeric_cols].corr()
    fig = px.imshow(
        corr_matrix,
        title="Корреляция между показателями",
        color_continuous_scale='RdBu_r',  # красно-синяя шкала
        zmin=-1,  # минимальное значение корреляции
        zmax=1    # максимальное значение корреляции
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # График рассеяния
    st.subheader("График рассеяния")
    st.markdown("""
        График показывает взаимосвязь между двумя выбранными показателями.
        
        **Как читать график:**
        - Каждая точка представляет наблюдение
        - Цвет точки показывает регион
        - Линия тренда показывает общую тенденцию
        
        **Что анализировать:**
        - Форму зависимости (линейная/нелинейная)
        - Силу связи (разброс точек)
        - Выбросы и аномалии
    """)
    
    # Выбор показателей для графика рассеяния
    col1, col2 = st.columns(2)
    with col1:
        x_metric = st.selectbox(
            "Показатель по оси X:",
            options=numeric_cols,
            key='x_axis'
        )
    with col2:
        # Исключаем уже выбранный показатель из списка для оси Y
        y_options = [col for col in numeric_cols if col != x_metric]
        y_metric = st.selectbox(
            "Показатель по оси Y:",
            options=y_options,
            key='y_axis'
        )
    
    # Создаем словарь для перевода названий показателей
    metric_labels = {
        'vaccination_rate': 'Процент вакцинации',
        'medical_facilities': 'Количество медучреждений',
        'medical_staff': 'Медицинский персонал',
        'awareness_index': 'Индекс информированности',
        'accessibility_score': 'Оценка доступности',
        'income_level': 'Уровень дохода',
        'education_level': 'Уровень образования',
        'urbanization': 'Уровень урбанизации',
        'elderly_population': 'Доля пожилого населения'
    }
    
    fig = px.scatter(
        filtered_df,
        x=x_metric,
        y=y_metric,
        color='region_id',
        trendline="ols",  # добавляем линию тренда
        title=f"Зависимость: {metric_labels[y_metric]} от {metric_labels[x_metric]}",
        labels={
            x_metric: metric_labels[x_metric],
            y_metric: metric_labels[y_metric],
            'region_id': 'Регион'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# Вкладка кластерного анализа
with tab3:
    st.header("📊 Кластерный анализ")
    st.markdown("""
        Кластерный анализ помогает выявить группы регионов с похожими характеристиками.
        
        **Как это работает:**
        1. Выберите показатели для кластеризации
        2. Укажите желаемое количество кластеров
        3. Алгоритм K-means разделит регионы на группы
        
        **Что анализировать:**
        - Характеристики каждого кластера
        - Размеры кластеров
        - Различия между кластерами
    """)
    
    # Выбор показателей для кластеризации
    cluster_features = st.multiselect(
        "Выберите показатели для кластеризации:",
        options=numeric_cols,
        default=['vaccination_rate', 'accessibility_score', 'income_level']
    )
    
    if cluster_features:
        # Подготавливаем данные для кластеризации
        # Берем последние значения для каждого региона
        cluster_data = filtered_df.groupby('region_id')[cluster_features].mean()
        
        # Определяем максимальное возможное количество кластеров
        max_clusters = min(10, len(cluster_data))
        
        if max_clusters < 2:
            st.warning("⚠️ Выберите как минимум 2 региона для проведения кластерного анализа.")
        else:
            # Выбор количества кластеров
            n_clusters = st.slider(
                "Количество кластеров:",
                min_value=2,
                max_value=max_clusters,
                value=min(3, max_clusters)
            )
            
            # Стандартизируем данные
            scaler = StandardScaler()
            cluster_data_scaled = scaler.fit_transform(cluster_data)
            
            # Выполняем кластеризацию
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(cluster_data_scaled)
            
            # Добавляем метки кластеров к данным
            cluster_data['Cluster'] = clusters
            
            # Визуализируем результаты
            if len(cluster_features) >= 2:
                st.subheader("Визуализация кластеров")
                st.markdown("""
                    График показывает распределение регионов по кластерам в пространстве выбранных показателей.
                    
                    **Как читать график:**
                    - Каждая точка - отдельный регион
                    - Цвет точки показывает принадлежность к кластеру
                    - Положение точки определяется значениями выбранных показателей
                    - При наведении на точку отображаются точные значения показателей
                    - Размер точки отражает численность населения региона
                    
                    **Что анализировать:**
                    - Группы похожих регионов (кластеры одного цвета)
                    - Насколько четко разделены кластеры
                    - Есть ли выбросы (точки, далекие от своего кластера)
                    - Как связаны различные показатели между собой
                """)
                
                # Добавляем информацию о населении для размера точек
                cluster_data_with_pop = cluster_data.copy()
                cluster_data_with_pop['population'] = filtered_df.groupby('region_id')['population'].mean()
                
                # Создаем более информативные подписи для точек
                hover_data = {
                    'region_id': True,  # Показываем ID региона
                    'population': True,  # Показываем население
                }
                # Добавляем все выбранные показатели в hover_data
                for feature in cluster_features:
                    hover_data[feature] = ':.2f'  # Показываем с двумя знаками после запятой
                
                fig = px.scatter(
                    cluster_data_with_pop.reset_index(),
                    x=cluster_features[0],
                    y=cluster_features[1],
                    color='Cluster',
                    size='population',  # Размер точки зависит от населения
                    hover_data=hover_data,  # Данные при наведении
                    title="Распределение регионов по кластерам",
                    labels={
                        cluster_features[0]: metric_labels.get(cluster_features[0], cluster_features[0]),
                        cluster_features[1]: metric_labels.get(cluster_features[1], cluster_features[1]),
                        'Cluster': 'Кластер',
                        'population': 'Население'
                    },
                    color_continuous_scale='Viridis'  # Используем более контрастную цветовую схему
                )
                
                # Улучшаем внешний вид графика
                fig.update_traces(
                    marker=dict(
                        line=dict(width=1, color='white')  # Добавляем белую обводку точек
                    )
                )
                fig.update_layout(
                    plot_bgcolor='white',  # Белый фон
                    title_x=0.5,  # Центрируем заголовок
                    title_font_size=20,
                    showlegend=True,
                    legend_title_text='Кластер'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Добавляем описание кластеров
                st.subheader("Описание кластеров")
                
                # Рассчитываем средние значения и размеры кластеров
                cluster_descriptions = []
                for cluster_num in range(n_clusters):
                    cluster_mask = cluster_data['Cluster'] == cluster_num
                    cluster_size = cluster_mask.sum()
                    cluster_means = cluster_data[cluster_mask][cluster_features].mean()
                    
                    # Определяем особенности кластера
                    features_description = []
                    for feature in cluster_features:
                        mean_value = cluster_means[feature]
                        overall_mean = cluster_data[feature].mean()
                        diff_percent = ((mean_value - overall_mean) / overall_mean) * 100
                        
                        if abs(diff_percent) > 10:  # Если отличие более 10%
                            direction = "выше" if diff_percent > 0 else "ниже"
                            features_description.append(
                                f"{metric_labels.get(feature, feature)} {direction} среднего на {abs(diff_percent):.1f}%"
                            )
                    
                    # Формируем описание кластера
                    description = [
                        f"**Кластер {cluster_num}** (количество регионов: {cluster_size})",
                        "",
                        "Особенности кластера:"
                    ]
                    
                    if features_description:
                        description.extend([f"- {feat}" for feat in features_description])
                    else:
                        description.append("Нет явных отличий от средних значений")
                    
                    cluster_descriptions.append("\n".join(description))
                
                # Выводим описания кластеров в две колонки
                cols = st.columns(2)
                for i, desc in enumerate(cluster_descriptions):
                    cols[i % 2].markdown(desc)
            
            # Показываем характеристики кластеров
            st.subheader("Характеристики кластеров")
            st.markdown("""
                Таблица показывает средние значения показателей для каждого кластера.
                
                **Как читать таблицу:**
                - Строки - кластеры
                - Столбцы - средние значения показателей
                - Значения показывают типичные характеристики кластера
            """)
            
            cluster_stats = cluster_data.groupby('Cluster')[cluster_features].mean().round(2)
            st.dataframe(cluster_stats)

# Добавляем информацию о проекте
st.markdown("""
    ---
    ### 📚 О проекте
    
    Этот дашборд демонстрирует различные методы анализа данных:
    
    1. **Временной анализ**
       - Визуализация трендов
       - Анализ сезонности
       - Статистические показатели
    
    2. **Корреляционный анализ**
       - Матрица корреляций
       - Графики рассеяния
       - Линии тренда
    
    3. **Кластерный анализ**
       - Алгоритм K-means
       - Визуализация кластеров
       - Характеристики групп
""") 