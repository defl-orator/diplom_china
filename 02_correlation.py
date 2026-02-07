import matplotlib.pyplot as plt
import seaborn as sns
from china_config import load_data, add_source, GDI_COLS, GSI_COLS, GCI_COLS

df, _, _, _ = load_data()

RU_LABELS = {
    'dev_02_infrastructure_usd': 'Инфраструктура',
    'dev_03_fdi_usd': 'Прямые инвестиции',
    'dev_04_sez_usd': 'Спец. зоны (ОЭЗ)',
    'sec_01_arms_transfer_tiv': 'Оружие',
    'sec_04_joint_exercise_ct': 'Учения',
    'sec_02_surveillance_usd': 'Наблюдение',
    'civ_03_total_visits_ct': 'Визиты',
    'civ_06_ci_cc_ct': 'Ин-ты Конфуция',
    'civ_04_csps_ct': 'Медиа'
}

if df is not None:
    plt.figure(figsize=(12, 10))
    cols = GDI_COLS + GSI_COLS + GCI_COLS
    corr_data = df[cols].corr()
    
    corr_data.columns = [RU_LABELS.get(c, c) for c in corr_data.columns]
    corr_data.index = [RU_LABELS.get(c, c) for c in corr_data.index]
    
    sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, fmt=".2f",
                linewidths=1, linecolor='white')
    
    plt.title('Взаимосвязь инструментов влияния КНР', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    add_source(plt.gcf())
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig('5_Correlation.jpg', dpi=300)
    print("Сохранен 5_Correlation.jpg")