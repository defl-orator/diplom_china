import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from china_config import load_data, add_source, get_text, LANG

df, _, _, _ = load_data()

if df is not None:
    rus = df[df['recipient'] == 'Russia'].copy()
    
    # We only use durable metrics valid up to 2024
    cols = {
        'dev_03_fdi_usd': get_text('russia_pivot_title_fdi'),
        'sec_03_military_engagement_ct': get_text('russia_pivot_title_mil'),
        'sec_04_joint_exercise_ct': get_text('russia_pivot_title_ex')
    }
    
    pre_2021 = rus[(rus['year'] >= 2013) & (rus['year'] <= 2020)][list(cols.keys())].mean()
    post_2021 = rus[rus['year'] >= 2021][list(cols.keys())].mean()
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 7))
    palette = ['#95A5A6', '#C0392B'] 
    
    for i, (col_code, col_name) in enumerate(cols.items()):
        ax = axes[i]
        val1 = pre_2021[col_code]
        val2 = post_2021[col_code]
        
        bars = ax.bar(['2013-2020', '2021+'], [val1, val2], color=palette)
        
        # Determine the growth text color
        if val2 > val1:
            txt_color = '#27AE60' # Green for growth
        else:
            txt_color = '#C0392B' # Red for decline

        if val1 > 0:
            change = ((val2 - val1) / val1) * 100
            txt = f"{change:+.0f}%"
        else:
            txt = get_text('growth') if val2 > val1 else "0%"
            
        ax.set_title(col_name, fontweight='bold', fontsize=12)
        y_max = max(val1, val2) if max(val1, val2) > 0 else 1
        ax.set_ylim(0, y_max * 1.25)
        
        # Convert FDI values to billions if necessary
        d1, d2 = val1, val2
        if "usd" in col_code: 
            d1 /= 1e9; d2 /= 1e9
            unit_fmt = f"{{:.2f}} {get_text('billion_usd_short')}"
        else:
            unit_fmt = "{:.1f}"
            
        ax.text(0, bars[0].get_height(), unit_fmt.format(d1), ha='center', va='bottom', fontsize=11)
        ax.text(1, bars[1].get_height(), unit_fmt.format(d2), ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Dynamic pill badge for percentage change
        ax.text(0.5, y_max * 1.1, txt, ha='center', 
                bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'), 
                fontsize=11, color=txt_color, fontweight='bold')

    legend_elements = [
        Patch(facecolor='#95A5A6', label=get_text('bri_epoch')),
        Patch(facecolor='#C0392B', label=get_text('initiatives_epoch'))
    ]
    
    # Adjust position coordinates of elements to avoid overlapping
    fig.legend(handles=legend_elements, loc='lower center', ncol=2, 
               bbox_to_anchor=(0.5, 0.08), fontsize=12, frameon=True)

    add_source(fig)
    plt.tight_layout(rect=[0, 0.15, 1, 0.99])
    
    filename = f'Russia_Pivot_{LANG}.jpg'
    plt.savefig(filename, dpi=300)
    print(f"Saved {filename}")