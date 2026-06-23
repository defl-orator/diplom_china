import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from adjustText import adjust_text
from china_config import load_data, add_source, get_country, get_text, LANG

df, _, _, col_visits = load_data()

if df is not None:
    recent_df = df[df['year'] >= 2021].copy()
    stats = recent_df.groupby('recipient')[['gdi_idx', 'gsi_idx', col_visits]].mean().reset_index()
    stats['name_localized'] = stats['recipient'].apply(get_country)

    stats['gsi_idx_plot'] = np.log10(stats['gsi_idx'].clip(lower=0.0005))

    top_gdi_countries = stats.sort_values('gdi_idx', ascending=False).head(5)['recipient'].tolist()
    top_gsi_countries = stats.sort_values('gsi_idx', ascending=False).head(5)['recipient'].tolist()

    def classify_country(row):
        r = row['recipient']
        in_gdi = r in top_gdi_countries
        in_gsi = r in top_gsi_countries
        if in_gdi and in_gsi:
            return 'BOTH'
        elif in_gdi:
            return 'GDI_ONLY'
        elif in_gsi:
            return 'GSI_ONLY'
        else:
            return 'MODERATE'

    stats['group'] = stats.apply(classify_country, axis=1)

    fig, ax = plt.subplots(figsize=(19, 10))
    
    GROUP_STYLES = {
        'BOTH': {'color': '#9B59B6', 'marker': 'D', 'label': get_text('both_leaders')},       
        'GDI_ONLY': {'color': '#27AE60', 'marker': 's', 'label': get_text('gdi_leaders_top')}, 
        'GSI_ONLY': {'color': '#E67E22', 'marker': '^', 'label': get_text('gsi_leaders_top')}, 
        'MODERATE': {'color': '#2980B9', 'marker': 'o', 'label': get_text('moderate_group')}   
    }

    texts = []
    for i, row in stats.iterrows():
        grp = row['group']
        style = GROUP_STYLES[grp]
        
        size = 620 if row['recipient'] == 'Russia' else 500
        
        ax.scatter(row['gdi_idx'], row['gsi_idx_plot'], 
                   s=size, color=style['color'], marker=style['marker'], 
                   edgecolors='black', alpha=0.90, zorder=3)
        
        is_russia = row['recipient'] == 'Russia'
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
        Line2D([0], [0], marker=GROUP_STYLES['BOTH']['marker'], color='w', markerfacecolor=GROUP_STYLES['BOTH']['color'], 
               label=GROUP_STYLES['BOTH']['label'], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=GROUP_STYLES['GDI_ONLY']['marker'], color='w', markerfacecolor=GROUP_STYLES['GDI_ONLY']['color'], 
               label=GROUP_STYLES['GDI_ONLY']['label'], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=GROUP_STYLES['GSI_ONLY']['marker'], color='w', markerfacecolor=GROUP_STYLES['GSI_ONLY']['color'], 
               label=GROUP_STYLES['GSI_ONLY']['label'], markersize=12, markeredgecolor='k'),
        Line2D([0], [0], marker=GROUP_STYLES['MODERATE']['marker'], color='w', markerfacecolor=GROUP_STYLES['MODERATE']['color'], 
               label=GROUP_STYLES['MODERATE']['label'], markersize=12, markeredgecolor='k')
    ]
    
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.11), 
              ncol=2, frameon=True, borderpad=1.2, fontsize=11)

    if LANG == 'EN':
        info_text = (
            "METRIC COMPOSITION:\n\n"
            "• ECONOMY (GDI):\n"
            "  Direct Investment (FDI)\n"
            "  and Currency Swaps.\n\n"
            "• SECURITY (GSI):\n"
            "  Arms Transfers (SIPRI TIV),\n"
            "  Joint Military Drills, and\n"
            "  Military Diplomatic Visits.\n\n"
            "All indexes are normalized\n"
            "to [0, 1] range.\n\n"
            "CLASSIFICATION RULE:\n"
            "Countries are classified based\n"
            "on whether they are in the\n"
            "TOP-5 of each index."
        )
    else:
        info_text = (
            "СОСТАВ МЕТРИК:\n\n"
            "• ЭКОНОМИКА (GDI):\n"
            "  Прямые инвестиции (FDI)\n"
            "  и валютные свопы.\n\n"
            "• БЕЗОПАСНОСТЬ (GSI):\n"
            "  Торговля оружием (TIV),\n"
            "  совместные учения и\n"
            "  визиты военной дипломатии.\n\n"
            "Все индексы нормализованы\n"
            "к единой шкале [0; 1].\n\n"
            "ПРАВИЛО КЛАССИФИКАЦИИ:\n"
            "Группы выделены на основе\n"
            "вхождения стран в ТОП-5\n"
            "по каждому из индексов."
        )

    ax.text(1.03, 0.5, info_text, transform=ax.transAxes, va='center', ha='left', 
            fontsize=10.5, fontweight='bold', color='#2C3E50',
            bbox=dict(boxstyle='round,pad=1.0', facecolor='#F8F9F9', edgecolor='#D5DBDB', alpha=0.95), zorder=7)

    add_source(fig)
    plt.subplots_adjust(left=0.08, right=0.76, top=0.95, bottom=0.22)
    
    filename = f'Clusters_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Saved {filename}")