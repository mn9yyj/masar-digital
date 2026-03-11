import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. تصميم الواجهة (احترافي ثابت) ---
st.set_page_config(page_title="المسار 🖥️ الرقمي - الإصدار الذهبي", layout="wide")
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

# --- 2. محرك التصميم الهندسي والمعلوماتي ---
def apply_gold_theme(slide, topic, item, lang_choice):
    # اختيار لون الثيم (ذكي)
    t = topic.lower()
    main_rgb = RGBColor(112, 111, 211) # بنفسجي افتراضي
    if any(w in t for w in ['رمضان', 'صيام', 'ديني']): main_rgb = RGBColor(39, 174, 96) # أخضر
    elif any(w in t for w in ['تقني', 'ذكاء', 'tech']): main_rgb = RGBColor(41, 128, 185) # أزرق
    elif any(w in t for w in ['صحه', 'طب', 'health']): main_rgb = RGBColor(192, 57, 43) # أحمر طبي

    # أ) إضافة هيدر هندسي (Title Bar)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(1))
    shape.fill.solid()
    shape.fill.fore_color.rgb = main_rgb
    shape.line.width = 0

    # ب) تنسيق العنوان
    title_box = slide.shapes.add_textbox(0, 0, Inches(10), Inches(1))
    p_title = title_box.text_frame.paragraphs[0]
    p_title.text = str(item.get('title', 'العنوان'))
    p_title.font.size, p_title.font.bold = Pt(24), True
    p_title.font.color.rgb = RGBColor(255, 255, 255)
    p_title.alignment = PP_ALIGN.CENTER

    # ج) تنسيق المحتوى (تكثيف المعلومات + ترتيب المزدوج)
    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9), Inches(5.5))
    tf = content_box.text_frame
    tf.word_wrap = True

    # ترتيب النصوص: العربي فوق ثم الإنجليزي تحت
    if lang_choice == "مزدوج":
        # إضافة الفقرة العربية
        p_ar = tf.paragraphs[0]
        p_ar.text = f"● {item.get('body_ar', 'لا يوجد نص عربي')}"
        p_ar.font.size, p_ar.alignment = Pt(13), PP_ALIGN.RIGHT
        p_ar.font.name = "Arial"
        
        # إضافة الفقرة الإنجليزية بالأسفل
        p_en = tf.add_paragraph()
        p_en.text = f"\n● {item.get('body_en', 'No English text available')}"
        p_en.font.size, p_en.alignment = Pt(12), PP_ALIGN.LEFT
    else:
        p = tf.paragraphs[0]
        p.text = str(item.get('body', ''))
        p.font.size = Pt(13)
        p.alignment = PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT

# --- 3. واجهة التحكم ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض", placeholder="اكتب الموضوع هنا...")
    slides = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    
    if st.button("🚀 صنع العرض المطور"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key: st.error("تأكد من إعداد Secrets!")
        else:
            with st.spinner('🎨 جاري تنسيق المعلومات وتطبيق الثيمات...'):
                try:
                    # صياغة الأمر لجلب معلومات مكثفة ودقيقة
                    lang_instr = "Return JSON with 'body_ar' and 'body_en' fields." if lang == "مزدوج" else "Return JSON with 'body' field."
                    prompt = f"Create {slides} deep academic slides about '{topic}'. {lang_instr} Use paragraphs, provide facts. Return ONLY clean JSON array."
                    
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    raw = res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw)
                    
                    prs = Presentation()
                    for item in data:
                        slide = prs.slides.add_slide(prs.slide_layouts[6])
                        apply_gold_theme(slide, topic, item, lang)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['f'] = buf.getvalue()
                    st.session_state['t'] = topic
                except Exception as e: st.error(f"تأكد من رصيد الـ API: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'f' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.success("✅ تم بناء العرض الاحترافي بنجاح")
    st.download_button("📥 تحميل ملف البوربوينت", data=st.session_state['f'], file_name=f"{st.session_state['t']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
