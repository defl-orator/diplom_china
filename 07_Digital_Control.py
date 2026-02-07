import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from china_config import load_data, add_source, COUNTRY_RU

df, _, _, _ = load_data()
col_surv = 'sec_02_surveillance_usd'

if df is not None:
    # Разделяем на периоды
    df['period'] = df['year'].apply(lambda x: '2013-2020 (BRI)' if 2013 <= x <= 2020 else '2021+ (GSI Era)' if x >= 2021 else 'Other')
    
    # Считаем среднегодовые расходы, чтобы сравнение было честным (периоды разной длины)
    stats = df[df['period'] != 'Other'].groupby(['period', 'recipient'])[col_surv].mean().reset_index()
    
    # Берем ТОП-8 стран по суммарной активности
    top_recipients = stats.groupby('recipient')[col_surv].sum().sort_values(ascending=False).head(8).index
    plot_data = stats[stats['recipient'].isin(top_recipients)].copy()
    plot_data['recipient_ru'] = plot_data['recipient'].map(COUNTRY_RU).fillna(plot_data['recipient'])
    
    pivot_df = plot_data.pivot(index='recipient_ru', columns='period', values=col_surv).fillna(0) / 1e6
    pivot_df = pivot_df.sort_values('2013-2020 (BRI)', ascending=True)

    ax = pivot_df.plot(kind='barh', figsize=(12, 8), color=['#BDC3C7', '#8E44AD'], width=0.8)
    
    plt.title('Технологии слежения (Surveillance): Сравнение среднегодовых затрат', fontsize=16, fontweight='bold')
    plt.xlabel('Средний объем проектов в год (млн USD)', fontweight='bold')
    plt.ylabel('')
    
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)
    add_source(plt.gcf())
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    plt.savefig('9_Digital_Surveillance_Comp.jpg', dpi=300)