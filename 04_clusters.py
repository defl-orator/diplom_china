import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from sklearn.cluster import KMeans
from matplotlib.patches import Patch
from china_config import load_data, add_source, COUNTRY_RU

df, _, _, col_visits = load_data()

if df is not None:
    stats = df.groupby('recipient')[['gdi_idx', 'gsi_idx', col_visits]].mean().reset_index()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(stats[['gdi_idx', 'gsi_idx']])
    stats['cluster'] = kmeans.labels_
    stats['recipient_ru'] = stats['recipient'].map(COUNTRY_RU).fillna(stats['recipient'])
    
    v_vals = stats[col_visits]
    p33, p66 = np.percentile(v_vals, 33), np.percentile(v_vals, 66)

    fig, ax = plt.subplots(figsize=(15, 11))
    colors = {0: '#3498DB', 1: '#E67E22', 2: '#9B59B6'}
    
    sc_list = []
    for i, row in stats.iterrows():
        v = row[col_visits]
        m = 'o' if v <= p33 else '^' if v <= p66 else 's'
        sc = ax.scatter(row['gdi_idx'], row['gsi_idx'], s=400 + (v * 100), marker=m,
                   color=colors[row['cluster']], edgecolors='#2C3E50', alpha=0.8)
        sc_list.append(sc)

    # границы графика
    plt.tight_layout(rect=[0, 0.15, 1, 0.95])
    y_min, y_max = ax.get_ylim()
    y_offset = (y_max - y_min) * 0.05 # Отступ 5% от высоты

    texts = [ax.text(row['gdi_idx'], row['gsi_idx'] + y_offset, row['recipient_ru'], 
                    fontweight='bold', fontsize=11, ha='center') for _, row in stats.iterrows()]
    
    adjust_text(texts, add_objects=sc_list, expand_points=(3, 3), 
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.8, shrinkB=5))
    
    legend_elements = [Patch(facecolor=colors[i], edgecolor='k', label=f'Группа {i+1}') for i in range(3)]
    legend_elements.extend([
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Редкие'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='gray', markersize=10, label='Умеренные'),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', markersize=10, label='Частые')
    ])
    
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.12), 
              ncol=3, frameon=True, borderpad=1.2)
    
    ax.set_title('Кластерный анализ стратегий взаимодействия', fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel('Индекс Экономического взаимодействия (GDI) →', fontweight='bold')
    ax.set_ylabel('Индекс в сфере Безопасности (GSI) →', fontweight='bold')
    
    add_source(fig)
    plt.savefig('7_Clusters.jpg', dpi=300)
    print("Сохранен 7_Clusters.jpg")