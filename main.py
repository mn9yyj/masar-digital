import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. واجهة المستخدم (الثابتة كما طلبت) ---
st.set_page_config(page_title="المسار 🖥️ الرقمي", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #050505; direction: rtl; }
    .brand { font-size: 42px; font-weight: 900; text-align: center; color: #706fd3; margin-bottom: 20px; }
    .centered-ui { max-width: 600px; margin: 0 auto; }
    div[data-baseweb="segmented-control"] { background: rgba(255, 255, 255, 0.05) !important; border-radius: 10px; padding: 5px; border: 1px solid rgba(112, 111, 211, 0.2); }
    .stButton>button { width: 100%; border-radius: 12px !important; background: linear-gradient(90deg, #4834d4, #686de0) !important; height: 55px; font-weight: bold; font-size: 18px; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي</div>', unsafe_allow_html=True)

# --- 2. التحكم في الإعدادات والقوائم ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    mode = st.segmented_control("الوضع الحالي", options=["تلقائي ✨", "يدوي ✍️"], default="تلقائي ✨")
    st.markdown("<br>", unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض الرئيسي", placeholder="اكتب العنوان هنا...")

    col1, col2 = st.columns(2)
    with col1:
        slides_num = st.segmented_control("S_Num", options=[3, 5, 10, 15], default=5)
    with col2:
        lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])

    manual_titles = []
    if mode == "يدوي ✍️":
        for i in range(slides_num):
            manual_titles.append(st.text_input(f"عنوان الشريحة {i+1}", key=f"m_{i}"))

    generate_btn = st.button("🚀 صنع العرض المطور")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. محرك الألوان الذكي حسب الموضوع ---
def get_dynamic_theme(topic_text):
    t = topic_text.lower()
    if any(w in t for w in ['تقني', 'ذكاء', 'tech', 'ai', 'computer']):
        return RGBColor(0, 120, 215), RGBColor(240, 240, 240) # أزرق تقني
    elif any(w in t for w in ['طب', 'صحي', 'health', 'medical']):
        return RGBColor(0, 153, 76), RGBColor(255, 255, 255) # أخضر طبي
    else:
        return RGBColor(112, 111, 211), RGBColor(255, 255, 255) # بنفسجي افتراضي

# --- 4. معالجة البيانات والبوربوينت ---
def create_styled_pptx(data, topic_name, language):
    prs = Presentation()
    main_color, bg_color = get_dynamic_theme(topic_name)
    
    for item in data:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        
        # --- إضافة خلفية/أشكال جمالية ---
        # مستطيل ملون في الأعلى كخلفية للعنوان
        rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
        rect.fill.solid()
        rect.fill.foreground_color.rgb = main_color
        rect.line.fill.background()

        # ضبط العنوان فوق المستطيل
        title_shape = slide.shapes.title
        title_shape.text = str(item.get('title', ''))
        title_text_frame = title_shape.text_frame.paragraphs[0]
        title_text_frame.font.size = Pt(28)
        title_text_frame.font.bold = True
        title_text_frame.font.color.rgb = RGBColor(255, 255, 255) # أبيض دائماً فوق اللون

        # ضبط المحتوى (معلومات دقيقة وكثيفة)
        body_shape = slide.placeholders[1]
        body_shape.text = str(item.get('body', ''))
        for p in body_shape.text_frame.paragraphs:
            p.font.size = Pt(13)
            p.font.name = "Arial"
            p.alignment = PP_ALIGN.RIGHT if language != "English" else PP_ALIGN.LEFT
            
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()

# --- 5. منطق التشغيل ---
if generate_btn and topic:
    with st.spinner('جاري التحليل والتصميم الذكي...'):
        api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
        # طلب محتوى مكثف جداً كما طلبت سابقاً
        prompt = f"Create {slides_num} slides for '{topic}'. Deep details, academic level. Return JSON array."
        
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                headers={"Authorization": f"Bearer {api_key}"},
                                json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
            
            raw_content = res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
            st.session_state['final_pptx'] = create_styled_pptx(json.loads(raw_content), topic, lang)
            st.session_state['file_name'] = topic
        except Exception as e:
            st.error(f"تأكد من إعداد Secrets: {e}")

if 'final_pptx' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.success(f"✅ تم تصميم العرض لـ: {st.session_state['file_name']}")
    st.download_button("📥 تحميل البوربوينت المصمم", 
                       data=st.session_state['final_pptx'], 
                       file_name=f"{st.session_state['file_name']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
