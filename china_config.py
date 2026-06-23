import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as maxes
import matplotlib.figure as mfig
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageOps, ImageDraw
import os
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns

# === LANGUAGE SETTING ===
# Choose 'EN' for English or 'RU' for Russian
LANG = 'RU'

# === AUTOMATED OUTPUT DIRECTORY ROUTING ===
OUTPUT_DIR = f"charts_results_{LANG.lower()}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Patch plt.savefig and Figure.savefig to redirect images to OUTPUT_DIR automatically
orig_plt_savefig = plt.savefig
def patched_plt_savefig(fname, *args, **kwargs):
    if isinstance(fname, str):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        # Apply routing only if filename is a flat string without path structure
        if not fname.startswith(OUTPUT_DIR) and not os.path.dirname(fname):
            fname = os.path.join(OUTPUT_DIR, fname)
    return orig_plt_savefig(fname, *args, **kwargs)
plt.savefig = patched_plt_savefig

orig_fig_savefig = mfig.Figure.savefig
def patched_fig_savefig(self, fname, *args, **kwargs):
    if isinstance(fname, str):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        if not fname.startswith(OUTPUT_DIR) and not os.path.dirname(fname):
            fname = os.path.join(OUTPUT_DIR, fname)
    return orig_fig_savefig(self, fname, *args, **kwargs)
mfig.Figure.savefig = patched_fig_savefig


# === GLOBAL MATPLOTLIB PARAMETERS ===
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'axes.titlesize': 18
})

# Intercept Matplotlib methods to apply the scale factor dynamically
SCALE_FACTOR = 1.4 

def patch_matplotlib_method(cls, method_name):
    orig_method = getattr(cls, method_name)
    def hooked_method(self, *args, **kwargs):
        if 'fontsize' in kwargs and isinstance(kwargs['fontsize'], (int, float)):
            kwargs['fontsize'] *= SCALE_FACTOR
        if 'size' in kwargs and isinstance(kwargs['size'], (int, float)):
            kwargs['size'] *= SCALE_FACTOR
        return orig_method(self, *args, **kwargs)
    setattr(cls, method_name, hooked_method)

for method in ['text', 'set_title', 'set_xlabel', 'set_ylabel', 'set_xticklabels', 'set_yticklabels', 'legend']:
    if hasattr(maxes.Axes, method):
        patch_matplotlib_method(maxes.Axes, method)

patch_matplotlib_method(mfig.Figure, 'text')
if hasattr(mfig.Figure, 'legend'):
    patch_matplotlib_method(mfig.Figure, 'legend')

plt.rcParams['font.family'] = 'Arial'
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")

# === DATA CONSTANTS ===
BORDER_COUNTRIES = [
    "Afghanistan", "Bhutan", "India", "Kazakhstan", "Kyrgyzstan",
    "Laos", "Mongolia", "Myanmar", "Nepal", "North Korea",
    "Pakistan", "Russia", "Tajikistan", "Vietnam",
    "Japan", "South Korea", "Philippines", "Malaysia", "Brunei", "Indonesia"
]

GDI_COLS = ['dev_03_fdi_usd', 'dev_01_currency_swap_p_usd']
GSI_COLS = ['sec_01_arms_transfer_tiv', 'sec_04_joint_exercise_ct', 'sec_03_military_engagement_ct']
GCI_COLS = ['civ_05_judicial_engagement_ct'] 

# === TRANSLATION TABLES ===
SOURCE_TEXT = {
    'EN': "Source: Mapping China’s Borderlands Dataset (2025)",
    'RU': "Источник: База данных Mapping China’s Borderlands (2025)"
}

LABELS = {
    'EN': {
        'gdi_idx': 'Economy (FDI/Swaps)',
        'gsi_idx': 'Security (Arms/Drills)',
        'dev_03_fdi_usd': 'Foreign Direct Investment (FDI)',
        'dev_01_currency_swap_p_usd': 'Currency Swaps',
        'sec_01_arms_transfer_tiv': 'Arms Trade',
        'sec_04_joint_exercise_ct': 'Joint Exercises',
        'sec_03_military_engagement_ct': 'Military Diplomacy',
        'civ_05_judicial_engagement_ct': 'Judicial Engagement'
    },
    'RU': {
        'gdi_idx': 'Экономика (FDI/Свопы)',
        'gsi_idx': 'Безопасность (Оружие/Учения)',
        'dev_03_fdi_usd': 'Прямые инвестиции (FDI)',
        'dev_01_currency_swap_p_usd': 'Валютные свопы',
        'sec_01_arms_transfer_tiv': 'Торговля оружием',
        'sec_04_joint_exercise_ct': 'Военные учения',
        'sec_03_military_engagement_ct': 'Военная дипломатия',
        'civ_05_judicial_engagement_ct': 'Судебная дипломатия'
    }
}

