import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns 
from scipy.stats import zscore
from china_config import load_data, add_source, RU_LABELS

df, _, _, _ = load_data()

if df is not None:
    # Используем только те колонки, которые валидны до 2024 года
    cols = ['dev_03_fdi_usd', 'sec_01_arms_transfer_tiv', 
            'sec_04_joint_exercise_ct', 'sec_03_military_engagement_ct']
    
    results = []
    # Сравниваем два ключевых периода для вашего исследования
    periods = [('2013-2020 (BRI)', df[df['year'].between(2013, 2020)]), 
               ('2021-2024 (Initiatives)', df[df['year'] >= 2021])]

    for p_name, p_df in periods:
        # Считаем среднее для каждой страны в рамках периода
        means = p_df.groupby('recipient')[cols].mean()
        
        # Считаем Z-score: насколько страна отклоняется от "среднего соседа" КНР в этот период
        # Z=0 — как все; Z > 1.5 — аномально высокая активность; Z < 0 — ниже среднего
        z_data = means.apply(zscore)
        
        if 'Russia' in z_data.index:
            r_z = z_data.loc['Russia'].to_frame(name='Z-Score')
            r_z['Period'] = p_name
            r_z['Indicator'] = r_z.index.map(lambda x: RU_LABELS.get(x, x))
            results.append(r_z)

    # Объединяем результаты в одну таблицу для графика
    plot_df = pd.concat(results).reset_index()

    plt.figure(figsize=(12, 8))
    
    # Рисуем группированные столбцы
    sns.barplot(data=plot_df, y='Indicator', x='Z-Score', hue='Period', 
                palette=['#BDC3C7', '#C0392B'])
    
    # Линии-ориентиры
    plt.axvline(0, color='black', lw=1.5, label='Средний уровень соседа')
    plt.axvline(1.5, color='#E67E22', linestyle='--', alpha=0.6) # Порог высокой аномальности
    
    plt.title('Аномалия России: Насколько РФ уникальна среди соседей КНР?', fontsize=16, fontweight='bold', pad=25)
    plt.xlabel('Z-Score (Отклонение от среднего соседа в единицах сигма)', fontweight='bold')
    plt.ylabel('')
    
    # Настройка легенды под графиком
    plt.legend(title='Период', loc='upper center', bbox_to_anchor=(0.5, -0.12), 
               ncol=2, frameon=True, borderpad=1)
    
    plt.grid(axis='x', linestyle=':', alpha=0.7)
    
    # Текст-пояснение прямо на графике
    plt.text(1.6, 0.5, 'Зона аномально\nвысокой активности', color='#E67E22', fontweight='bold', fontsize=10)

    add_source(plt.gcf())
    
    # Увеличиваем нижний отступ, чтобы легенда и источник не обрезались
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    plt.savefig('13_Russia_Anomaly_Comp.jpg', dpi=300)
    print("Сохранен 13_Russia_Anomaly_Comp.jpg (теперь с импортом seaborn)")