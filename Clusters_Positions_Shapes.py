import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text
from sklearn.cluster import KMeans
from china_config import load_data, add_source, get_country, get_text, LANG

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
    "SUPPORTED_ALL": "#27AE60",
    "PARTIALLY": "#F1C40F",
    "NOTHING_SAID": "#95A5A6",
    "NOT_SUPPORTED": "#E74C3C"
}

POS_MARKERS = {
    "SUPPORTED_ALL": "o",
    "PARTIALLY": "^",
    "NOTHING_SAID": "s",
    "NOT_SUPPORTED": "p"
}

def get_pos_group(name):
    for k, v in GROUPS_MAP.items():
        if name in v: 
            return k
    return "NOTHING_SAID"

df, _, _, _ = load_data()

if df is not None:
    recent_df = df[df['year'] >= 2021]
    stats = recent_df.groupby('recipient')[['gdi_idx', 'gsi_idx']].mean().reset_index()
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(stats[['gdi_idx', 'gsi_idx']])
    stats['cluster'] = kmeans.labels_
    stats['pos_group'] = stats['recipient'].apply(get_pos_group)
    stats['recipient_localized'] = stats['recipient'].apply(get_country)

    stats['gsi_idx_plot'] = np.log10(stats['gsi_idx'].clip(lower=0.0005))

    fig, ax = plt.subplots(figsize=(16, 11))

    for i, row in stats.iterrows():
        color = POS_COLORS[row['pos_group']]
        marker = POS_MARKERS[row['pos_group']]
        
        ax.scatter(row['gdi_idx'], row['gsi_idx_plot'], 
                   s=650, 
                   c=color, 
                   marker=marker, 
                   edgecolors='#2C3E50', 
                   linewidth=1.2, 
                   alpha=0.95, 
                   zorder=3)

    ax.set_ylim(np.log10(0.0004), np.log10(0.20))
    ax.set_xlim(-0.05, 0.75)

    ticks_real = [0.0005, 0.001, 0.003, 0.01, 0.03, 0.10, 0.20]
    ticks_labels = ['0.000', '0.001', '0.003', '0.010', '0.030', '0.100', '0.200']
    
    ax.set_yticks([np.log10(t) for t in ticks_real])
    ax.set_yticklabels(ticks_labels)

    ax.set_xlabel(f"{get_text('economy_gdi')} →", fontweight='bold', fontsize=12, color='#2C3E50')
    ax.set_ylabel(f"{get_text('security_gsi')} →", fontweight='bold', fontsize=12, color='#2C3E50')
    
    ax.grid(True, which="both", linestyle=':', color='#E0E0E0', alpha=0.6, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#BDC3C7')
    ax.spines['bottom'].set_color('#BDC3C7')

    texts = [ax.text(row['gdi_idx'], row['gsi_idx_plot'], row['recipient_localized'], 
                     fontweight='bold', fontsize=10.5, color='#2C3E50') for i, row in stats.iterrows()]
    
    adjust_text(texts, 
                x=stats['gdi_idx'].values,  
                y=stats['gsi_idx_plot'].values,  
                arrowprops=dict(arrowstyle='-', color='#BDC3C7', lw=1, alpha=0.7),
                expand=(1.4, 1.6), 
                only_move={'text': 'xy+', 'static': 'xy+', 'explode': 'xy+', 'pull': 'xy+'})

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker=POS_MARKERS["SUPPORTED_ALL"], color='w', 
               markerfacecolor=POS_COLORS["SUPPORTED_ALL"], markersize=13, label=get_text('supported_all'), markeredgecolor='#2C3E50'),
        Line2D([0], [0], marker=POS_MARKERS["PARTIALLY"], color='w', 
               markerfacecolor=POS_COLORS["PARTIALLY"], markersize=13, label=get_text('partially'), markeredgecolor='#2C3E50'),
        Line2D([0], [0], marker=POS_MARKERS["NOTHING_SAID"], color='w', 
               markerfacecolor=POS_COLORS["NOTHING_SAID"], markersize=13, label=get_text('nothing_said'), markeredgecolor='#2C3E50'),
        Line2D([0], [0], marker=POS_MARKERS["NOT_SUPPORTED"], color='w', 
               markerfacecolor=POS_COLORS["NOT_SUPPORTED"], markersize=13, label=get_text('not_supported'), markeredgecolor='#2C3E50'),
    ]

    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.08), 
              ncol=4, frameon=True, fontsize=11, borderpad=1)

    CUSTOM_SOURCES = "Sources: Analysis of IMF, AidData, SIPRI and Official Statements (2021-2024)."
    add_source(fig, CUSTOM_SOURCES, use_default=False)
    
    plt.subplots_adjust(bottom=0.18, top=0.98, left=0.1, right=0.9)
    
    filename = f'Clusters_Positions_Shapes_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    print(f"Saved {filename}")