COUNTRY_NAMES = {
    'EN': {c: c for c in BORDER_COUNTRIES},
    'RU': {
        "Afghanistan": "Афганистан", "Bhutan": "Бутан", "India": "Индия",
        "Kazakhstan": "Казахстан", "Kyrgyzstan": "Киргизия", "Laos": "Лаос",
        "Mongolia": "Монголия", "Myanmar": "Мьянма", "Nepal": "Непал",
        "North Korea": "КНДР", "Pakistan": "Пакистан", "Russia": "Россия",
        "Tajikistan": "Таджикистан", "Vietnam": "Вьетнам", "Japan": "Япония",
        "South Korea": "Южная Корея", "Philippines": "Филиппины",
        "Malaysia": "Малайзия", "Brunei": "Бруней", "Indonesia": "Индонезия"
    }
}

TEXTS = {
    'EN': {
        'supported_all': 'FULL SUPPORT',
        'partially': 'PARTIALLY',
        'nothing_said': 'NO POSITION / SILENCE',
        'not_supported': 'DID NOT SUPPORT',
        'russia_pivot_title_fdi': 'Foreign Direct Investment (FDI)',
        'russia_pivot_title_mil': 'Military Diplomacy (Visits)',
        'russia_pivot_title_ex': 'Joint Exercises',
        'growth': 'Growth',
        'bri_epoch': '2013-2020 (BRI)',
        'initiatives_epoch': '2021-2024 (Global Initiatives)',
        'average_neighbor': 'Average Neighbor Level',
        'anomaly_zone': 'Zone of abnormally\nhigh activity',
        'z_score_label': 'Z-Score (Deviation from neighbor average in sigma units)',
        'period_legend_title': 'Period',
        'military_col_label': 'Average annual military events (arms orders + meetings + drills)',
        'pre_2021': 'Pre-2021',
        'post_2021': 'Post-2021',
        'bri_avg_level': 'BRI Era (average level)',
        'growth_activity': 'Activity Growth',
        'decline_activity': 'Activity Decline',
        'sea_border': 'Maritime Border',
        'land_border': 'Land Border',
        'economy_gdi': 'Economy (GDI)',
        'security_gsi': 'Security (GSI)',
        'humanitarian_gci': 'Humanitarian (GCI)',
        'average_engagement': 'Average engagement index',
        'initiatives_sea': '2021-2024 (Initiatives - Sea)',
        'initiatives_land': '2021-2024 (Initiatives - Land)',
        'digital_surveillance_title': 'Digital Surveillance',
        'average_annual_projects': 'Average annual project volume (million USD)',
        'humanitarian_index': 'Humanitarian Index',
        'events': 'events',
        'billion_usd': 'billion USD',
        'billion_usd_short': 'bn $',
        'million_usd': 'million USD',
        'million_usd_short': 'M $',
        'new': 'NEW',
        'group': 'Group',
        'moderate_group': 'Moderate interaction group',
        'gdi_leaders': 'Economic partners (GDI leaders)',
        'gsi_leaders': 'Security partners (GSI leaders)',
        'russia': 'Russia',
        'both_leaders': 'Comprehensive Leaders (Top-5 GDI + GSI)',
        'gdi_leaders_top': 'Economic Leaders (Top-5 GDI)',
        'gsi_leaders_top': 'Security Leaders (Top-5 GSI)',
    },
    'RU': {
        'supported_all': 'ПОЛНАЯ ПОДДЕРЖКА',
        'partially': 'ЧАСТИЧНО',
        'nothing_said': 'МОЛЧАНИЕ / НЕТ ПОЗИЦИИ',
        'not_supported': 'НЕ ПОДДЕРЖАЛИ',
        'russia_pivot_title_fdi': 'Прямые инвестиции (FDI)',
        'russia_pivot_title_mil': 'Военная дипломатия (Визиты)',
        'russia_pivot_title_ex': 'Военные учения',
        'growth': 'Рост',
        'bri_epoch': '2013-2020 (Эпоха BRI)',
        'initiatives_epoch': '2021-2024 (Эпоха Инициатив)',
        'average_neighbor': 'Средний уровень соседа',
        'anomaly_zone': 'Зона аномально\nвысокой активности',
        'z_score_label': 'Z-Score (Отклонение от среднего соседа в единицах сигма)',
        'period_legend_title': 'Период',
        'military_col_label': 'Среднее количество военных контактов и сделок в год (ед.)',
        'pre_2021': 'До 2021',
        'post_2021': 'После 2021',
        'bri_avg_level': 'Эпоха BRI (ср. уровень)',
        'growth_activity': 'Рост активности',
        'decline_activity': 'Спад активности',
        'sea_border': 'Морская граница',
        'land_border': 'Сухопутная граница',
        'economy_gdi': 'Экономика (GDI)',
        'security_gsi': 'Безопасность (GSI)',
        'humanitarian_gci': 'Гуманитарка (GCI)',
        'average_engagement': 'Средний индекс вовлеченности',
        'initiatives_sea': '2021-2024 (Инициативы - Море)',
        'initiatives_land': '2021-2024 (Инициативы - Суша)',
        'digital_surveillance_title': 'Технологии слежения',
        'average_annual_projects': 'Средний объем проектов в год (млн USD)',
        'humanitarian_index': 'Гуманитарный индекс',
        'events': 'событий',
        'billion_usd': 'млрд $',
        'billion_usd_short': 'млрд $',
        'million_usd': 'млн USD',
        'million_usd_short': 'млн $',
        'new': 'NEW',
        'group': 'Группа',
        'moderate_group': 'Группа умеренного взаимодействия',
        'gdi_leaders': 'Экономические партнеры (GDI лидеры)',
        'gsi_leaders': 'Партнеры в сфере безопасности (GSI лидеры)',
        'russia': 'Россия',
        'both_leaders': 'Лидеры в обеих сферах (Топ-5 GDI + GSI)',
        'gdi_leaders_top': 'Лидеры экономики (Топ-5 GDI)',
        'gsi_leaders_top': 'Лидеры безопасности (Топ-5 GSI)',
    }
}

