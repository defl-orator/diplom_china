import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
# Импортируем загрузчик, функцию источника и словарь переводов
from china_config import load_data, add_source, COUNTRY_RU

df, col_arms, _, _ = load_data()

# Дополнительные колонки для "мягкой" безопасности
col_mil_visits = 'sec_03_military_engagement_ct'
col_exercises = 'sec_04_joint_exercise_ct'

if df is not None:
    # Если колонок нет в файле, создаем их и заполняем нулями
    for c in [col_mil_visits, col_exercises]:
        if c not in df.columns: df[c] = 0

    # Группируем данные по странам
    sec_data = df.groupby('recipient')[[col_arms, col_mil_visits, col_exercises]].sum().reset_index()
    
    # Считаем сумму дипломатических событий
    sec_data['soft_security'] = sec_data[col_mil_visits] + sec_data[col_exercises]
    
    # Нормализуем данные (приводим к диапазону 0-1) для визуального сравнения на графике
    scaler = MinMaxScaler()
    sec_data[['norm_arms', 'norm_diplomacy']] = scaler.fit_transform(sec_data[[col_arms, 'soft_security']])
    
    # Сортируем топ-10 по общей активности
    sec_data['total'] = sec_data['norm_arms'] + sec_data['norm_diplomacy']
    top_10 = sec_data.sort_values('total', ascending=False).head(10)
    
    # === ПЕРЕВОД НАЗВАНИЙ ===
    top_10['recipient_ru'] = top_10['recipient'].map(COUNTRY_RU).fillna(top_10['recipient'])
    
    # Настройка графика
    fig, ax = plt.subplots(figsize=(14, 8))
    y = np.arange(len(top_10))
    height = 0.35
    
    # Рисуем горизонтальные полосы
    # Красные - оружие, Синие - дипломатия
    rects1 = ax.barh(y + height/2, top_10['norm_arms'], height, label='Торговля оружием (Hard Power)', color='#C0392B')
    rects2 = ax.barh(y - height/2, top_10['norm_diplomacy'], height, label='Военная дипломатия (Учения/Визиты)', color='#2980B9')
    
    # Настройка осей
    ax.set_yticks(y)
    ax.set_yticklabels(top_10['recipient_ru'], fontweight='bold', fontsize=12) # Русские подписи
    ax.invert_yaxis() # Сверху вниз
    
    ax.set_xlabel('Нормированный индекс активности (0-1)', fontweight='bold')
    ax.set_title('Структура безопасности: Торговля vs. Дипломатия', fontsize=16, fontweight='bold')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), 
            ncol=2, frameon=True)
    add_source(fig)
    plt.tight_layout(rect=[0, 0.15, 1, 0.95])
    
    # Добавляем текстовые подписи значений (Сырые данные)
    for i, (idx, row) in enumerate(top_10.iterrows()):
        # Значение оружия (TIV)
        # Если значение есть, пишем его. Если 0 - не пишем.
        arms_raw = row[col_arms]
        if arms_raw > 0:
            # Форматируем: если больше миллиона - пишем 100M, если меньше - просто число
            arms_val = f"{arms_raw:.0f} TIV"
            # Смещаем текст чуть вправо от полоски
            ax.text(row['norm_arms'] + 0.01, i + height/2, arms_val, va='center', fontsize=9, color='#880000', fontweight='bold')
        
        # Значение дипломатии (события)
        dip_val = f"{int(row['soft_security'])} events"
        if row['soft_security'] > 0:
            ax.text(row['norm_diplomacy'] + 0.01, i - height/2, dip_val, va='center', fontsize=9, color='#004488', fontweight='bold')

    # Добавляем источник внизу
    add_source(fig)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    filename = '8_Security_Structure.jpg'
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Готово! Файл сохранен как {filename}")