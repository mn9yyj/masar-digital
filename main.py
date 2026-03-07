import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN

# --- 1. التصميم البصري ---
st.set_page_config(page_title="المسار 🖥️ الرقمي", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #050505; direction: rtl; }
    .brand { font-size: 42px; font-weight: 900; text-align: center; color: #706fd3; margin-bottom: 20px; }
    .centered-ui { max-width: 600px; margin: 0 auto; }

    /* تنسيق المربعات البارزة للايقونات */
    div[data-baseweb="segmented-control"] { 
        background: rgba(255, 255, 255, 0.05) !important; 
        border-radius: 10px; padding: 5px;
        border: 1px solid rgba(112, 111, 211, 0.2);
    }

    .stButton>button { 
        width: 100%; border-radius: 12px !important; 
        background: linear-gradient(90deg, #4834d4, #686de0) !important; 
        height: 55px; font-weight: bold; font-size: 18px; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي</div>', unsafe_allow_html=True)

# --- 2. واجهة المستخدم (تلقائي/يدوي) ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)

    mode = st.segmented_control("الوضع الحالي", options=["تلقائي ✨", "يدوي ✍️"], default="تلقائي ✨")

    st.markdown("<br>", unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض الرئيسي", placeholder="اكتب عنوان الموضوع هنا...")

    col1, col2 = st.columns(2)
    with col1:
        st.write("🔢 عدد الشرائح")
        slides_num = st.segmented_control("S_Num", options=[3, 5, 10, 15, 20, 30], default=5, label_visibility="collapsed")
    with col2:
        st.write("📝 عمق المحتوى")
        depth = st.segmented_control("D_Val", options=["مختصر", "تفصيلي"], default="مختصر", label_visibility="collapsed")

    # منطق الخانات اليدوية
    manual_titles = []
    if mode == "يدوي ✍️":
        st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        for i in range(slides_num):
            t_input = st.text_input(f"عنوان الشريحة {i+1}", key=f"manual_t_{i}")
            manual_titles.append(t_input)

    c1, c2 = st.columns(2)
    with c1:
        lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج (Ar/En)"])
    with c2:
        style = st.selectbox("🎨 الأسلوب", ["احترافي", "عادي", "تعليمي"])

    generate_btn = st.button("🚀 صنع العرض الآن")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. وظيفة إنشاء ملف البوربوينت (المصلحة) ---
def build_pptx(data, language):
    prs = Presentation()
    for item in data:
        slide = prs.slides.add_slide(prs.slide_layouts[1])

        # استخراج النصوص ومعالجة خطأ القواميس (AttributeError fix)
        # نضمن هنا أن يكون الناتج دوماً نص (String) وليس قاموساً
        t_raw = item.get('title', '')
        b_raw = item.get('body', '')

        t_text = str(t_raw) if not isinstance(t_raw, dict) else " / ".join(filter(None, t_raw.values()))
        b_text = str(b_raw) if not isinstance(b_raw, dict) else "\n".join(filter(None, b_raw.values()))

        # إعداد العنوان (حجم 24)
        title_shape = slide.shapes.title
        title_shape.text = t_text
        title_shape.text_frame.paragraphs[0].font.size = Pt(24)

        # إعداد المحتوى (حجم 14 لضمان المساحة)
        body_shape = slide.placeholders[1]
        body_shape.text = b_text
        for p in body_shape.text_frame.paragraphs:
            p.font.size = Pt(14)
            # ضبط الاتجاه حسب اللغة
            p.alignment = PP_ALIGN.RIGHT if "العربية" in language or "مزدوج" in language else PP_ALIGN.LEFT

    output_stream = io.BytesIO()
    prs.save(output_stream)
    return output_stream.getvalue()

# --- 4. منطق التشغيل والتحميل ---
if generate_btn and topic:
    with st.spinner('جاري توليد المحتوى وتنسيق البوربوينت...'):
        api_key = os.environ.get('OPENROUTER_API_KEY')

        # بناء الطلب حسب الوضع (تلقائي أو يدوي)
        if mode == "يدوي ✍️" and any(manual_titles):
            titles_list = ", ".join([t for t in manual_titles if t])
            prompt = f"Create {slides_num} slides for '{topic}' using these specific titles: {titles_list}. Write in {lang}. Return ONLY JSON array of {{'title': '...', 'body': '...'}}."
        else:
            prompt = f"Create {slides_num} professional slides about '{topic}'. Language: {lang}. Style: {style}. Depth: {depth}. Return ONLY JSON array of {{'title': '...', 'body': '...'}}."

        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                headers={"Authorization": f"Bearer {api_key}"},
                                json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})

            content = res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
            data_json = json.loads(content)

            # تخزين الملف في الجلسة لضمان عمل زر التحميل
            st.session_state['file_ready'] = build_pptx(data_json, lang)
            st.session_state['current_topic'] = topic
        except Exception as e:
            st.error(f"خطأ في المعالجة: {str(e)}")

if 'file_ready' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.success(f"✅ تم إنشاء عرض: {st.session_state['current_topic']}")
    st.download_button(
        label="📥 تحميل ملف البوربوينت النهائي",
        data=st.session_state['file_ready'],
        file_name=f"{st.session_state['current_topic']}.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    st.markdown('</div>', unsafe_allow_html=True)
