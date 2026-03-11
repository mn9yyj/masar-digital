import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# --- 1. واجهة المستخدم الثابتة ---
st.set_page_config(page_title="المسار 🖥️ الرقمي", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #050505; direction: rtl; }
    .brand { font-size: 42px; font-weight: 900; text-align: center; color: #706fd3; margin-bottom: 20px; }
    .centered-ui { max-width: 600px; margin: 0 auto; }
    .stButton>button { width: 100%; border-radius: 12px !important; background: linear-gradient(90deg, #4834d4, #686de0) !important; height: 55px; font-weight: bold; font-size: 18px; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي</div>', unsafe_allow_html=True)

# --- 2. مدخلات المستخدم ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    mode = st.radio("الوضع", ["تلقائي ✨", "يدوي ✍️"], horizontal=True)
    topic = st.text_input("🎯 موضوع العرض الرئيسي", placeholder="اكتب العنوان هنا...")
    slides_num = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    generate_btn = st.button("🚀 صنع العرض المطور")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. محرك التصميم المصلح (حل خطأ FillFormat) ---
def apply_style(slide, topic_name, title_text, body_text, lang_choice):
    # تحديد لون الثيم بناءً على الموضوع
    t = topic_name.lower()
    main_rgb = RGBColor(0, 120, 215) # أزرق افتراضي
    if any(w in t for w in ['طب', 'صحي', 'health']): main_rgb = RGBColor(0, 153, 76)
    elif any(w in t for w in ['تقني', 'ذكاء', 'ai']): main_rgb = RGBColor(112, 111, 211)

    # إضافة شريط العنوان العلوي (طريقة مصلحة وآمنة)
    from pptx.enum.shapes import MSO_SHAPE
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(1))
    rect.fill.solid() # تفعيل التعبئة الصلبة أولاً
    rect.fill.foreground_color.rgb = main_rgb
    rect.line.width = 0

    # تنسيق العنوان
    title_shape = slide.shapes.title
    title_shape.text = str(title_text)
    tf = title_shape.text_frame.paragraphs[0]
    tf.font.size = Pt(24)
    tf.font.bold = True
    tf.font.color.rgb = RGBColor(255, 255, 255)

    # تنسيق المحتوى الكثيف
    body_shape = slide.placeholders[1]
    body_shape.text = str(body_text)
    for p in body_shape.text_frame.paragraphs:
        p.font.size = Pt(12)
        p.alignment = PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT

# --- 4. منطق التشغيل ---
if generate_btn and topic:
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("❌ خطأ: لم يتم ضبط مفتاح الـ API في Secrets")
    else:
        with st.spinner('جاري التحليل والتصميم الذكي...'):
            prompt = f"Create {slides_num} highly detailed slides for '{topic}'. Professional and academic style. Use paragraphs, not just bullets. Return ONLY JSON array."
            try:
                res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {api_key}"},
                                    json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                
                res_json = res.json()
                if 'choices' in res_json:
                    content = res_json['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
                    data = json.loads(content)
                    
                    prs = Presentation()
                    for item in data:
                        slide = prs.slides.add_slide(prs.slide_layouts[1])
                        apply_style(slide, topic, item['title'], item['body'], lang)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['pptx'] = buf.getvalue()
                    st.session_state['name'] = topic
                else:
                    st.error("فشل في جلب البيانات من الذكاء الاصطناعي")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")

if 'pptx' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.download_button("📥 تحميل البوربوينت المصمم والجاهز", data=st.session_state['pptx'], file_name=f"{st.session_state['name']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
