import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox
from china_config import get_circular_flag, COUNTRY_RU, add_source

GROUPS = {
    "SUPPORTED_ALL": {
        "countries": ["Bhutan", "Kazakhstan", "Kyrgyzstan", "Laos", "Mongolia", "Myanmar", "Pakistan", "Russia", "Tajikistan", "Malaysia", "Brunei"],
        "label": "ПОЛНАЯ ПОДДЕРЖКА", "color": "#E8F8F5", "text_color": "#148F77", "angle": 180
    },
    "PARTIALLY": {
        "countries": ["Nepal", "Vietnam", "Philippines", "Indonesia"],
        "label": "ЧАСТИЧНО *", "color": "#FEF9E7", "text_color": "#B7950B", "angle": 70
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
    "Источник: составлено автором на основе официальных данных МИД КНР и правительств государств пограничного пояса,\n"
    "а также материалов аналитических центров и СМИ (The National Bureau of Asian Research, Chatham House, Lowy Institute,\n"
    "Valdai Club, TASS, The Kathmandu Post, Daily NK, Global Times, China Daily, Vientiane Times, Astana Times и др.)."
)

PARTIAL_EXPLANATION = [
    ("Непал", "Поддерживает только GDI. Официально\nотвергает GSI/GCI, считая их угрозой\nполитике неприсоединения."),
    ("Вьетнам", "Поддерживает GDI. GSI и GCI одобряются\nформально в рамках «сообщества единой\nсудьбы», но без жестких обязательств."),
    ("Филиппины", "Приоритет международного права\n(UNCLOS). Резкая критика практики GSI\nна фоне конфликта в ЮКМ."),
    ("Индонезия", "Поддерживает GDI/GGI. Дистанцируется\nот военного аспекта GSI, делая ставку\nна автономию АСЕАН.")
]

def get_cartesian(r, alpha_deg):
    alpha_rad = np.deg2rad(alpha_deg)
    return r * np.cos(alpha_rad), r * np.sin(alpha_rad)

def draw_info_table(ax, center_x):
    box_w = 13.0
    box_h = 10.8
    box_x = 9.0
    box_y = -5.4
    
    rect = patches.Rectangle((box_x, box_y), box_w, box_h, linewidth=0, 
                             facecolor='#FEF9E7', alpha=0.5, zorder=0)
    ax.add_patch(rect)
    
    left_border = patches.Rectangle((box_x, box_y), 0.15, box_h, linewidth=0,
                                    facecolor='#B7950B', alpha=0.8, zorder=1)
    ax.add_patch(left_border)
    
    text_x = box_x + 0.8
    
    ax.text(text_x, box_y + box_h - 1.0, "* Позиция группы «ЧАСТИЧНО»:", 
            fontsize=13, fontweight='bold', color='#B7950B', ha='left')
    
    start_y = box_y + box_h - 2.2
    for country, text in PARTIAL_EXPLANATION:
        ax.text(text_x, start_y, f"{country}:", fontsize=11, 
                fontweight='bold', color='#333333', ha='left')
        ax.text(text_x, start_y - 0.4, text, fontsize=9.5, 
                va='top', style='italic', color='#555555', ha='left', linespacing=1.2)
        start_y -= 2.1

def plot_circular_groups():
    fig, ax = plt.subplots(figsize=(22, 16))

    center_x = -3 
    ax.set_xlim(-15, 18) 
    ax.set_ylim(-12, 12)
    ax.set_aspect('equal')
    ax.axis('off')

    current_angle = 0
    
    for key, data in GROUPS.items():
        start_angle = current_angle
        end_angle = current_angle + data["angle"]
        mid_angle = (start_angle + end_angle) / 2
        
        wedge = patches.Wedge(center=(center_x, 0), r=10, theta1=start_angle, theta2=end_angle, 
                              facecolor=data["color"], edgecolor='white', linewidth=3, zorder=1)
        ax.add_patch(wedge)

        label_r = 10.8
        lx, ly = get_cartesian(label_r, mid_angle)
        lx += center_x
        
        rotation = mid_angle if 0 <= mid_angle <= 180 else mid_angle + 180
        ax.text(lx, ly, data["label"], ha='center', va='center', fontsize=16, 
                fontweight='bold', color=data["text_color"], rotation=rotation-90)

        countries = data["countries"]
        num = len(countries)

        for i, country in enumerate(countries):
            if key == "SUPPORTED_ALL":
                row = 0 if i < 6 else 1
                row_num = 6 if row == 0 else 5
                angle_in_wedge = start_angle + (data["angle"] / (row_num + 1)) * (i % row_num + 1)
                r = [7.8, 4.8][row]
            elif key == "PARTIALLY" or key == "NOTHING_SAID":
                angle_in_wedge = start_angle + (data["angle"] / (num + 1)) * (i + 1)
                r = [5.8, 8.2][i % 2]
            else:
                angle_in_wedge = start_angle + (data["angle"] / (num + 1)) * (i + 1)
                r = 7.0

            fx, fy = get_cartesian(r, angle_in_wedge)
            fx += center_x
            
            flag = get_circular_flag(country, zoom=0.14)
            if flag:
                ax.add_artist(AnnotationBbox(flag, (fx, fy), frameon=False, zorder=3))
                ax.text(fx, fy - 0.7, COUNTRY_RU.get(country, country[:5]), 
                        ha='center', va='top', fontsize=10, fontweight='bold', zorder=4)

        current_angle += data["angle"]

    draw_info_table(ax, center_x)

    add_source(fig, SITE_SOURCES, use_default=False)
    
    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.1)
    plt.savefig("Initiative_Consensus.jpg", dpi=300)
    plt.close()

if __name__ == "__main__":
    plot_circular_groups()