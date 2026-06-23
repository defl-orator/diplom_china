import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from china_config import load_data, add_source, get_country, get_text, LANG

df, _, _, _ = load_data()
col_surv = 'sec_02_surveillance_usd'

if df is not None:
    # Divide the core timeline structure
    df['period'] = df['year'].apply(
        lambda x: get_text('bri_epoch') if 2013 <= x <= 2020 else (get_text('initiatives_epoch') if x >= 2021 else 'Other')
    )
    
    # Measure historical surveillance indices
    stats = df[df['period'] != 'Other'].groupby(['period', 'recipient'])[col_surv].mean().reset_index()
    
    top_recipients = stats.groupby('recipient')[col_surv].sum().sort_values(ascending=False).head(8).index
    plot_data = stats[stats['recipient'].isin(top_recipients)].copy()
    plot_data['recipient_localized'] = plot_data['recipient'].apply(get_country)
    
    pivot_df = plot_data.pivot(index='recipient_localized', columns='period', values=col_surv).fillna(0) / 1e6
    pivot_df = pivot_df.sort_values(get_text('bri_epoch'), ascending=True)

    ax = pivot_df.plot(kind='barh', figsize=(12, 8), color=['#BDC3C7', '#8E44AD'], width=0.8)
    
    plt.xlabel(get_text('average_annual_projects'), fontweight='bold')
    plt.ylabel('')
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=True)
    add_source(plt.gcf())
    plt.tight_layout(rect=[0, 0.05, 1, 0.99])
    
    filename = f'Digital_Surveillance_Comp_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    print(f"Saved {filename}")