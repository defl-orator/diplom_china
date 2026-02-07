import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from china_config import load_data, add_source

df, _, _, _ = load_data()
LAND_NEIGHBORS = ["North Korea", "Russia", "Mongolia", "Kazakhstan", "Kyrgyzstan", "Tajikistan", "Afghanistan", "Pakistan", "India", "Nepal", "Bhutan", "Myanmar", "Laos", "Vietnam"]
SEA_NEIGHBORS = ["South Korea", "Japan", "Philippines", "Brunei", "Malaysia", "Indonesia"]

if df is not None:
    df['Border_Type'] = df['recipient'].apply(lambda x: 'Сухопутная граница' if x in LAND_NEIGHBORS else 'Морская граница' if x in SEA_NEIGHBORS else 'Other')
    df['Period'] = df['year'].apply(lambda x: '2013-2020 (BRI)' if 2013 <= x <= 2020 else '2021+ (Initiatives)' if x >= 2021 else 'Other')
    
    # Фильтруем
    clean_df = df[(df['Border_Type'] != 'Other') & (df['Period'] != 'Other')]
    
    # Группируем по типу границы, периоду и считаем средние валидные индексы
    geo_stats = clean_df.groupby(['Border_Type', 'Period'])[['gdi_idx', 'gsi_idx']].mean().reset_index()
    
    # Переводим в "длинный" формат для отрисовки
    melted = geo_stats.melt(id_vars=['Border_Type', 'Period'], var_name='Index', value_name='Value')
    melted['Index'] = melted['Index'].map({'gdi_idx': 'Экономика (GDI)', 'gsi_idx': 'Безопасность (GSI)'})

    plt.figure(figsize=(14, 8))
    # Рисуем с разделением по типам границ и периодам
    g = sns.barplot(data=melted, x='Index', y='Value', hue='Period', color=None, palette=['#BDC3C7', '#E67E22'], errorbar=None)
    
    # Настройка осей для двух групп (Сухопутные и Морские)
    # Сделаем два сабплота для наглядности
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
    
    for ax, b_type in zip([ax1, ax2], ['Морская граница', 'Сухопутная граница']):
        subset = melted[melted['Border_Type'] == b_type]
        sns.barplot(data=subset, x='Index', y='Value', hue='Period', palette=['#BDC3C7', '#2980B9' if 'Мор' in b_type else '#C0392B'], ax=ax)
        ax.set_title(b_type, fontweight='bold', fontsize=14)
        ax.set_xlabel('')
        ax.set_ylabel('Средний индекс вовлеченности' if ax == ax1 else '')
        ax.get_legend().remove()

    plt.suptitle('Сравнение стратегий: Морские vs Сухопутные соседи (До и После 2021)', fontsize=18, fontweight='bold', y=0.98)
    
    # Общая легенда
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#BDC3C7', label='2013-2020 (BRI)'),
        Patch(facecolor='#2980B9', label='2021-2024 (Инициативы - Море)'),
        Patch(facecolor='#C0392B', label='2021-2024 (Инициативы - Суша)')
    ]
    
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, 
               bbox_to_anchor=(0.5, 0.05), frameon=True)
    
    add_source(fig)
    plt.tight_layout(rect=[0, 0.12, 1, 0.92])
    
    plt.savefig('12_Land_vs_Sea_Comp.jpg', dpi=300)
    print("Готов 12_Land_vs_Sea_Comp.jpg")