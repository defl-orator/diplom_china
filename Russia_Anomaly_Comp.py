import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns 
from scipy.stats import zscore
from china_config import load_data, add_source, get_label, get_text, LANG

df, _, _, _ = load_data()

if df is not None:
    # Use metrics that are fully valid up to 2024
    cols = ['dev_03_fdi_usd', 'sec_01_arms_transfer_tiv', 
            'sec_04_joint_exercise_ct', 'sec_03_military_engagement_ct']
    
    results = []
    # Identify comparative epochs
    periods = [(get_text('bri_epoch'), df[df['year'].between(2013, 2020)]), 
               (get_text('initiatives_epoch'), df[df['year'] >= 2021])]

    for p_name, p_df in periods:
        # Mean value calculations
        means = p_df.groupby('recipient')[cols].mean()
        
        # Calculate Z-score to measure Russian divergence from regional averages
        z_data = means.apply(zscore)
        
        if 'Russia' in z_data.index:
            r_z = z_data.loc['Russia'].to_frame(name='Z-Score')
            r_z['Period'] = p_name
            r_z['Indicator'] = r_z.index.map(get_label)
            results.append(r_z)

    plot_df = pd.concat(results).reset_index()

    plt.figure(figsize=(12, 8))
    
    sns.barplot(data=plot_df, y='Indicator', x='Z-Score', hue='Period', 
                palette=['#BDC3C7', '#C0392B'])
    
    # Reference guide-lines
    plt.axvline(0, color='black', lw=1.5, label=get_text('average_neighbor'))
    plt.axvline(1.5, color='#E67E22', linestyle='--', alpha=0.6) # High anomaly threshold line
    
    plt.xlabel(get_text('z_score_label'), fontweight='bold')
    plt.ylabel('')
    
    plt.legend(title=get_text('period_legend_title'), loc='upper center', bbox_to_anchor=(0.5, -0.12), 
               ncol=2, frameon=True, borderpad=1)
    
    plt.grid(axis='x', linestyle=':', alpha=0.7)
    
    # Text annotation over the grid layout
    plt.text(1.6, 0.5, get_text('anomaly_zone'), color='#E67E22', fontweight='bold', fontsize=10)

    add_source(plt.gcf())
    plt.tight_layout(rect=[0, 0.05, 1, 0.99])
    
    filename = f'Russia_Anomaly_Comp_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    print(f"Saved {filename}")