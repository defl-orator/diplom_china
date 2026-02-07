import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from china_config import load_data, add_source, COUNTRY_RU

df, _, _, _ = load_data()

if df is not None:
    # 1. Формируем метрику "Гуманитарка"
    df['civ_activity'] = (df['civ_02_healthcare_ct'] + 
                          df['civ_06_ci_ct'] + 
                          df['civ_05_judicial_engagement_ct'])

    # 2. Считаем СРЕДНЕЕ в год
    df_bri = df[(df['year'] >= 2013) & (df['year'] <= 2020)].groupby('recipient')['civ_activity'].mean()
    df_new = df[df['year'] >= 2021].groupby('recipient')['civ_activity'].mean()
    
    comp = pd.DataFrame({'Pre-2021': df_bri, 'Post-2021': df_new}).fillna(0)
    comp['diff'] = comp['Post-2021'] - comp['Pre-2021']
    
    comp = comp.sort_values('diff', ascending=True)
    subset = comp[(comp['Pre-2021'] > 0) | (comp['Post-2021'] > 0)].copy()
    
    labels = [COUNTRY_RU.get(c, c) for c in subset.index]
    
    fig, ax = plt.subplots(figsize=(13, 10))
    
    ax.hlines(y=range(len(subset)), xmin=subset['Pre-2021'], xmax=subset['Post-2021'], 
              color='gray', alpha=0.4, linewidth=2)
    
    ax.scatter(subset['Pre-2021'], range(len(subset)), color='#95A5A6', s=120, zorder=3)
    colors = ['#E74C3C' if x < 0 else '#27AE60' for x in subset['diff']]
    ax.scatter(subset['Post-2021'], range(len(subset)), color=colors, s=180, zorder=4)
    
    ax.set_yticks(range(len(subset)))
    ax.set_yticklabels(labels, fontweight='bold', fontsize=11)
    
    ax.set_title('Гуманитарное влияние (GCI): Смена интенсивности', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Среднее количество гуманитарных проектов и встреч в год (ед.)', fontweight='bold', fontsize=12)
    
    custom_lines = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#95A5A6', markersize=12, label='Эпоха BRI (ср. уровень)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27AE60', markersize=12, label='Рост влияния'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E74C3C', markersize=12, label='Спад влияния')
    ]
    ax.legend(handles=custom_lines, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
              ncol=3, frameon=True, borderpad=1)
    
    CUSTOM_SRC = "Sources: AidData, NBR. Metric: Average annual civil events (health + CIs + judicial)."
    add_source(fig, CUSTOM_SRC, use_default=False)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig('18_Humanitarian_Dumbbell.jpg', dpi=300)
    print("Сохранен 18_Humanitarian_Dumbbell.jpg")