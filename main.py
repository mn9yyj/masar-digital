import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. تصميم واجهة الموقع ---
st.set_page_config(page_title="المسار 🖥️ الرقمي - المطور", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #050505; direction: rtl; }
    .brand { font-size: 42px; font-weight: 900; text-align: center; color: #706fd3; margin-bottom: 20px; }
    .centered-ui { max-width: 600px; margin: 0 auto; }
    .stButton>button { width: 100%; border-radius: 12px !important; background: linear-gradient(90deg, #4834d4, #686de0) !important; height: 55px; font-weight: bold; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي</div>', unsafe_allow_html=True)

# --- 2. محرك التصميم والترتيب الذكي ---
def apply_ultra_theme(slide, topic, item, lang_choice):
    # تحديد اللون بناءً على الموضوع
    t = topic.lower()
    main_rgb = RGBColor(112, 111, 211) # افتراضي
    if any(w in t for w in ['رمضان', 'ديني', 'سلام']): main_rgb = RGBColor(39, 174, 96)
    elif any(w in t for w in ['تقني', 'ذكاء', 'ai']): main_rgb = RGBColor(41, 128, 185)
    elif any(w in t for w in ['جامعة', 'دراسة']): main_rgb = RGBColor(44, 62, 80)

    # أ) إضافة أشكال هندسية (إطار العنوان)
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(1))
    rect.fill.solid()
    rect.fill.fore_color.rgb = main_rgb
    rect.line.width = 0

    # ب) ترتيب العنوان
    title_box = slide.shapes.add_textbox(0, 0, Inches(10), Inches(1))
    p_title = title_box.text_frame.paragraphs[0]
    p_title.text = str(item.get('title', ''))
    p_title.font.size, p_title.font.bold = Pt(26), True
    p_title.font.color.rgb = RGBColor(255, 255, 255)
    p_title.alignment = PP_ALIGN.CENTER

    # ج) ترتيب النصوص (العربي فوق الإنجليزي في المزدوج)
    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9), Inches(5.5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    # معالجة النص المزدوج
    full_text = ""
    if lang_choice == "مزدوج":
        full_text = f"{item.get('body_ar', '')}\n\n{item.get('body_en', '')}"
    else:
        full_text = item.get('body', '')

    p = tf.paragraphs[0]
    p.text = full_text
    p.font.size = Pt(13)
    p.font.name = "Arial"
    p.alignment = PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT

# --- 3. تشغيل النظام ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض", placeholder="مثلاً: تأثير الصيام على الصحة")
    slides = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    
    if st.button("🚀 صنع العرض المطور"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key: st.error("ضبط مفتاح API أولاً!")
        else:
            with st.spinner('🎨 جاري التنسيق وتكثيف المعلومات...'):
                try:
                    # طلب محتوى مكثف ومرتب
                    fmt = "[{'title': '...', 'body_ar': 'نص عربي كثيف', 'body_en': 'Detailed English text'}]" if lang == "مزدوج" else "[{'title': '...', 'body': '...'}]"
                    prompt = f"Create {slides} academic slides about '{topic}'. Deep details. Format: {fmt}"
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    data = json.loads(res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
                    prs = Presentation()
                    for item in data:
                        slide = prs.slides.add_slide(prs.slide_layouts[6])
                        apply_ultra_theme(slide, topic, item, lang)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['file'] = buf.getvalue()
                    st.session_state['topic'] = topic
                except Exception as e: st.error(f"حدث خطأ: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'file' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.download_button("📥 تحميل الملف العالمي", data=st.session_state['file'], file_name=f"{st.session_state['topic']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
