import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox
from china_config import get_circular_flag, get_country, get_text, add_source, INFO_TABLE_TEXTS, LANG

GROUPS = {
    "SUPPORTED_ALL": {
        "countries": [
            "Bhutan", "Kazakhstan", "Kyrgyzstan", "Laos", "Mongolia", 
            "Myanmar", "Pakistan", "Russia", "Tajikistan", "Malaysia", 
            "Brunei", "Afghanistan", "North Korea", "Indonesia", "Vietnam"
        ],
        "label": get_text('supported_all'), "color": "#E8F8F5", "text_color": "#148F77", "angle": 240
    },
    "PARTIALLY": {
        "countries": ["Nepal", "Philippines"],
        "label": get_text('partially') + " *", "color": "#FEF9E7", "text_color": "#B7950B", "angle": 40
    },
    "NOTHING_SAID": {
        "countries": ["South Korea"],
        "label": get_text('nothing_said') + " **", "color": "#F8F9F9", "text_color": "#707B7C", "angle": 35
    },
    "NOT_SUPPORTED": {
        "countries": ["India", "Japan"],
        "label": get_text('not_supported'), "color": "#FDEDEC", "text_color": "#CB4335", "angle": 45
    }
}

def get_cartesian(r, alpha_deg):
    alpha_rad = np.deg2rad(alpha_deg)
    return r * np.cos(alpha_rad), r * np.sin(alpha_rad)

def draw_info_table(ax, center_x):
    texts_db = INFO_TABLE_TEXTS[LANG]
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
    
    # --- BLOCK 1: PARTIALLY (*) ---
    ax.text(text_x, box_y + box_h - 1.0, texts_db['title_partially'], 
            fontsize=12, fontweight='bold', color='#B7950B', ha='left')
    
    start_y = box_y + box_h - 2.0
    part_1 = [
        (get_country("Nepal"), texts_db['nepal_desc']),
        (get_country("Philippines"), texts_db['phil_desc'])
    ]
    for country, text in part_1:
        ax.text(text_x, start_y, f"{country}:", fontsize=10.5, 
                fontweight='bold', color='#333333', ha='left')
        ax.text(text_x, start_y - 0.35, text, fontsize=9.0, 
                va='top', style='italic', color='#555555', ha='left', linespacing=1.2)
        start_y -= 2.0
        
    # --- BLOCK 2: NO POSITION (**) ---
    ax.text(text_x, start_y, texts_db['title_no_pos'], 
            fontsize=12, fontweight='bold', color='#707B7C', ha='left')
    
    start_y -= 1.0
    part_2 = [
        (get_country("South Korea"), texts_db['sk_desc'])
    ]
    for country, text in part_2:
        ax.text(text_x, start_y, f"{country}:", fontsize=10.5, 
                fontweight='bold', color='#333333', ha='left')
        ax.text(text_x, start_y - 0.35, text, fontsize=9.0, 
                va='top', style='italic', color='#555555', ha='left', linespacing=1.2)
        start_y -= 2.0

def plot_circular_groups():
    fig, ax = plt.subplots(figsize=(22, 16))

    center_x = -3 
    ax.set_xlim(-15, 18) 
    ax.set_ylim(-12, 12)
    ax.set_aspect('equal')
    ax.axis('off')

    current_angle = -30
    
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
                row = 0 if i < 8 else 1
                inner_i = i if row == 0 else i - 8
                row_num = 8 if row == 0 else 7
                angle_in_wedge = start_angle + (data["angle"] / (row_num + 1)) * (inner_i + 1)
                r = [7.8, 4.8][row]
            elif key in ["PARTIALLY", "NOTHING_SAID"]:
                angle_in_wedge = start_angle + (data["angle"] / (num + 1)) * (i + 1)
                r = [5.8, 8.2][i % 2] if num > 1 else 7.0
            else:
                angle_in_wedge = start_angle + (data["angle"] / (num + 1)) * (i + 1)
                r = 7.0

            fx, fy = get_cartesian(r, angle_in_wedge)
            fx += center_x
            
            flag = get_circular_flag(country, zoom=0.14)
            if flag:
                ax.add_artist(AnnotationBbox(flag, (fx, fy), frameon=False, zorder=3))
                ax.text(fx, fy - 0.7, get_country(country)[:12], 
                        ha='center', va='top', fontsize=10, fontweight='bold', zorder=4)

        current_angle += data["angle"]

    draw_info_table(ax, center_x)
    add_source(fig, INFO_TABLE_TEXTS[LANG]['source_text'], use_default=False)
    
    plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.1)
    
    filename = f"Initiative_Consensus_{LANG}.jpg"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Saved {filename}")

if __name__ == "__main__":
    plot_circular_groups()