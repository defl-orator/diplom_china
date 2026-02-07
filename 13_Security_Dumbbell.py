import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from china_config import load_data, add_source, COUNTRY_RU

df, _, _, _ = load_data()

if df is not None:
    # 1. Формируем метрику "Активность" (сумма событий)
    df['sec_activity'] = (df['sec_01_arms_transfer_orders_ct'] + 
                          df['sec_03_military_engagement_ct'] + 
                          df['sec_04_joint_exercise_ct'])

    # 2. Считаем СРЕДНЕЕ в год (чтобы уравнять периоды 8 лет и 4 года)
    df_bri = df[(df['year'] >= 2013) & (df['year'] <= 2020)].groupby('recipient')['sec_activity'].mean()
    df_new = df[df['year'] >= 2021].groupby('recipient')['sec_activity'].mean()
    
    comp = pd.DataFrame({'Pre-2021': df_bri, 'Post-2021': df_new}).fillna(0)
    comp['diff'] = comp['Post-2021'] - comp['Pre-2021']
    
    # Сортируем: сверху самые растущие, снизу падающие
    comp = comp.sort_values('diff', ascending=True)
    
    # Берем самые показательные (где были изменения)
    # Исключаем тех, у кого и было 0 и стало 0
    subset = comp[(comp['Pre-2021'] > 0) | (comp['Post-2021'] > 0)].copy()
    
    labels = [COUNTRY_RU.get(c, c) for c in subset.index]
    
    fig, ax = plt.subplots(figsize=(13, 10))
    
    # Линии
    ax.hlines(y=range(len(subset)), xmin=subset['Pre-2021'], xmax=subset['Post-2021'], 
              color='gray', alpha=0.4, linewidth=2)
    
    # Точки
    ax.scatter(subset['Pre-2021'], range(len(subset)), color='#95A5A6', s=120, zorder=3, label='_nolegend_')
    colors = ['#E74C3C' if x < 0 else '#27AE60' for x in subset['diff']]
    ax.scatter(subset['Post-2021'], range(len(subset)), color=colors, s=180, zorder=4, label='_nolegend_')
    
    # Оформление
    ax.set_yticks(range(len(subset)))
    ax.set_yticklabels(labels, fontweight='bold', fontsize=11)
    
    ax.set_title('Военное сотрудничество (GSI): Смена интенсивности', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Среднее количество военных контактов и сделок в год (ед.)', fontweight='bold', fontsize=12)
    
    # Легенда
    custom_lines = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#95A5A6', markersize=12, label='Эпоха BRI (ср. уровень)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27AE60', markersize=12, label='Рост активности'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E74C3C', markersize=12, label='Спад активности')
    ]
    ax.legend(handles=custom_lines, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
              ncol=3, frameon=True, borderpad=1)
    
    # Источник
    CUSTOM_SRC = "Sources: SIPRI, NDU. Metric: Average annual military events (arms orders + meetings + drills)."
    add_source(fig, CUSTOM_SRC, use_default=False)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig('17_Security_Dumbbell.jpg', dpi=300)
    print("Сохранен 17_Security_Dumbbell.jpg")