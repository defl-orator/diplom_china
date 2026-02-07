import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from china_config import load_data, add_source, COUNTRY_RU

df, _, _, _ = load_data()

if df is not None:
    
    df_bri = df[(df['year'] >= 2013) & (df['year'] <= 2020)].groupby('recipient')['gdi_idx'].mean()
    df_new = df[df['year'] >= 2021].groupby('recipient')['gdi_idx'].mean()
    
    comp = pd.DataFrame({'Pre-2021': df_bri, 'Post-2021': df_new}).dropna()
    comp['diff'] = comp['Post-2021'] - comp['Pre-2021']
    comp = comp.sort_values('diff', ascending=True)
    
    subset = pd.concat([comp.head(5), comp.tail(10)])
    labels = [COUNTRY_RU.get(c, c) for c in subset.index]
    
    fig, ax = plt.subplots(figsize=(13, 9))
    
    ax.hlines(y=range(len(subset)), xmin=subset['Pre-2021'], xmax=subset['Post-2021'], 
              color='gray', alpha=0.4, linewidth=2)
    
    ax.scatter(subset['Pre-2021'], range(len(subset)), color='#95A5A6', s=120, zorder=3)
    colors = ['#E74C3C' if x < 0 else '#27AE60' for x in subset['diff']]
    ax.scatter(subset['Post-2021'], range(len(subset)), color=colors, s=180, zorder=4)
    
    ax.set_yticks(range(len(subset)))
    ax.set_yticklabels(labels, fontweight='bold', fontsize=11)
    
    ax.set_title('Реальная экономика (FDI): Эпоха BRI vs. Эпоха Инициатив', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Индекс прямых инвестиций и свопов (0-1)', fontweight='bold')
    
    custom_lines = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#95A5A6', markersize=12, label='2013-2020 (BRI)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27AE60', markersize=12, label='Рост после 2021'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E74C3C', markersize=12, label='Спад после 2021')
    ]
    ax.legend(handles=custom_lines, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
              ncol=3, frameon=True, borderpad=1)
    
    add_source(fig)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig('16_Impact_Dumbbell.jpg', dpi=300)
    print("Сохранен 16_Impact_Dumbbell.jpg (Валидные данные)")