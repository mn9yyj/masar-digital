import streamlit as st
import requests, json, os, io, random
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. واجهة المستخدم بنمط Dark Mode الاحترافي ---
st.set_page_config(page_title="المسار 🖥️ الرقمي - نسخة الإنفوجرافيك", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #0e0e0e; direction: rtl; }
    .brand { font-size: 35px; font-weight: 900; text-align: center; color: #00d2ff; margin: 20px 0; }
    .stButton>button { width: 100%; border-radius: 20px !important; background: linear-gradient(90deg, #00d2ff, #3a7bd5) !important; height: 50px; font-weight: bold; border: none !important; }
    .stInput>div>div>input { background-color: #1a1a1a !important; color: white !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي - Premium Layouts</div>', unsafe_allow_html=True)

# --- 2. محرك التصميم وتوزيع النصوص ---
def apply_pro_layout(slide, item, index, lang_choice):
    # مصفوفة ألوان متناغمة
    palette = [RGBColor(0, 210, 255), RGBColor(255, 107, 107), RGBColor(29, 209, 161), RGBColor(254, 202, 87)]
    color = palette[index % len(palette)]
    
    # تحديد نمط الشريحة (يتغير كل مرة)
    style = index % 3

    # أ) إضافة لمسات هندسية خلفية (تجنب خطأ TRIANGLE)
    if style == 0:
        shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.5), Inches(-0.5), Inches(3), Inches(3))
    elif style == 1:
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(0.7))
    else:
        shape = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(8.8), Inches(0.2), Inches(1), Inches(1))
    
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.width = 0

    # ب) معالجة العنوان (تنظيف النصوص من JSON)
    title_text = item.get('title', 'العنوان')
    if isinstance(title_text, dict): title_text = title_text.get('ar', title_text.get('en', ''))
    
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.2), Inches(8), Inches(1))
    p_title = title_box.text_frame.paragraphs[0]
    p_title.text = str(title_text)
    p_title.font.size, p_title.font.bold = Pt(26), True
    p_title.alignment = PP_ALIGN.CENTER

    # ج) توزيع النقاط مع الترقيم الاحترافي
    points = item.get('points', [])
    for i, pt_data in enumerate(points[:4]):
        top_pos = Inches(1.6 + (i * 1.3))
        
        # رسم دائرة الرقم
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), top_pos + Inches(0.1), Inches(0.4), Inches(0.4))
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        
        # إضافة الرقم
        num_frame = slide.shapes.add_textbox(Inches(0.52), top_pos + Inches(0.05), Inches(0.4), Inches(0.4))
        p_num = num_frame.text_frame.paragraphs[0]
        p_num.text = str(i + 1)
        p_num.font.size, p_num.font.color.rgb = Pt(14), RGBColor(255, 255, 255)

        # إضافة النص المرتب
        content_box = slide.shapes.add_textbox(Inches(1.1), top_pos, Inches(8.5), Inches(1))
        tf = content_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        
        if lang_choice == "مزدوج" and isinstance(pt_data, dict):
            p.text = f"{pt_data.get('ar', '')}\n{pt_data.get('en', '')}"
            p.font.size = Pt(11)
        else:
            p.text = str(pt_data)
            p.font.size = Pt(13)
        
        p.alignment = PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT

# --- 3. تشغيل التطبيق ---
with st.container():
    topic = st.text_input("🎯 موضوع العرض", placeholder="أدخل موضوعك هنا...")
    count = st.select_slider("عدد الشرائح", options=[3, 5, 10], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])

    if st.button("🚀 صنع العرض الاحترافي المطور"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key: st.error("يرجى التأكد من مفتاح الـ API!")
        else:
            with st.spinner('🎨 جاري تنسيق الإنفوجرافيك وتوزيع النقاط...'):
                try:
                    p_fmt = "{'ar': 'نص عربي مختصر', 'en': 'Short English'}" if lang == "مزدوج" else "'نص النقطة'"
                    prompt = f"Create {count} slides about '{topic}'. Return ONLY JSON: [{{'title': '...', 'points': [{p_fmt}, {p_fmt}, {p_fmt}, {p_fmt}]}}]"
                    
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    data = json.loads(res.json()['choices'][0]['message']['content'].strip('`json \n'))
                    prs = Presentation()
                    for i, s_data in enumerate(data):
                        slide = prs.slides.add_slide(prs.slide_layouts[6])
                        apply_pro_layout(slide, s_data, i, lang)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['file'] = buf.getvalue()
                except Exception as e: st.error(f"حدث خطأ في البيانات: {e}")

if 'file' in st.session_state:
    st.success("✅ تم بناء العرض بنجاح!")
    st.download_button("📥 تحميل الإنفوجرافيك المرقم", data=st.session_state['file'], file_name="Digital_Path_Final.pptx")
