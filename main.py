import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- تصميم الواجهة ---
st.set_page_config(page_title="المسار 🖥️ الرقمي", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #050505; direction: rtl; }
    .brand { font-size: 42px; font-weight: 900; text-align: center; color: #706fd3; margin-bottom: 20px; }
    .centered-ui { max-width: 600px; margin: 0 auto; }
    .stButton>button { width: 100%; border-radius: 12px !important; background: linear-gradient(90deg, #4834d4, #686de0) !important; height: 55px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي</div>', unsafe_allow_html=True)

# --- محرك إنشاء المحتوى والتصميم ---
def create_presentation(data, topic, lang):
    prs = Presentation()
    # تحديد لون الثيم بناء على الموضوع
    theme_rgb = RGBColor(112, 111, 211) # بنفسجي افتراضي
    if any(w in topic.lower() for w in ['جامعة', 'تعليم', 'دراسة']): theme_rgb = RGBColor(0, 51, 102)

    for item in data:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) # تخطيط فارغ تماماً
        
        # إضافة مستطيل العنوان العلوي (حل مشكلة التداخل والألوان)
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
        shape.fill.solid()
        shape.fill.fore_color.rgb = theme_rgb # الطريقة الصحيحة لتلوين الشكل
        shape.line.width = 0

        # إضافة نص العنوان
        title_box = slide.shapes.add_textbox(0, 0, prs.slide_width, Inches(1))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = str(item.get('title', 'العنوان'))
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # إضافة نص المحتوى (Body) مع إزاحة لمنع التداخل
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), prs.slide_width - Inches(1), prs.slide_height - Inches(2))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        p_content = content_frame.paragraphs[0]
        p_content.text = str(item.get('body', 'لا يوجد محتوى'))
        p_content.font.size = Pt(13)
        p_content.alignment = PP_ALIGN.RIGHT if lang != "English" else PP_ALIGN.LEFT

    return prs

# --- واجهة المدخلات ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض", placeholder="اكتب العنوان هنا...")
    slides = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    if st.button("🚀 صنع العرض المطور"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key:
            st.error("يرجى ضبط Secrets: OPENROUTER_API_KEY")
        else:
            with st.spinner('جاري التحليل والتصميم الذكي...'):
                prompt = f"Create {slides} professional slides for '{topic}'. Provide VERY DEEP academic info. Return ONLY JSON array: [{{'title': '...', 'body': '...'}}]"
                res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {api_key}"},
                                    json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                
                try:
                    res_json = res.json()
                    content = res_json['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
                    data = json.loads(content)
                    prs = create_presentation(data, topic, lang)
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['file'] = buf.getvalue()
                    st.session_state['topic'] = topic
                except Exception as e:
                    st.error(f"حدث خطأ: تأكد من الرصيد والبيانات. {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'file' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.download_button("📥 تحميل الملف المصمم", data=st.session_state['file'], file_name=f"{st.session_state['topic']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
