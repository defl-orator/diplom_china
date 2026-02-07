import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from china_config import load_data, add_source

# Группировка стран
GROUPS_MAP = {
    "ПОЛНАЯ ПОДДЕРЖКА": ["Bhutan", "Kazakhstan", "Kyrgyzstan", "Laos", "Mongolia", "Myanmar", "Pakistan", "Russia", "Tajikistan", "Malaysia", "Brunei"],
    "ЧАСТИЧНО": ["Nepal", "Vietnam", "Philippines", "Indonesia"],
    "МОЛЧАНИЕ": ["Afghanistan", "North Korea", "South Korea"],
    "ПРОТИВ": ["India", "Japan"]
}

def get_group(name):
    for k, v in GROUPS_MAP.items():
        if name in v: return k
    return "UNKNOWN"

df, _, _, _ = load_data()

def calculate_group_performance():
    if df is None: return

    # --- ПОДГОТОВКА МЕТРИК ---
    df['Экономика'] = df[['dev_03_fdi_usd', 'dev_02_infrastructure_usd']].sum(axis=1) / 1e9
    df['Безопасность'] = (df['sec_01_arms_transfer_orders_ct'] + 
                          df['sec_03_military_engagement_ct'] + 
                          df['sec_04_joint_exercise_ct'])
    df['Гуманитарка'] = df[['civ_02_healthcare_ct', 'civ_06_ci_ct', 'civ_05_judicial_engagement_ct']].sum(axis=1)

    df['Group'] = df['recipient'].apply(get_group)

    p1 = df[df['year'].between(2013, 2020)]
    p2 = df[df['year'].between(2021, 2024)]

    dimensions = ['Экономика', 'Безопасность', 'Гуманитарка']
    group_names = list(GROUPS_MAP.keys())

    fig, axes = plt.subplots(2, 2, figsize=(24, 17))
    
    fig.suptitle("Сравнительный анализ внешнеполитических профилей КНР (2013-2024)\n(Среднегодовые показатели на одну страну в группе)", 
                 fontsize=28, fontweight='bold', x=0.5, y=0.97)

    legend_handles = []

    for i, g_name in enumerate(group_names):
        ax = axes[i // 2, i % 2]
        
        data_p1 = [p1[p1['Group'] == g_name][d].mean() for d in dimensions]
        data_p2 = [p2[p2['Group'] == g_name][d].mean() for d in dimensions]

        data_p1 = [0 if (np.isnan(v) or v < 0) else v for v in data_p1]
        data_p2 = [0 if (np.isnan(v) or v < 0) else v for v in data_p2]

        x = np.arange(len(dimensions))
        width = 0.35

        h1 = ax.bar(x - width/2, data_p1, width, color='#AED6F1', edgecolor='white')
        h2 = ax.bar(x + width/2, data_p2, width, color='#2E86C1', edgecolor='white')
        
        if not legend_handles: legend_handles = [h1, h2]

        ax.set_title(f"Группа: {g_name}", fontsize=21, fontweight='bold', pad=25, color='#2C3E50')
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions, fontsize=15, fontweight='bold')
        ax.grid(axis='y', linestyle=':', alpha=0.6)
        
        max_val = max(data_p1 + data_p2) if max(data_p1 + data_p2) > 0 else 1
        ax.set_ylim(0, max_val * 1.45)

        for j in range(len(dimensions)):
            v1, v2 = data_p1[j], data_p2[j]
            
            # Логика подписей для исключения наложения
            if v1 == 0 and v2 == 0:
                # Полное отсутствие данных
                ax.text(x[j], 0.2, "0.0", ha='center', va='bottom', fontsize=12, color='#BDC3C7', fontweight='bold')
            elif v2 == 0 and v1 > 0:
                # Падение до нуля (Молчание) - пишем только проценты
                ax.text(x[j] + width/2, 0.2, "-100.0%", ha='center', va='bottom', color='#E74C3C', fontweight='black', fontsize=13)
            elif v1 > 0:
                # Стандартный расчет
                diff = ((v2 - v1) / v1) * 100
                color = '#27AE60' if diff >= 0 else '#E74C3C'
                ax.text(x[j] + width/2, v2 + (max_val * 0.02), f"{diff:+.1f}%", 
                        ha='center', va='bottom', color=color, fontweight='black', fontsize=13)
            elif v2 > 0:
                # Новая активность
                ax.text(x[j] + width/2, v2 + (max_val * 0.02), "NEW", 
                        ha='center', va='bottom', color='#27AE60', fontweight='black', fontsize=13)

    # --- ЛЕГЕНДА МЕТРИК (СЛЕВА ВНИЗУ) ---
    metric_info = (
        "ПОЯСНЕНИЕ МЕТРИК (ОДНОРОДНАЯ ШКАЛА):\n"
        "• Экономика: ср. объем инвестиций и проектов (млрд $ / год)\n"
        "• Безопасность: ср. кол-во заказов оружия, встреч и учений (ед. / год)\n"
        "• Гуманитарка: ср. кол-во проектов в медицине, образовании и праве (ед. / год)"
    )
    # y=0.05 прижимает легенду ниже к краю
    fig.text(0.08, 0.05, metric_info, fontsize=12, style='italic', color='#566573', 
             bbox=dict(boxstyle='round,pad=1', facecolor='#FDFEFE', edgecolor='#D5DBDB', alpha=0.9))

    # --- ЛЕГЕНДА ЭПОХ (СПРАВА ВНИЗУ) ---
    fig.legend(legend_handles, ['Эпоха BRI (2013-2020)', 'Эпоха Инициатив (2021-2024)'], 
               loc='lower right', ncol=1, fontsize=15, frameon=True, bbox_to_anchor=(0.92, 0.05))

    CUSTOM_SOURCES = "Sources: IMF, AidData, SIPRI, NDU. Values show annual averages per country in each group."
    add_source(fig, CUSTOM_SOURCES, use_default=False)
    
    plt.subplots_adjust(left=0.08, right=0.92, top=0.84, bottom=0.15, hspace=0.45, wspace=0.2)
    plt.savefig("20_Initiative_Performance.jpg", dpi=300)
    plt.close()

if __name__ == "__main__":
    calculate_group_performance()