import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# --- تصميم الواجهة الاحترافية (الثابتة) ---
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

# --- محرك التصميم المعتمد على القوالب المصورة (لتحقيق نتيجة الأمثلة) ---
def apply_template_design(slide, item, lang_choice, topic):
    # تحديد مسار صورة الخلفية بناءً على الموضوع (يجب رفع الصور لـ GitHub)
    t_lower = topic.lower()
    bg_image_path = "default_bg.png" # مسار افتراضي
    
    if any(w in t_lower for w in ['تقني', 'ذكاء', 'ai']):
        bg_image_path = "tech_template.png" # مثال لتصميم مثل image_10.png
    elif any(w in t_lower for w in ['جامعة', 'دراسة']):
        bg_image_path = "academic_template.png" # مثال لتصميم مثل image_8.png

    # 1. دمج صورة الخلفية المصممة جاهزة (Image-Based Template)
    if os.path.exists(bg_image_path):
        slide.shapes.add_picture(bg_image_path, 0, 0, width=Inches(10), height=Inches(7.5))

    # 2. إضافة وتنسيق العنوان في مكانه المخصص داخل التصميم
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
    tf_title = title_box.text_frame
    p_title = tf_title.paragraphs[0]
    p_title.text = str(item.get('title', 'العنوان'))
    p_title.font.size, p_title.font.bold = Pt(28), True
    p_title.font.color.rgb = RGBColor(0, 0, 0) # أسود افتراضي فوق التصميم الملون
    p_title.alignment = PP_ALIGN.CENTER if lang_choice == "مزدوج" else (PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT)

    # 3. إضافة وتنسيق المحتوى الكثيف مع منع التداخل
    content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(5.2))
    tf_content = content_box.text_frame
    tf_content.word_wrap = True
    
    # تنسيق المزدوج: العربي فوق الإنجليزي
    if lang_choice == "مزدوج":
        p_ar = tf_content.paragraphs[0]
        p_ar.text = f"● {item.get('body_ar', 'النص العربي المطور...')}"
        p_ar.font.size, p_ar.alignment = Pt(14), PP_ALIGN.RIGHT
        p_ar.font.name = "Arial"
        
        p_en = tf_content.add_paragraph()
        p_en.text = f"\n● {item.get('body_en', 'Detailed English content...')}"
        p_en.font.size, p_en.alignment = Pt(12), PP_ALIGN.LEFT
    else:
        p = tf_content.paragraphs[0]
        p.text = str(item.get('body', ''))
        p.font.size = Pt(14)
        p.alignment = PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT

# --- واجهة المدخلات والتشغيل ---
with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض (سيحدد التصميم المرئي)", placeholder="اكتب الموضوع الرئيسي هنا...")
    slides = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    
    if st.button("🚀 صنع العرض الاحترافي المصور"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key:
            st.error("يرجى ضبط Secrets: OPENROUTER_API_KEY")
        else:
            with st.spinner('🎨 جاري دمج التصاميم المرئية وتنسيق اللغات...'):
                try:
                    # طلب معلومات مكثفة ودقيقة
                    lang_instr = "Include 'title', 'body_ar', and 'body_en'." if lang == "مزدوج" else "Include 'title' and 'body'."
                    prompt = f"Create {slides} deep academic slides about '{topic}'. {lang_instr} Return ONLY JSON array."
                    
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    res_json = res.json()
                    if 'choices' in res_json:
                        raw = res_json['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
                        data = json.loads(raw)
                        
                        prs = Presentation()
                        # استخدام تخطيط فارغ تماماً لتطبيق التصميم المصور
                        blank_layout = prs.slide_layouts[6] 
                        
                        for slide_data in data:
                            slide = prs.slides.add_slide(blank_layout)
                            apply_template_design(slide, slide_data, lang, topic)
                        
                        buf = io.BytesIO()
                        prs.save(buf)
                        st.session_state['f'] = buf.getvalue()
                        st.session_state['t'] = topic
                    else: st.error("خطأ 'choices': تأكد من رصيد الـ API")
                except Exception as e: st.error(f"خطأ تقني: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'f' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.success("✅ تم بناء العرض الاحترافي بنجاح!")
    st.download_button("📥 تحميل البوربوينت المصمم", data=st.session_state['f'], file_name=f"{st.session_state['t']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
