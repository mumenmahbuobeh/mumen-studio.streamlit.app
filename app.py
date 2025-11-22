import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageFilter, ImageEnhance
import io

# ---------------------------------------------------------
# 1. Page Config (Must be first)
# ---------------------------------------------------------
st.set_page_config(page_title="MUMEN Brand AI", page_icon="🎨", layout="wide")

# ---------------------------------------------------------
# 2. Load Model (Cached)
# ---------------------------------------------------------
@st.cache_resource
def get_model():
    return new_session("u2net")

# ---------------------------------------------------------
# 3. Initialize Session State
# ---------------------------------------------------------
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

# ---------------------------------------------------------
# 4. Translations Dictionary
# ---------------------------------------------------------
translations = {
    'en': {
        'title': "Remove Image Background",
        'upload_label': "Upload Image (JPG, PNG, WEBP)",
        'sidebar_title': "🎨 Design Studio",
        'shadow_settings': "🌑 Realistic Shadow",
        'enable_shadow': "Add Contact Shadow",
        'blur': "Shadow Softness",
        'opacity': "Shadow Intensity",
        'x_offset': "Position X",
        'y_offset': "Position Y",
        'quality_settings': "✨ Quality Enhancer",
        'enable_quality': "Enhance Quality & Details",
        'button_process': "Remove Background (High-Res) ✨",
        'download': "📥 Download Design",
        'footer': "Developed by Mo Mahbuobeh © 2025",
        'dir': 'ltr', 'align': 'left'
    },
    'ar': {
        'title': "مؤمن | إزالة خلفية بدقة عالية",
        'upload_label': "ارفع الصورة هنا (JPG, PNG, WEBP)",
        'sidebar_title': "🎨 استوديو التصميم",
        'shadow_settings': "🌑 ظل واقعي",
        'enable_shadow': "إضافة ظل أرضي",
        'blur': "نعومة الظل",
        'opacity': "قوة الظل",
        'x_offset': "تحريك أفقي",
        'y_offset': "تحريك عمودي",
        'quality_settings': "✨ تحسين السحر",
        'enable_quality': "رفع الجودة والتفاصيل",
        'button_process': "معالجة بدقة عالية ✨",
        'download': "📥 تحميل التصميم",
        'footer': "تم التطوير بواسطة Mo Mahbuobeh © 2025",
        'dir': 'rtl', 'align': 'right'
    }
}

lang = st.session_state['language']
t = translations[lang]

# ---------------------------------------------------------
# 5. CSS Styling
# ---------------------------------------------------------
st.markdown(f"""
    <style>
    .main {{ direction: {t['dir']}; text-align: {t['align']}; }}
    .stApp {{ background-color: #0E0E0E; }}
    [data-testid="stSidebar"] {{ background-color: #181614; border-right: 1px solid #333; }}
    .stButton>button {{
        background-color: #C0A062; color: #000; font-weight: bold;
        border-radius: 8px; border: none; padding: 12px; width: 100%; transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #E3C07B; color: #000;
        box-shadow: 0 4px 15px rgba(192, 160, 98, 0.4);
    }}
    h1, h2, h3 {{ color: #E3C07B !important; font-family: 'Segoe UI', sans-serif; }}
    .footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #181614; color: #888; text-align: center;
        padding: 10px; font-size: 14px; border-top: 1px solid #333; z-index: 999;
    }}
    .stSpinner > div {{ border-top-color: #C0A062 !important; }}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. Image Processing Functions
# ---------------------------------------------------------
def add_shadow(image, offset_x, offset_y, blur_radius, shadow_opacity):
    image = image.convert("RGBA")
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_data = []
    datas = image.getdata()
    for item in datas:
        if item[3] > 0:
            shadow_data.append((0, 0, 0, int(shadow_opacity * 255)))
        else:
            shadow_data.append((0, 0, 0, 0))
    shadow.putdata(shadow_data)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    canvas_width = image.width + abs(offset_x) + 100
    canvas_height = image.height + abs(offset_y) + 100
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    
    center_x = (canvas_width - image.width) // 2
    center_y = (canvas_height - image.height) // 2
    
    canvas.paste(shadow, (center_x + offset_x, center_y + offset_y), shadow)
    canvas.paste(image, (center_x, center_y), image)
    
    return canvas.crop(canvas.getbbox())

# ---------------------------------------------------------
# 7. Main App Layout
# ---------------------------------------------------------

# --- SIDEBAR START ---
with st.sidebar:
    try:
        st.image("logo.png", use_column_width=True)
    except:
        st.warning("Upload logo.png")

    # Language Flags
    c1, c2 = st.columns(2)
    if c1.button("🇬🇧 EN"): 
        st.session_state['language'] = 'en'
        st.rerun()
    if c2.button("🇯🇴 AR"): 
        st.session_state['language'] = 'ar'
        st.rerun()

    st.markdown("---")
    st.header(t['sidebar_title'])
    
    # Shadow Settings
    with st.expander(t['shadow_settings'], expanded=True):
        apply_shadow = st.checkbox(t['enable_shadow'], value=True)
        if apply_shadow:
            s_y = st.slider(t['y_offset'], -50, 100, 20) 
            s_x = st.slider(t['x_offset'], -50, 50, 0)
            s_blur = st.slider(t['blur'], 0, 50, 15)
            s_opacity = st.slider(t['opacity'], 0.0, 1.0, 0.6)

    # Quality Settings
    with st.expander(t['quality_settings']):
        enhance_quality = st.checkbox(t['enable_quality'], value=True)
        if enhance_quality:
            sharpness = st.slider("Sharpness", 1.0, 3.0, 1.4)
            contrast = st.slider("Contrast", 1.0, 2.0, 1.1)
# --- SIDEBAR END ---

# --- MAIN PAGE START ---
st.title(t['title'])

uploaded_file = st.file_uploader(t['upload_label'], type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, use_column_width=True)

    if st.button(t['button_process']):
        status_text = "Processing..."
        if 'model_loaded' not in st.session_state:
             status_text = "Downloading AI Model (First time only)... ⏳"
        
        with st.spinner(status_text):
            try:
                # Load Model
                model_session = get_model()
                st.session_state['model_loaded'] = True
                
                # Process
                output = remove(image, session=model_session)
                
                if enhance_quality:
                    output = ImageEnhance.Sharpness(output).enhance(sharpness)
                    output = ImageEnhance.Contrast(output).enhance(contrast)

                if apply_shadow:
                    output = add_shadow(output, s_x, s_y, s_blur, s_opacity)

                with col2:
                    st.markdown('<div style="background:url(https://www.transparenttextures.com/patterns/checkerboard.png); padding:10px; border-radius:10px;">', unsafe_allow_html=True)
                    st.image(output, use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                buf = io.BytesIO()
                output.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=t['download'],
                    data=byte_im,
                    file_name=f"Mumen_Pro_Design.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Error: {e}")


st.markdown(f"<div class='footer'>{t['footer']}</div>", unsafe_allow_html=True)
