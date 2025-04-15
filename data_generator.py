# Импортируем необходимые библиотеки
import pandas as pd  # для работы с табличными данными
import numpy as np   # для математических операций
from datetime import datetime, timedelta  # для работы с датами

def generate_medical_data(n_regions=50, days=365):
    """
    Генерирует синтетические данные о медицинских показателях по регионам.
    
    Параметры:
    ----------
    n_regions : int, по умолчанию 50
        Количество регионов для генерации данных
    days : int, по умолчанию 365
        Количество дней для генерации данных
    
    Возвращает:
    -----------
    pandas.DataFrame
        Датафрейм с сгенерированными данными, содержащий следующие колонки:
        - date: дата наблюдения
        - region_id: идентификатор региона
        - population: численность населения
        - medical_facilities: количество медучреждений
        - medical_staff: количество медицинского персонала
        - vaccination_rate: процент вакцинированных
        - awareness_index: индекс информированности населения
        - accessibility_score: оценка доступности медпомощи
        - income_level: уровень дохода населения
        - education_level: уровень образования
        - urbanization: уровень урбанизации
        - elderly_population: доля пожилого населения
    """
    
    # Создаем список дат
    dates = pd.date_range(
        start=datetime(2023, 1, 1),  # начальная дата
        periods=days,                 # количество дней
        freq='D'                      # дневная частота
    )
    
    # Создаем базовые характеристики регионов
    regions = pd.DataFrame({
        'region_id': range(1, n_regions + 1),
        # Генерируем население (от 100,000 до 5,000,000)
        'base_population': np.random.uniform(100000, 5000000, n_regions),
        # Генерируем базовый уровень медучреждений (от 10 до 100 на 100,000 населения)
        'base_medical_facilities': np.random.uniform(10, 100, n_regions),
        # Генерируем базовый уровень урбанизации (от 0.2 до 0.9)
        'base_urbanization': np.random.uniform(0.2, 0.9, n_regions),
        # Генерируем базовый уровень образования (от 0.4 до 0.9)
        'base_education_level': np.random.uniform(0.4, 0.9, n_regions),
        # Генерируем базовый уровень дохода (от 20,000 до 100,000)
        'base_income_level': np.random.uniform(20000, 100000, n_regions)
    })
    
    # Создаем пустой список для хранения данных
    data = []
    
    # Генерируем данные для каждой даты и региона
    for date in dates:
        for _, region in regions.iterrows():
            # Добавляем случайные колебания к базовым значениям
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * date.dayofyear / 365)
            
            # Рассчитываем показатели с учетом сезонности и случайных колебаний
            population = region['base_population'] * (1 + np.random.normal(0, 0.001))
            medical_facilities = region['base_medical_facilities'] * seasonal_factor
            urbanization = region['base_urbanization'] + np.random.normal(0, 0.01)
            education_level = region['base_education_level'] + np.random.normal(0, 0.01)
            income_level = region['base_income_level'] * seasonal_factor
            
            # Рассчитываем производные показатели
            medical_staff = medical_facilities * np.random.uniform(5, 15)  # персонал на учреждение
            elderly_population = np.random.uniform(0.1, 0.3)  # доля пожилых
            
            # Рассчитываем индекс информированности (зависит от образования и урбанизации)
            awareness_index = (education_level * 0.6 + urbanization * 0.4) + np.random.normal(0, 0.05)
            
            # Рассчитываем оценку доступности (зависит от количества учреждений и урбанизации)
            accessibility_score = (
                medical_facilities / population * 100000 * 0.7 +
                urbanization * 0.3
            ) + np.random.normal(0, 0.05)
            
            # Рассчитываем процент вакцинации (зависит от многих факторов)
            base_vaccination = (
                awareness_index * 0.3 +
                accessibility_score * 0.3 +
                education_level * 0.2 +
                (income_level / 100000) * 0.2
            )
            vaccination_rate = np.clip(base_vaccination * 100, 0, 100)
            
            # Добавляем строку в данные
            data.append({
                'date': date,
                'region_id': region['region_id'],
                'population': int(population),
                'medical_facilities': int(medical_facilities),
                'medical_staff': int(medical_staff),
                'vaccination_rate': round(vaccination_rate, 2),
                'awareness_index': round(awareness_index, 3),
                'accessibility_score': round(accessibility_score, 3),
                'income_level': round(income_level, 2),
                'education_level': round(education_level, 3),
                'urbanization': round(urbanization, 3),
                'elderly_population': round(elderly_population, 3)
            })
    
    # Создаем датафрейм из собранных данных
    df = pd.DataFrame(data)
    
    # Сортируем данные по дате и региону
    df = df.sort_values(['date', 'region_id']).reset_index(drop=True)
    
    return df

# Если скрипт запущен напрямую, генерируем тестовый набор данных
if __name__ == '__main__':
    # Генерируем данные
    df = generate_medical_data(n_regions=10, days=30)
    
    # Выводим информацию о датафрейме
    print("\nРазмерность датафрейма:", df.shape)
    print("\nПример данных:")
    print(df.head())
    
    # Выводим базовую статистику
    print("\nСтатистика по числовым показателям:")
    print(df.describe()) 