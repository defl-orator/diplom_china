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


# 1. Глобальные настройки для элементов, где размер не задан явно
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'axes.titlesize': 18
})

# 2. Перехватываем методы Matplotlib, чтобы автоматически увеличить 
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

for method in['text', 'set_title', 'set_xlabel', 'set_ylabel', 'set_xticklabels', 'set_yticklabels', 'legend']:
    if hasattr(maxes.Axes, method):
        patch_matplotlib_method(maxes.Axes, method)

patch_matplotlib_method(mfig.Figure, 'text')
if hasattr(mfig.Figure, 'legend'):
    patch_matplotlib_method(mfig.Figure, 'legend')

# === КОНСТАНТЫ ===
plt.rcParams['font.family'] = 'Arial'
SOURCE_TEXT = "Source: Mapping China’s Borderlands Dataset (2025)"

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")

BORDER_COUNTRIES =[
    "Afghanistan", "Bhutan", "India", "Kazakhstan", "Kyrgyzstan",
    "Laos", "Mongolia", "Myanmar", "Nepal", "North Korea",
    "Pakistan", "Russia", "Tajikistan", "Vietnam",
    "Japan", "South Korea", "Philippines", "Malaysia", "Brunei", "Indonesia"
]

# === ПЕРЕМЕННЫЕ ===
# Экономика
GDI_COLS =['dev_03_fdi_usd', 'dev_01_currency_swap_p_usd']

# Безопасность
GSI_COLS =['sec_01_arms_transfer_tiv', 'sec_04_joint_exercise_ct', 'sec_03_military_engagement_ct']

# Гуманитарка
GCI_COLS = ['civ_05_judicial_engagement_ct'] 

RU_LABELS = {
    'gdi_idx': 'Экономика (FDI/Swaps)',
    'gsi_idx': 'Безопасность (Оружие/Учения)',
    'dev_03_fdi_usd': 'Прямые инвестиции (FDI)',
    'dev_01_currency_swap_p_usd': 'Валютные свопы',
    'sec_01_arms_transfer_tiv': 'Торговля оружием',
    'sec_04_joint_exercise_ct': 'Военные учения',
    'sec_03_military_engagement_ct': 'Военная дипломатия',
    'civ_05_judicial_engagement_ct': 'Судебная дипломатия'
}

COUNTRY_RU = {
    "Afghanistan": "Афганистан", "Bhutan": "Бутан", "India": "Индия",
    "Kazakhstan": "Казахстан", "Kyrgyzstan": "Киргизия", "Laos": "Лаос",
    "Mongolia": "Монголия", "Myanmar": "Мьянма", "Nepal": "Непал",
    "North Korea": "КНДР", "Pakistan": "Пакистан", "Russia": "Россия",
    "Tajikistan": "Таджикистан", "Vietnam": "Вьетнам", "Japan": "Япония",
    "South Korea": "Южная Корея", "Philippines": "Филиппины",
    "Malaysia": "Малайзия", "Brunei": "Бруней", "Indonesia": "Индонезия"
}

def add_source(fig, extra_sources=None, use_default=True):
    if use_default:
        text = SOURCE_TEXT
        if extra_sources:
            text += f", {extra_sources}"
    else:
        text = extra_sources if extra_sources else ""
        
    if text:
        # Увеличил размер шрифта источника здесь до 13
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
    except: return None

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
        print(f"Ошибка в china_config: {e}")
        return None, None, None, None