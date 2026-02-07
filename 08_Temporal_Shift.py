import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from china_config import load_data, add_source

df, _, _, _ = load_data()

if df is not None:
    # Оставляем данные только с 2013 года (начало активной политики Си)
    df_f = df[df['year'] >= 2013].copy()
    
    # Разделяем на периоды вокруг 2021 года
    df_f['period'] = df_f['year'].apply(lambda x: '2013-2020 (Эпоха BRI)' if x < 2021 else '2021-2024 (Эпоха Инициатив)')
    
    # Группируем по периодам и странам, считая среднее
    # Используем только GDI и GSI, так как по GCI данные за 2021+ неполные
    period_stats = df_f.groupby(['period', 'recipient'])[['gdi_idx', 'gsi_idx']].mean().reset_index()
    
    melted = period_stats.melt(id_vars=['period', 'recipient'], var_name='Index', value_name='Score')
    melted['Index'] = melted['Index'].map({'gdi_idx': 'Экономика (GDI)', 'gsi_idx': 'Безопасность (GSI)'})

    plt.figure(figsize=(12, 8))
    sns.barplot(data=melted, x='Index', y='Score', hue='period', palette=['#BDC3C7', '#E74C3C'], errorbar=None)
    
    plt.title('Смещение акцентов: Эпоха BRI vs Глобальные инициативы (GDI/GSI)', fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Средний индекс влияния (0-1)', fontweight='bold')
    plt.xlabel('')
    
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    add_source(plt.gcf())
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    plt.savefig('11_Temporal_Shift.jpg', dpi=300)
    print("Сохранен 11_Temporal_Shift.jpg (сравнение 2013-2020 vs 2021+)")