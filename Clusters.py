import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from adjustText import adjust_text
from china_config import load_data, add_source, get_country, get_text, LANG

df, _, _, col_visits = load_data()

if df is not None:
    recent_df = df[df['year'] >= 2021].copy()
    stats = recent_df.groupby('recipient')[['gdi_idx', 'gsi_idx', col_visits]].mean().reset_index()
    
    X = stats[['gdi_idx', 'gsi_idx']]
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    stats['cluster'] = kmeans.fit_predict(X)
    
    stats['name_localized'] = stats['recipient'].apply(get_country)
    stats['gsi_idx_plot'] = np.log10(stats['gsi_idx'].clip(lower=0.0005))

    fig, ax = plt.subplots(figsize=(15, 10))
    
    cluster_info = stats.groupby('cluster')[['gdi_idx', 'gsi_idx']].mean()
    
    colors = {0: '#2980B9', 1: '#27AE60', 2: '#E67E22'} 
    markers = {0: 'o', 1: 's', 2: '^'}
    
    idx_econ = cluster_info['gdi_idx'].idxmax()
    idx_mil = cluster_info['gsi_idx'].idxmax()
    idx_low = [i for i in range(3) if i not in [idx_econ, idx_mil]][0]
    
    labels_map = {
        idx_econ: get_text('gdi_leaders'),
        idx_mil: get_text('gsi_leaders'),
        idx_low: get_text('moderate_group')
    }

    texts = []
    for i, row in stats.iterrows():
        cluster = row['cluster']
        is_russia = row['recipient'] == 'Russia'
        
        marker = 'p' if is_russia else markers[cluster]
        color = '#C0392B' if is_russia else colors[cluster]
        
        size = 500 + (row[col_visits] * 120) if is_russia else 400 + (row[col_visits] * 100)
        
        ax.scatter(row['gdi_idx'], row['gsi_idx_plot'], 
                   s=size, color=color, marker=marker, 
                   edgecolors='black', alpha=0.85, 
                   zorder=10 if is_russia else 3)
        
        texts.append(ax.text(row['gdi_idx'], row['gsi_idx_plot'], row['name_localized'], 
                             fontweight='bold' if is_russia else 'normal',
                             fontsize=12 if is_russia else 10))

    ax.set_ylim(np.log10(0.0004), np.log10(0.20))
    ax.set_xlim(-0.05, 0.75)

    ticks_real = [0.0005, 0.001, 0.003, 0.01, 0.03, 0.10, 0.20]
    ticks_labels = ['0.000', '0.001', '0.003', '0.010', '0.030', '0.100', '0.200']
    
    ax.set_yticks([np.log10(t) for t in ticks_real])
    ax.set_yticklabels(ticks_labels)

    adjust_text(texts, 
                x=stats['gdi_idx'].values,
                y=stats['gsi_idx_plot'].values,
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.8, alpha=0.7),
                expand=(1.4, 1.6),
                only_move={'text': 'xy+', 'static': 'xy+', 'explode': 'xy+', 'pull': 'xy+'})

    ax.set_xlabel(f"{get_text('economy_gdi')} →", fontweight='bold')
    ax.set_ylabel(f"{get_text('security_gsi')} →", fontweight='bold')
    
    ax.grid(True, which="both", linestyle=':', color='#E0E0E0', alpha=0.6, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#BDC3C7')
    ax.spines['bottom'].set_color('#BDC3C7')

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker=markers[idx_econ], color='w', markerfacecolor=colors[idx_econ], 
               label=labels_map[idx_econ], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=markers[idx_mil], color='w', markerfacecolor=colors[idx_mil], 
               label=labels_map[idx_mil], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=markers[idx_low], color='w', markerfacecolor=colors[idx_low], 
               label=labels_map[idx_low], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker='p', color='w', markerfacecolor='#C0392B', 
               label=get_text('russia'), markersize=15, markeredgecolor='k')
    ]
    
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), 
              ncol=2, frameon=True, borderpad=1.2, fontsize=11)

    add_source(fig)
    plt.tight_layout(rect=[0, 0.05, 1, 0.99])
    
    filename = f'Clusters_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    print(f"Saved {filename}")