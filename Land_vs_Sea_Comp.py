import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.patches import Patch
from china_config import load_data, add_source, get_text, LANG

df, _, _, _ = load_data()
LAND_NEIGHBORS = ["North Korea", "Russia", "Mongolia", "Kazakhstan", "Kyrgyzstan", "Tajikistan", "Afghanistan", "Pakistan", "India", "Nepal", "Bhutan", "Myanmar", "Laos", "Vietnam"]
SEA_NEIGHBORS = ["South Korea", "Japan", "Philippines", "Brunei", "Malaysia", "Indonesia"]

if df is not None:
    # Set localized names for borders and periods
    df['Border_Type'] = df['recipient'].apply(
        lambda x: get_text('land_border') if x in LAND_NEIGHBORS else (get_text('sea_border') if x in SEA_NEIGHBORS else 'Other')
    )
    df['Period'] = df['year'].apply(
        lambda x: get_text('bri_epoch') if 2013 <= x <= 2020 else (get_text('initiatives_epoch') if x >= 2021 else 'Other')
    )
    
    clean_df = df[(df['Border_Type'] != 'Other') & (df['Period'] != 'Other')]
    geo_stats = clean_df.groupby(['Border_Type', 'Period'])[['gdi_idx', 'gsi_idx']].mean().reset_index()
    
    melted = geo_stats.melt(id_vars=['Border_Type', 'Period'], var_name='Index', value_name='Value')
    melted['Index'] = melted['Index'].map({
        'gdi_idx': get_text('economy_gdi'), 
        'gsi_idx': get_text('security_gsi')
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
    
    # Calculate global maximum across both subplots to prevent Y-axis clipping
    global_max = melted['Value'].max() if not melted.empty else 1
    
    for ax, b_type in zip([ax1, ax2], [get_text('sea_border'), get_text('land_border')]):
        subset = melted[melted['Border_Type'] == b_type]
        
        # Render the grouped barplot
        sns.barplot(data=subset, x='Index', y='Value', hue='Period', 
                    palette=['#BDC3C7', '#2980B9' if b_type == get_text('sea_border') else '#C0392B'], ax=ax)
        
        ax.set_title(b_type, fontweight='bold', fontsize=14)
        ax.set_xlabel('')
        ax.set_ylabel(get_text('average_engagement') if ax == ax1 else '')
        ax.get_legend().remove()
        
        # Set standardized axis limits based on the global dataset maximum
        ax.set_ylim(0, global_max * 1.25)
        
        # Dynamic calculation of percentage changes and rendering text labels above bars
        if len(ax.containers) >= 2:
            container_pre = ax.containers[0]   # 2013-2020 (BRI)
            container_post = ax.containers[1]  # 2021-2024 (Initiatives)
            
            for j in range(2):  # 0: Economy, 1: Security
                v1 = container_pre[j].get_height()
                v2 = container_post[j].get_height()
                
                # Sanitize NaN or negative values safely
                v1 = 0 if np.isnan(v1) or v1 < 0 else v1
                v2 = 0 if np.isnan(v2) or v2 < 0 else v2
                
                if v1 > 0:
                    change = ((v2 - v1) / v1) * 100
                    txt = f"{change:+.1f}%"
                    txt_color = '#27AE60' if change >= 0 else '#C0392B'
                elif v2 > 0:
                    txt = get_text('new')
                    txt_color = '#27AE60'
                else:
                    txt = "0.0%"
                    txt_color = '#BDC3C7'
                
                # Align text dynamically using global_max to keep offset scaling uniform
                bar_post = container_post[j]
                x_pos = bar_post.get_x() + bar_post.get_width() / 2
                y_pos = v2 + (global_max * 0.03)
                
                ax.text(x_pos, y_pos, txt, ha='center', va='bottom', 
                        color=txt_color, fontweight='bold', fontsize=11)
    
    legend_elements = [
        Patch(facecolor='#BDC3C7', label=get_text('bri_epoch')),
        Patch(facecolor='#2980B9', label=get_text('initiatives_sea')),
        Patch(facecolor='#C0392B', label=get_text('initiatives_land'))
    ]
    
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, 
               bbox_to_anchor=(0.5, 0.07), frameon=True)
    
    add_source(fig)
    plt.tight_layout(rect=[0, 0.18, 1, 0.99])
    
    filename = f'Land_vs_Sea_Comp_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    plt.close()
    
    print(f"Saved {filename}")