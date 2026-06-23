import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Patch
from china_config import load_data, add_source, get_text, LANG

df, _, _, _ = load_data()

if df is not None:
    period_pre = df[(df['year'] >= 2013) & (df['year'] <= 2020)]
    period_post = df[df['year'] >= 2021]
    
    metrics = ['gdi_idx', 'gsi_idx']
    metric_names = [get_text('economy_gdi'), get_text('security_gsi')]
    
    vals_pre = [period_pre[m].mean() for m in metrics]
    vals_post = [period_post[m].mean() for m in metrics]
    growth = [((post - pre) / pre) * 100 if pre > 0 else 0 for pre, post in zip(vals_pre, vals_post)]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(11, 8))
    
    rects1 = ax.bar(x - width/2, vals_pre, width, color='#BDC3C7')
    rects2 = ax.bar(x + width/2, vals_post, width, color='#2980B9')
    
    ax.set_ylabel(get_text('average_engagement'), fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names, fontsize=12, fontweight='bold')
    
    y_limit = max(max(vals_post), max(vals_pre)) * 1.25
    ax.set_ylim(0, y_limit)
    
    for i, val in enumerate(growth):
        txt = f"{val:+.1f}%"
        color = '#27AE60' if val > 0 else '#C0392B'
        
        ax.text(x[i] + width/2, vals_post[i] + (y_limit * 0.02), txt, 
                ha='center', va='bottom', color=color, fontweight='bold', fontsize=12)

    legend_elements = [
        Patch(facecolor='#BDC3C7', label=get_text('bri_epoch')),
        Patch(facecolor='#2980B9', label=get_text('initiatives_epoch'))
    ]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), 
              ncol=2, frameon=True, borderpad=1)

    add_source(fig)
    plt.tight_layout(rect=[0, 0.05, 1, 0.99])
    
    filename = f'Initiatives_Comparison_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    print(f"Saved {filename}")