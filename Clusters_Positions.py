import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text
from sklearn.cluster import KMeans
from china_config import load_data, add_source, COUNTRY_RU

# Группировка стран актуализирована на основе официальных данных
GROUPS_MAP = {
    "SUPPORTED_ALL": [
        "Bhutan", "Kazakhstan", "Kyrgyzstan", "Laos", "Mongolia", 
        "Myanmar", "Pakistan", "Russia", "Tajikistan", "Malaysia", 
        "Brunei", "Afghanistan", "North Korea", "Indonesia", "Vietnam"
    ],
    "PARTIALLY": ["Nepal", "Philippines"],
    "NOTHING_SAID": ["South Korea"],
    "NOT_SUPPORTED": ["India", "Japan"]
}

POS_COLORS = {
    "SUPPORTED_ALL": "#27AE60", # Зеленый
    "PARTIALLY": "#F1C40F",    # Желтый
    "NOTHING_SAID": "#95A5A6", # Серый
    "NOT_SUPPORTED": "#E74C3C"  # Красный
}

# Добавляем словарь для фигур
POS_MARKERS = {
    "SUPPORTED_ALL": "o",   # Круг
    "PARTIALLY": "^",       # Треугольник
    "NOTHING_SAID": "s",    # Квадрат
    "NOT_SUPPORTED": "p"    # Пятиугольник
}

def get_pos_group(name):
    for k, v in GROUPS_MAP.items():
        if name in v: return k
    return "NOTHING_SAID"

df, _, _, _ = load_data()

if df is not None:
    # Берем данные за последние годы для актуальности
    recent_df = df[df['year'] >= 2021]
    stats = recent_df.groupby('recipient')[['gdi_idx', 'gsi_idx']].mean().reset_index()
    
    # Считаем кластеры
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(stats[['gdi_idx', 'gsi_idx']])
    stats['cluster'] = kmeans.labels_
    stats['pos_group'] = stats['recipient'].apply(get_pos_group)
    stats['recipient_ru'] = stats['recipient'].map(COUNTRY_RU).fillna(stats['recipient'])

    stats['gsi_idx_plot'] = np.log10(stats['gsi_idx'].clip(lower=0.0005))

    fig, ax = plt.subplots(figsize=(16, 11))

    # 1. Отрисовка точек
    for i, row in stats.iterrows():
        color = POS_COLORS[row['pos_group']]
        marker = POS_MARKERS[row['pos_group']]
        
        ax.scatter(row['gdi_idx'], row['gsi_idx_plot'], # Строим по логарифмированной Y-оси
                   s=650, 
                   c=color, 
                   marker=marker, 
                   edgecolors='#2C3E50', 
                   linewidth=1.2, 
                   alpha=0.95, 
                   zorder=3)

    # 2. НАСТРОЙКА ОСЕЙ
    # Задаем лимиты в логарифмических значениях
    ax.set_ylim(np.log10(0.0004), np.log10(0.20))
    ax.set_xlim(-0.05, 0.75)

    # Задаем деления шкалы Y и маскируем их под реальные значения
    ticks_real = [0.0005, 0.001, 0.003, 0.01, 0.03, 0.10, 0.20]
    ticks_labels = ['0.000', '0.001', '0.003', '0.010', '0.030', '0.100', '0.200']
    
    ax.set_yticks([np.log10(t) for t in ticks_real])
    ax.set_yticklabels(ticks_labels)

    ax.set_xlabel('Интенсивность экономического взаимодействия (GDI) →', fontweight='bold', fontsize=12, color='#2C3E50')
    ax.set_ylabel('Интенсивность военного сотрудничества (GSI) →', fontweight='bold', fontsize=12, color='#2C3E50')
    
    # Сетка и рамки
    ax.grid(True, which="both", linestyle=':', color='#E0E0E0', alpha=0.6, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#BDC3C7')
    ax.spines['bottom'].set_color('#BDC3C7')

    # 3. ПОДПИСИ СТРАН
    texts = [ax.text(row['gdi_idx'], row['gsi_idx_plot'], row['recipient_ru'], 
                     fontweight='bold', fontsize=10.5, color='#2C3E50') for i, row in stats.iterrows()]
    
    adjust_text(texts, 
                x=stats['gdi_idx'].values,  
                y=stats['gsi_idx_plot'].values,  
                arrowprops=dict(arrowstyle='-', color='#BDC3C7', lw=1, alpha=0.7),
                expand=(1.4, 1.6), 
                only_move={'text': 'xy+', 'static': 'xy+', 'explode': 'xy+', 'pull': 'xy+'})

    # 4. ЛЕГЕНДА
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker=POS_MARKERS["SUPPORTED_ALL"], color='w', 
               markerfacecolor=POS_COLORS["SUPPORTED_ALL"], markersize=13, label='Полная поддержка', markeredgecolor='#2C3E50'),
        Line2D([0], [0], marker=POS_MARKERS["PARTIALLY"], color='w', 
               markerfacecolor=POS_COLORS["PARTIALLY"], markersize=13, label='Частичная поддержка', markeredgecolor='#2C3E50'),
        Line2D([0], [0], marker=POS_MARKERS["NOTHING_SAID"], color='w', 
               markerfacecolor=POS_COLORS["NOTHING_SAID"], markersize=13, label='Нет позиции / Молчание', markeredgecolor='#2C3E50'),
        Line2D([0], [0], marker=POS_MARKERS["NOT_SUPPORTED"], color='w', 
               markerfacecolor=POS_COLORS["NOT_SUPPORTED"], markersize=13, label='Не поддержали', markeredgecolor='#2C3E50'),
    ]

    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
              ncol=4, frameon=True, fontsize=11, borderpad=1)

    CUSTOM_SOURCES = "Sources: Analysis of IMF, AidData, SIPRI and Official Statements (2021-2024)."
    add_source(fig, CUSTOM_SOURCES, use_default=False)
    
    plt.subplots_adjust(bottom=0.18, top=0.98, left=0.1, right=0.9)
    plt.savefig('Clusters_Positions_Shapes.jpg', dpi=300)
    print("Сохранен Clusters_Positions_Shapes.jpg")