import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from china_config import load_data, add_source

df, _, _, _ = load_data()

if df is not None:
    rus = df[df['recipient'] == 'Russia'].copy()
    
    # ИСПОЛЬЗУЕМ ТОЛЬКО "ДОЛГИЕ" МЕТРИКИ (до 2024 г.)
    cols = {
        'dev_03_fdi_usd': 'Прямые инвестиции (FDI)',
        'sec_03_military_engagement_ct': 'Военная дипломатия (Визиты)',
        'sec_04_joint_exercise_ct': 'Военные учения'
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
        
        # --- УДАЛЕН ПУНКТИР (ax.plot) ---
        # ax.plot([0, 1], [val1, val2], color='black', alpha=0.3, linestyle='--', marker='o')
        
        # Логика цвета текста
        if val2 > val1:
            txt_color = '#27AE60' # Зеленый при росте
        else:
            txt_color = '#C0392B' # Красный при падении

        if val1 > 0:
            change = ((val2 - val1) / val1) * 100
            txt = f"{change:+.0f}%"
        else:
            txt = "Рост" if val2 > val1 else "0%"
            
        ax.set_title(col_name, fontweight='bold', fontsize=12)
        y_max = max(val1, val2) if max(val1, val2) > 0 else 1
        ax.set_ylim(0, y_max * 1.25)
        
        # Конвертация для FDI в миллиарды
        d1, d2 = val1, val2
        if "usd" in col_code: 
            d1 /= 1e9; d2 /= 1e9
            unit_fmt = "{:.2f} млрд $"
        else:
            unit_fmt = "{:.1f}"
            
        ax.text(0, bars[0].get_height(), unit_fmt.format(d1), ha='center', va='bottom', fontsize=11)
        ax.text(1, bars[1].get_height(), unit_fmt.format(d2), ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Плашка с процентом (динамический цвет)
        ax.text(0.5, y_max * 1.1, txt, ha='center', 
                bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round'), 
                fontsize=11, color=txt_color, fontweight='bold')

    legend_elements = [
        Patch(facecolor='#95A5A6', label='2013-2020 (BRI)'),
        Patch(facecolor='#C0392B', label='2021-2024 (Новые инициативы)')
    ]
    
    # --- НАСТРОЙКА ОТСТУПОВ ---
    # Легенду поднимаем чуть выше (bbox_to_anchor y=0.08)
    fig.legend(handles=legend_elements, loc='lower center', ncol=2, 
               bbox_to_anchor=(0.5, 0.08), fontsize=12, frameon=True)

    plt.suptitle('Россия 2024: Трансформация взаимодействия', fontsize=18, fontweight='bold', y=0.98)
    add_source(fig)
    
    # Увеличиваем нижний отступ (bottom=0.15), чтобы легенда не наезжала на Source
    plt.tight_layout(rect=[0, 0.15, 1, 0.95])
    
    plt.savefig('18_Russia_Pivot.jpg', dpi=300)
    print("Сохранен 18_Russia_Pivot.jpg")