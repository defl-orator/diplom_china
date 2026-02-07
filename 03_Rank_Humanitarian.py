import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.offsetbox import AnnotationBbox
from china_config import load_data, add_source, get_circular_flag, COUNTRY_RU

CUSTOM_PERIODS = [
    (2005, 2012, "До 2013 г."),
    (2013, 2020, "2013-2020 (BRI)"),
    (2021, 2024, "2021-2024 (GCI)")
]

df, _, _, _ = load_data()

# Все метрики в штуках (кол-во проектов, кол-во институтов, кол-во встреч)
civ_cols = ['civ_02_healthcare_ct', 'civ_06_ci_ct', 'civ_05_judicial_engagement_ct']
col = 'humanitarian_index'

def get_bezier_path(x1, y1, x2, y2):
    dist = (x2 - x1) * 0.45
    verts = [(x1, y1), (x1 + dist, y1), (x2 - dist, y2), (x2, y2)]
    return Path(verts, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])

if df is not None:
    df[col] = df[civ_cols].sum(axis=1)
    
    limit, unit = 5, "событий"
    p_labs = [p[2] for p in CUSTOM_PERIODS]
    period_order = {lab: i for i, lab in enumerate(p_labs)}
    
    res = []
    for s, e, l in CUSTOM_PERIODS:
        per_sum = df[(df['year']>=s) & (df['year']<=e)].groupby('recipient')[col].sum().reset_index()
        per_sum['period'] = l
        per_sum['p_idx'] = period_order[l]
        res.append(per_sum)
    ldf = pd.concat(res)
    ldf = ldf[ldf[col] > 0].copy()
    ldf['rank'] = ldf.groupby('period')[col].rank(method='first', ascending=False)

    global_top = df.groupby('recipient')[col].sum().sort_values(ascending=False).head(5)
    recent_top = ldf[ldf['period'] == CUSTOM_PERIODS[-1][2]].sort_values('rank').head(5)

    fig, ax = plt.subplots(figsize=(18, 10))
    visible_countries = ldf[ldf['rank'] <= limit]['recipient'].unique()
    palette = sns.color_palette("husl", len(visible_countries))
    colors = dict(zip(visible_countries, palette))

    for country in visible_countries:
        c_data = ldf[ldf['recipient'] == country].sort_values('p_idx')
        valid = c_data[c_data['rank'] <= limit + 1.5].copy()
        if len(valid) > 1:
            x_v = valid['p_idx'].values
            y_v = valid['rank'].values
            for j in range(len(x_v) - 1):
                if x_v[j+1] - x_v[j] == 1:
                    path = get_bezier_path(x_v[j], y_v[j], x_v[j+1], y_v[j+1])
                    ax.add_patch(patches.PathPatch(path, facecolor='none', edgecolor=colors[country], lw=7, zorder=3,
                                path_effects=[pe.Stroke(linewidth=12, foreground='white'), pe.Normal()]))

    for country in visible_countries:
        c_data = ldf[ldf['recipient'] == country].sort_values('p_idx')
        top_entries = c_data[c_data['rank'] <= limit]
        if not top_entries.empty:
            first = top_entries.iloc[0]
            ax.text(first['p_idx'] - 0.14, first['rank'], COUNTRY_RU.get(country, country), 
                    ha='right', va='center', fontsize=10.5, fontweight='bold', color=colors[country],
                    path_effects=[pe.withStroke(linewidth=3, foreground="white")], zorder=6)

        for _, row in c_data.iterrows():
            if row['rank'] <= limit:
                flag = get_circular_flag(row['recipient'], zoom=0.18)
                if flag: ax.add_artist(AnnotationBbox(flag, (row['p_idx'], row['rank']), frameon=False, zorder=5))

    ax.set_ylim(limit + 0.5, 0.5); ax.set_xlim(-0.7, 2.25)
    ax.set_xticks(np.arange(len(p_labs))); ax.set_xticklabels(p_labs, fontweight='bold', fontsize=14)
    ax.set_yticks(range(1, limit + 1)); ax.set_yticklabels([f"#{i}" for i in range(1, limit + 1)], fontweight='bold', color='gray')
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(axis='y', linestyle=':', alpha=0.3)

    info = ["ОБЩИЙ ТОП ЛИДЕРОВ (2005-2024):"]
    for i, (c, v) in enumerate(global_top.items()): info.append(f"{i+1}. {COUNTRY_RU.get(c,c)}: {v:.0f} {unit}")
    info.append("\n" + "─"*20 + f"\nТОП-5 ЭПОХИ ({CUSTOM_PERIODS[-1][2]}):")
    for i, (_, row) in enumerate(recent_top.iterrows()):
        info.append(f"{i+1}. {COUNTRY_RU.get(row['recipient'], row['recipient'])}: {row[col]:.0f} {unit}")
    
    info.append("\n" + "─"*20 + "\nСОСТАВ МЕТРИКИ:")
    info.append("Сумма активностей (в ед.):\n1. Мед. проекты (Health)\n2. Институты Конфуция (CIs)\n3. Судебная дипломатия (GCI)")
    
    ax.text(1.03, 0.5, "\n".join(info), transform=ax.transAxes, va='center', ha='left', fontsize=10.5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=1.0', facecolor='#F8F9F9', edgecolor='#D5DBDB', alpha=0.95), zorder=10)

    fig.suptitle('Эволюция гуманитарного сотрудничества (GCI)', fontsize=22, fontweight='bold', x=0.5, y=0.95, ha='center')
    add_source(fig, "AidData, NBR")
    plt.subplots_adjust(left=0.08, right=0.76, top=0.88, bottom=0.12)
    plt.savefig('5_Rank_Humanitarian.jpg', dpi=300)