INFO_TABLE_TEXTS = {
    'EN': {
        'title_partially': "* Position of the 'PARTIALLY' group:",
        'title_no_pos': "** Position of the 'NO POSITION' group:",
        'nepal_title': "Nepal",
        'nepal_desc': "Supports GDI only. Officially rejects GSI/GCI,\nviewing them as a threat to its policy of\nnon-alignment.",
        'phil_title': "Philippines",
        'phil_desc': "Member of the 'Group of Friends of GDI', but\nstrongly rejects GSI/GCI amid rising conflicts\nin the South China Sea.",
        'sk_title': "South Korea",
        'sk_desc': "Does not officially support any initiative, but\npragmatically develops economic partnership\n(GDI/GCI).",
        'source_text': "Source: compiled by the author based on official data from the MFA of the PRC and governments of border belt countries,\nas well as materials from think tanks and media (The National Bureau of Asian Research, Chatham House, Lowy Institute, etc.)"
    },
    'RU': {
        'title_partially': "* Позиция группы «ЧАСТИЧНО»:",
        'title_no_pos': "** Позиция группы «НЕТ ПОЗИЦИИ»:",
        'nepal_title': "Непал",
        'nepal_desc': "Поддерживает только GDI. Официально\nотвергает GSI/GCI, считая их угрозой\nполитике неприсоединения.",
        'phil_title': "Филиппины",
        'phil_desc': "Входит в «Группу друзей GDI», но резко\nкритикует и отвергает GSI/GGI на фоне\nобострения конфликта в ЮКМ.",
        'sk_title': "Южная Корея",
        'sk_desc': "Официально не поддерживает ни одну\nиз инициатив, но прагматично развивает\nэкономическое партнерство (GDI/GGI).",
        'source_text': "Источник: составлено автором на основе официальных данных МИД КНР и правительств государств пограничного пояса,\nа также материалов аналитических центров и СМИ (The National Bureau of Asian Research, Chatham House, Lowy Institute, и др.)"
    }
}

# === TRANSLATION HELPERS ===
def get_label(key):
    return LABELS[LANG].get(key, key)

def get_country(name):
    return COUNTRY_NAMES[LANG].get(name, name)

def get_text(key):
    return TEXTS[LANG].get(key, key)

def add_source(fig, extra_sources=None, use_default=True):
    if use_default:
        text = SOURCE_TEXT[LANG]
        if extra_sources:
            text += f", {extra_sources}"
    else:
        text = extra_sources if extra_sources else ""
        
    if text:
        plt.figtext(0.5, 0.015, text, ha="center", fontsize=13, style='italic', color='#444444', wrap=True)

def get_circular_flag(country_name, zoom=0.13):
    try:
        filename = f"{country_name.lower().strip()}.jpg"
        path = os.path.join(os.getcwd(), 'flags', filename) 
        if not os.path.exists(path): 
            path = os.path.join(os.getcwd(), filename)
            if not os.path.exists(path):
                return None
        img = Image.open(path).convert("RGBA")
        size = (300, 300)
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0); ImageDraw.Draw(mask).ellipse((0, 0) + size, fill=255)
        output = Image.new('RGBA', size, (0, 0, 0, 0)); output.paste(img, (0, 0), mask)
        ImageDraw.Draw(output).ellipse((0, 0) + size, outline=(80, 80, 80, 255), width=14)
        return OffsetImage(output, zoom=zoom)
    except: 
        return None

def load_data():
    try:
        df = pd.read_csv('china_data.csv', sep=None, engine='python', encoding='utf-8-sig', na_values='NA')
        df = df[df['recipient'].isin(BORDER_COUNTRIES)].copy()
        df['recipient'] = df['recipient'].str.strip()
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        all_cols = GDI_COLS + GSI_COLS + GCI_COLS
        for c in all_cols:
            if c not in df.columns: df[c] = 0
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        scaler = MinMaxScaler()
        
        df['gdi_idx'] = scaler.fit_transform(df[GDI_COLS].mean(axis=1).values.reshape(-1,1))
        df['gsi_idx'] = scaler.fit_transform(df[GSI_COLS].mean(axis=1).values.reshape(-1,1))
        df['gci_idx'] = scaler.fit_transform(df[GCI_COLS].values.reshape(-1,1))
        
        return df, 'sec_01_arms_transfer_tiv', 'dev_03_fdi_usd', 'sec_03_military_engagement_ct'
    except Exception as e:
        print(f"Error in china_config: {e}")
        return None, None, None, None