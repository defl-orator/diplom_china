import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from adjustText import adjust_text
from china_config import load_data, add_source, COUNTRY_RU

# Загружаем данные
df, _, _, col_visits = load_data()

if df is not None:
    # 1. Подготовка данных
    recent_df = df[df['year'] >= 2021].copy()
    stats = recent_df.groupby('recipient')[['gdi_idx', 'gsi_idx', col_visits]].mean().reset_index()
    
    # 2. Кластерный анализ
    X = stats[['gdi_idx', 'gsi_idx']]
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    stats['cluster'] = kmeans.fit_predict(X)
    
    stats['name_ru'] = [COUNTRY_RU.get(c, c) for c in stats['recipient']]

    # 3. Настройка оформления
    fig, ax = plt.subplots(figsize=(15, 10))
    
    cluster_info = stats.groupby('cluster')[['gdi_idx', 'gsi_idx']].mean()
    
    # Цвета и маркеры для кластеров
    colors = {0: '#2980B9', 1: '#27AE60', 2: '#E67E22'} 
    markers = {0: 'o', 1: 's', 2: '^'} # Базовые фигуры: круг, квадрат, треугольник
    
    idx_econ = cluster_info['gdi_idx'].idxmax()
    idx_mil = cluster_info['gsi_idx'].idxmax()
    idx_low = [i for i in range(3) if i not in [idx_econ, idx_mil]][0]
    
    labels_map = {
        idx_econ: "Экономические партнеры (GDI лидеры)",
        idx_mil: "Партнеры в сфере безопасности (GSI лидеры)",
        idx_low: "Группа умеренного взаимодействия"
    }

    # 4. Отрисовка
    texts = []
    for i, row in stats.iterrows():
        cluster = row['cluster']
        is_russia = row['recipient'] == 'Russia'
        
        # ЛОГИКА ФИГУРЫ: Если Россия — пятиугольник ('p'), иначе — фигура кластера
        marker = 'p' if is_russia else markers[cluster]
        color = '#C0392B' if is_russia else colors[cluster]
        
        size = 500 + (row[col_visits] * 120) if is_russia else 400 + (row[col_visits] * 100)
        
        ax.scatter(row['gdi_idx'], row['gsi_idx'], 
                   s=size, color=color, marker=marker, 
                   edgecolors='black', alpha=0.85, 
                   zorder=10 if is_russia else 3)
        
        texts.append(ax.text(row['gdi_idx'], row['gsi_idx'], row['name_ru'], 
                             fontweight='bold' if is_russia else 'normal',
                             fontsize=12 if is_russia else 10))

    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray', lw=0.5))

    # ax.set_title('Кластерный анализ стратегий взаимодействия Китая с соседями (2021-2024)', fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel('Индекс экономического взаимодействия (FDI + Swaps) →', fontweight='bold')
    ax.set_ylabel('Индекс вовлеченности в безопасность (Оружие + Учения) →', fontweight='bold')
    
    # 5. ЛЕГЕНДА
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker=markers[idx_econ], color='w', markerfacecolor=colors[idx_econ], 
               label=labels_map[idx_econ], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=markers[idx_mil], color='w', markerfacecolor=colors[idx_mil], 
               label=labels_map[idx_mil], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=markers[idx_low], color='w', markerfacecolor=colors[idx_low], 
               label=labels_map[idx_low], markersize=12, markeredgecolor='k'),
        # Пятиугольник для России в легенде
        Line2D([0], [0], marker='p', color='w', markerfacecolor='#C0392B', 
               label='Россия', markersize=15, markeredgecolor='k')
    ]
    
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), 
              ncol=2, frameon=True, borderpad=1.2, fontsize=11)

    add_source(fig)
    plt.tight_layout(rect=[0, 0.05, 1, 0.99])
    
    plt.savefig('Clusters.jpg', dpi=300)
    print("Сохранен Clusters.jpg")