import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. واجهة المستخدم الثابتة والجميلة ---
st.set_page_config(page_title="المسار 🖥️ الرقمي", layout="wide")
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

# --- 2. مدخلات المستخدم المحسنة ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض الرئيسي", placeholder="اكتب العنوان هنا...")
    
    col1, col2 = st.columns(2)
    with col1:
        slides_num = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    with col2:
        lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج (Ar/En)"])

    generate_btn = st.button("🚀 صنع العرض المطور بالثيمات")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. وظيفة التصميم الذكي (حل مشكلة التداخل واللغات) ---
def create_smart_pptx(data, topic_name, lang_choice):
    prs = Presentation()
    
    # اختيار لون الثيم بناءً على الموضوع
    main_color = RGBColor(112, 111, 211) # بنفسجي افتراضي
    if any(w in topic_name.lower() for w in ['جامعة', 'تعليم', 'university']): main_color = RGBColor(0, 51, 102)
    elif any(w in topic_name.lower() for w in ['رمضان', 'ديني', 'islam']): main_color = RGBColor(46, 125, 50)

    for item in data:
        # استخدام تخطيط فارغ للتحكم الكامل ومنع تداخل النصوص
        slide = prs.slides.add_slide(prs.slide_layouts[6]) 
        
        # أ) إضافة شريط العنوان الملون في الأعلى
        rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.1))
        rect.fill.solid()
        rect.fill.fore_color.rgb = main_color
        rect.line.width = 0

        # ب) إضافة نص العنوان
        title_box = slide.shapes.add_textbox(0, 0, prs.slide_width, Inches(1.1))
        p_title = title_box.text_frame.paragraphs[0]
        p_title.text = str(item.get('title', ''))
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = RGBColor(255, 255, 255)
        p_title.alignment = PP_ALIGN.CENTER

        # ج) إضافة نص المحتوى (Body) مع تنسيق اللغة
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), prs.slide_width - Inches(1), prs.slide_height - Inches(1.5))
        tf = content_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = str(item.get('body', ''))
        p.font.size = Pt(13)
        
        # تحديد المحاذاة بناءً على اللغة لمنع التداخل
        if "العربية" in lang_choice:
            p.alignment = PP_ALIGN.RIGHT
        elif "English" in lang_choice:
            p.alignment = PP_ALIGN.LEFT
        else: # المزدوجة: محاذاة مضبوطة
            p.alignment = PP_ALIGN.JUSTIFY

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()

# --- 4. معالجة الطلب ---
if generate_btn and topic:
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("❌ خطأ: يرجى إضافة OPENROUTER_API_KEY في Secrets")
    else:
        with st.spinner('🎨 جاري التنسيق ومنع تداخل اللغات...'):
            try:
                # طلب محتوى مكثف ودقيق
                prompt = f"Create {slides_num} slides for '{topic}'. Provide very deep academic info. Language: {lang}. Return ONLY JSON: [{{'title': '...', 'body': '...'}}]"
                res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {api_key}"},
                                    json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                
                content = res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
                pptx_data = create_smart_pptx(json.loads(content), topic, lang)
                
                st.session_state['file'] = pptx_data
                st.session_state['name'] = topic
            except Exception as e:
                st.error(f"حدث خطأ في المعالجة: {e}")

if 'file' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.success("✅ تم حل مشاكل التداخل وتجهيز الثيم!")
    st.download_button("📥 تحميل البوربوينت المطور", data=st.session_state['file'], file_name=f"{st.session_state['name']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
