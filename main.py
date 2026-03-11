import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- إعدادات الواجهة الثابتة ---
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

# --- مدخلات المستخدم ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض الرئيسي", placeholder="اكتب العنوان هنا...")
    slides_num = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    generate_btn = st.button("🚀 صنع العرض المطور")
    st.markdown('</div>', unsafe_allow_html=True)

# --- محرك الألوان الذكي ---
def get_theme(topic_text):
    t = topic_text.lower()
    if any(w in t for w in ['جامعة', 'تعليم', 'دراسة']): return RGBColor(0, 51, 102) # كحلي أكاديمي
    if any(w in t for w in ['تقني', 'ذكاء', 'tech']): return RGBColor(112, 111, 211) # بنفسجي تقني
    return RGBColor(44, 62, 80) # رمادي رسمي

# --- إنشاء البوربوينت المنسق ---
if generate_btn and topic:
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("❌ تأكد من إضافة المفتاح في Secrets")
    else:
        with st.spinner('🎨 جاري التصميم ومنع تداخل النصوص...'):
            try:
                prompt = f"Create {slides_num} slides for '{topic}'. Deep details. Return ONLY clean JSON array: [{{'title': '...', 'body': '...'}}]"
                res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {api_key}"},
                                    json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                
                res_data = res.json()
                if 'choices' in res_data:
                    data = json.loads(res_data['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
                    
                    prs = Presentation()
                    theme_color = get_theme(topic)
                    
                    for item in data:
                        # استخدام تخطيط فارغ للتحكم الكامل في المكان ومنع التداخل
                        slide = prs.slides.add_slide(prs.slide_layouts[6]) 
                        
                        # 1. إضافة إطار العنوان العلوي (ثيم ملون)
                        rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
                        rect.fill.solid()
                        rect.fill.foreground_color.rgb = theme_color
                        rect.line.width = 0

                        # 2. إضافة نص العنوان داخل الإطار
                        title_box = slide.shapes.add_textbox(0, 0, prs.slide_width, Inches(1.2))
                        tf = title_box.text_frame
                        p = tf.paragraphs[0]
                        p.text = item['title']
                        p.font.size = Pt(28)
                        p.font.bold = True
                        p.font.color.rgb = RGBColor(255, 255, 255)
                        p.alignment = PP_ALIGN.CENTER

                        # 3. إضافة محتوى النص (body) بعيداً عن العنوان لمنع التداخل
                        body_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), prs.slide_width - Inches(1), prs.slide_height - Inches(2))
                        bf = body_box.text_frame
                        bf.word_wrap = True
                        p2 = bf.paragraphs[0]
                        p2.text = item['body']
                        p2.font.size = Pt(13)
                        p2.alignment = PP_ALIGN.RIGHT if lang != "English" else PP_ALIGN.LEFT
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['file'] = buf.getvalue()
                    st.session_state['name'] = topic
                else: st.error("خطأ 'choices': تأكد من شحن رصيد الـ API")
            except Exception as e: st.error(f"حدث خطأ: {e}")

if 'file' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.download_button("📥 تحميل العرض المنسق (بدون تداخل)", data=st.session_state['file'], file_name=f"{st.session_state['name']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
