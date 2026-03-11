import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. واجهة المستخدم (التصميم الثابت) ---
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

st.markdown('<div class="brand">المسار 🖥️ الرقمي - Pro</div>', unsafe_allow_html=True)

# --- 2. محرك التصميم العالمي ---
def apply_pro_theme(slide, topic, title_text, body_text, lang_choice):
    # تحديد الهوية اللونية
    topic_l = topic.lower()
    main_color = RGBColor(112, 111, 211) # بنفسجي افتراضي
    if any(w in topic_l for w in ['رمضان', 'ديني', 'islam']): main_color = RGBColor(39, 174, 96) # أخضر زمردي
    elif any(w in topic_l for w in ['تقني', 'ذكاء', 'ai', 'tech']): main_color = RGBColor(41, 128, 185) # أزرق تقني
    elif any(w in topic_l for w in ['جامعة', 'دراسة', 'uni']): main_color = RGBColor(44, 62, 80) # كحلي أكاديمي

    # أ) إضافة هيدر (Header) احترافي ومستطيل هندسي
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(1.1))
    rect.fill.solid()
    rect.fill.fore_color.rgb = main_color
    rect.line.width = 0

    # ب) إضافة خط جمالي جانبي كشكل هندسي (Accent)
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.1), Inches(0.1), Inches(6.4))
    accent.fill.solid()
    accent.fill.fore_color.rgb = main_color
    accent.line.width = 0

    # ج) تنسيق العنوان داخل الهيدر ومنع التداخل
    title_box = slide.shapes.add_textbox(Inches(0.5), 0, Inches(9), Inches(1.1))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = str(title_text)
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER if lang_choice == "مزدوج" else (PP_ALIGN.RIGHT if lang_choice == "العربية" else PP_ALIGN.LEFT)

    # د) تنسيق المحتوى (Body) بمعايير عالمية ومنع تداخل اللغات
    content_box = slide.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(8.8), Inches(5))
    content_frame = content_box.text_frame
    content_frame.word_wrap = True
    p_body = content_frame.paragraphs[0]
    p_body.text = str(body_text)
    p_body.font.size = Pt(13)
    p_body.font.name = "Arial"
    
    # ضبط الاتجاه والمحاذاة تلقائياً
    if "العربية" in lang_choice:
        p_body.alignment = PP_ALIGN.RIGHT
    elif "English" in lang_choice:
        p_body.alignment = PP_ALIGN.LEFT
    else:
        p_body.alignment = PP_ALIGN.JUSTIFY

# --- 3. الواجهة والتشغيل ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض", placeholder="مثلاً: مستقبل الذكاء الاصطناعي")
    slides = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    
    if st.button("🚀 إصدار العرض الاحترافي"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key:
            st.error("يرجى ضبط Secrets: OPENROUTER_API_KEY")
        else:
            with st.spinner('🎨 جاري تطبيق الثيمات العالمية والأشكال الهندسية...'):
                try:
                    prompt = f"Create {slides} professional slides about '{topic}'. Deep academic details. Language: {lang}. Return ONLY JSON array: [{{'title': '...', 'body': '...'}}]"
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    data = json.loads(res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
                    prs = Presentation()
                    for item in data:
                        slide = prs.slides.add_slide(prs.slide_layouts[6])
                        apply_pro_theme(slide, topic, item['title'], item['body'], lang)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['pro_file'] = buf.getvalue()
                    st.session_state['pro_topic'] = topic
                except Exception as e:
                    st.error(f"خطأ: تأكد من المفتاح والرصيد. {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'pro_file' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.success("✅ جاهز للتحميل بمستوى عالمي وثيم مخصص!")
    st.download_button("📥 تحميل الملف المطور", data=st.session_state['pro_file'], file_name=f"{st.session_state['pro_topic']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
