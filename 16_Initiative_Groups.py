import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox
from china_config import get_circular_flag, COUNTRY_RU, add_source

# Актуальные группы данных
GROUPS = {
    "SUPPORTED_ALL": {
        "countries": ["Bhutan", "Kazakhstan", "Kyrgyzstan", "Laos", "Mongolia", "Myanmar", "Pakistan", "Russia", "Tajikistan", "Malaysia", "Brunei"],
        "label": "ПОЛНАЯ ПОДДЕРЖКА", "color": "#E8F8F5", "text_color": "#148F77", "angle": 180
    },
    "PARTIALLY": {
        "countries": ["Nepal", "Vietnam", "Philippines", "Indonesia"],
        "label": "ЧАСТИЧНО", "color": "#FEF9E7", "text_color": "#B7950B", "angle": 70
    },
    "NOTHING_SAID": {
        "countries": ["Afghanistan", "North Korea", "South Korea"],
        "label": "НЕТ ПОЗИЦИИ", "color": "#F8F9F9", "text_color": "#707B7C", "angle": 60
    },
    "NOT_SUPPORTED": {
        "countries": ["India", "Japan"],
        "label": "НЕ ПОДДЕРЖАЛИ", "color": "#FDEDEC", "text_color": "#CB4335", "angle": 50
    }
}

SITE_SOURCES = (
    "Sources: fmprc.gov.cn, gov.cn, mofa.gov.mm, cpec.gov.pk, mofa.go.jp, mofa.go.kr, mea.gov.in, nbr.org, "
    "chathamhouse.org, lowyinstitute.org, valdaiclub.com, thinkchina.sg, Reuters, AP News, The Kathmandu Post, "
    "The Diplomat, Global Times, China Daily, Vientiane Times, Astana Times, Manila Times, NDTV."
)

def get_cartesian(r, alpha_deg):
    alpha_rad = np.deg2rad(alpha_deg)
    return r * np.cos(alpha_rad), r * np.sin(alpha_rad)

def plot_circular_groups():
    fig, ax = plt.subplots(figsize=(18, 18))
    fig.suptitle("Консенсус пограничных стран по Глобальным Инициативам КНР (2021-2024)", 
                 fontsize=28, fontweight='bold', y=0.95)

    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.axis('off')

    current_angle = 0
    
    for key, data in GROUPS.items():
        start_angle = current_angle
        end_angle = current_angle + data["angle"]
        mid_angle = (start_angle + end_angle) / 2
        
        # 1. Рисуем сегмент (теперь сплошной, до самого центра)
        wedge = patches.Wedge(center=(0, 0), r=10, theta1=start_angle, theta2=end_angle, 
                              facecolor=data["color"], edgecolor='white', linewidth=3, zorder=1)
        ax.add_patch(wedge)

        # 2. Добавляем название категории снаружи круга
        label_r = 10.8
        lx, ly = get_cartesian(label_r, mid_angle)
        
        # Выравнивание текста в зависимости от угла
        rotation = mid_angle if 0 <= mid_angle <= 180 else mid_angle + 180
        ax.text(lx, ly, data["label"], ha='center', va='center', fontsize=16, 
                fontweight='bold', color=data["text_color"], rotation=rotation-90)

        # 3. Расставляем страны (флаги)
        countries = data["countries"]
        num = len(countries)
        
        # Настраиваем радиусы, чтобы флаги красиво заполняли сектор
        if num > 6:
            radii = [7.8, 4.8] # Два ряда для большой группы
        else:
            radii = [6.5] # Один ряд для маленьких групп

        for i, country in enumerate(countries):
            r_idx = i % len(radii)
            
            if num == 11: # Специальная раскладка для 11 стран (6 снаружи, 5 внутри)
                row = 0 if i < 6 else 1
                row_num = 6 if row == 0 else 5
                angle_in_wedge = start_angle + (data["angle"] / (row_num + 1)) * (i % row_num + 1)
                r = radii[row]
            else:
                angle_in_wedge = start_angle + (data["angle"] / (num + 1)) * (i + 1)
                r = radii[0]

            fx, fy = get_cartesian(r, angle_in_wedge)
            
            flag = get_circular_flag(country, zoom=0.14)
            if flag:
                ax.add_artist(AnnotationBbox(flag, (fx, fy), frameon=False, zorder=3))
                # Название страны под флагом
                ax.text(fx, fy - 0.9, COUNTRY_RU.get(country, country[:5]), 
                        ha='center', fontsize=10, fontweight='bold', zorder=4)

        current_angle += data["angle"]

    add_source(fig, SITE_SOURCES, use_default=False)
    
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    plt.savefig("19_Initiative_Consensus.jpg", dpi=300)
    plt.close()

if __name__ == "__main__":
    plot_circular_groups()