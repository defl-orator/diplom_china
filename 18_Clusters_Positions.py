import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text
from sklearn.cluster import KMeans
from china_config import load_data, add_source, COUNTRY_RU

# Группировка стран
GROUPS_MAP = {
    "SUPPORTED_ALL": ["Bhutan", "Kazakhstan", "Kyrgyzstan", "Laos", "Mongolia", "Myanmar", "Pakistan", "Russia", "Tajikistan", "Malaysia", "Brunei"],
    "PARTIALLY": ["Nepal", "Vietnam", "Philippines", "Indonesia"],
    "NOTHING_SAID": ["Afghanistan", "North Korea", "South Korea"],
    "NOT_SUPPORTED": ["India", "Japan"]
}

POS_COLORS = {
    "SUPPORTED_ALL": "#27AE60", # Зеленый
    "PARTIALLY": "#F1C40F",    # Желтый
    "NOTHING_SAID": "#95A5A6", # Серый
    "NOT_SUPPORTED": "#E74C3C"  # Красный
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
    
    # Считаем кластеры только для того, чтобы подтвердить их наличие в выводах
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(stats[['gdi_idx', 'gsi_idx']])
    stats['cluster'] = kmeans.labels_
    stats['pos_group'] = stats['recipient'].apply(get_pos_group)
    stats['recipient_ru'] = stats['recipient'].map(COUNTRY_RU).fillna(stats['recipient'])

    fig, ax = plt.subplots(figsize=(16, 11))
    fig.suptitle('Кластерный анализ: Дипломатические позиции vs Реальные данные (2021-2024)', 
                 fontsize=22, fontweight='bold', x=0.5, y=0.96)

    # Отрисовка точек
    for i, row in stats.iterrows():
        color = POS_COLORS[row['pos_group']]
        ax.scatter(row['gdi_idx'], row['gsi_idx'], 
                   s=650, c=color, edgecolors='#2C3E50', 
                   linewidth=1, alpha=0.95, zorder=3)

    # Подписи стран
    texts = [ax.text(row['gdi_idx'], row['gsi_idx'], row['recipient_ru'], 
                     fontweight='bold', fontsize=11) for i, row in stats.iterrows()]
    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='#BDC3C7', lw=1))

    ax.set_xlabel('Интенсивность экономического взаимодействия (GDI) →', fontweight='bold', fontsize=12)
    ax.set_ylabel('Интенсивность военного сотрудничества (GSI) →', fontweight='bold', fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.4)
    
    # ЛЕГЕНДА (только по позициям)
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=POS_COLORS["SUPPORTED_ALL"], markersize=14, label='Полная поддержка'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=POS_COLORS["PARTIALLY"], markersize=14, label='Частичная поддержка'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=POS_COLORS["NOTHING_SAID"], markersize=14, label='Нет позиции / Молчание'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=POS_COLORS["NOT_SUPPORTED"], markersize=14, label='Не поддержали'),
    ]

    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
              ncol=4, frameon=True, fontsize=11, borderpad=1)

    CUSTOM_SOURCES = "Sources: Analysis of IMF, AidData, SIPRI and Official Statements (2021-2024)."
    add_source(fig, CUSTOM_SOURCES, use_default=False)
    
    plt.subplots_adjust(bottom=0.18, top=0.88, left=0.1, right=0.9)
    plt.savefig('21_Clusters_Positions.jpg', dpi=300)
    print("Сохранен 21_Clusters_Positions.jpg")