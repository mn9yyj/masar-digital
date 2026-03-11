import streamlit as st
import requests, json, os, io, random
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. واجهة المستخدم المتطورة ---
st.set_page_config(page_title="المسار 🖥️ الرقمي - نسخة التصميم اللامحدود", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #0d0d0d; direction: rtl; }
    .brand { font-size: 40px; font-weight: 900; text-align: center; color: #00d2ff; margin-bottom: 25px; }
    .centered-box { max-width: 650px; margin: 0 auto; background: #181818; padding: 25px; border-radius: 15px; border: 1px solid #333; }
    .stButton>button { width: 100%; border-radius: 30px !important; background: linear-gradient(90deg, #00d2ff, #3a7bd5) !important; height: 50px; font-weight: bold; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي - Pro Design</div>', unsafe_allow_html=True)

# --- 2. محرك رسم القوالب المتغيرة والترقيم ---
def apply_pro_layout(slide, item, index, lang_choice):
    # مصفوفة ألوان عصرية (أزرق، وردي، أخضر، برتقالي)
    palette = [RGBColor(0, 210, 255), RGBColor(255, 107, 107), RGBColor(29, 209, 161), RGBColor(254, 202, 87)]
    color = palette[index % len(palette)]
    
    # اختيار النمط (تغيير القالب لكل شريحة)
    style = index % 3 

    # أ) إضافة لمسة هندسية (تصحيح خطأ الأسماء السابقة)
    if style == 0: # شكل بيضاوي جانبي
        shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.5), Inches(-0.5), Inches(2.5), Inches(2.5))
    elif style == 1: # مستطيل علوي
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(0.8))
    else: # شكل سداسي (بدلاً من المثلث المسبب للخطأ)
        shape = slide.shapes.add_shape(MSO_SHAPE.HEXAGON, Inches(8.5), Inches(0.2), Inches(1.2), Inches(1.2))
    
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.width = 0

    # ب) العنوان الرئيسي المنسق
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.2), Inches(8), Inches(1))
    p_title = title_box.text_frame.paragraphs[0]
    p_title.text = str(item.get('title', 'تحليل الموضوع'))
    p_title.font.size, p_title.font.bold = Pt(24), True
    p_title.alignment = PP_ALIGN.CENTER

    # ج) توزيع النقاط مع الترقيم التلقائي
    points = item.get('points', [])
    for i, pt_data in enumerate(points[:4]):
        top_pos = Inches(1.5 + (i * 1.3))
        left_pos = Inches(1)
        
        # رسم دائرة الرقم (ترقيم الموضوع)
        num_circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, left_pos - Inches(0.6), top_pos + Inches(0.1), Inches(0.4), Inches(0.4))
        num_circle.fill.solid()
        num_circle.fill.fore_color.rgb = color
        
        # وضع الرقم داخل الدائرة
        num_frame = slide.shapes.add_textbox(left_pos - Inches(0.58), top_pos + Inches(0.05), Inches(0.4), Inches(0.4))
        p_num = num_frame.text_frame.paragraphs[0]
        p_num.text = str(i + 1)
        p_num.font.size, p_num.font.color.rgb = Pt(14), RGBColor(255, 255, 255)

        # إضافة نص النقطة (عربي/إنجليزي)
        box = slide.shapes.add_textbox(left_pos, top_pos, Inches(8), Inches(1))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        
        if lang_choice == "مزدوج":
            # دمج العربي مع الإنجليزي في نقطة واحدة مع الترقيم
            p.text = f"{pt_data.get('ar', '')}\n{pt_data.get('en', '')}"
            p.font.size = Pt(12)
        else:
            p.text = str(pt_data)
            p.font.size = Pt(13)
        
        p.alignment = PP_ALIGN.RIGHT if lang_choice != "English" else PP_ALIGN.LEFT

# --- 3. إدارة التشغيل والـ API ---
with st.container():
    st.markdown('<div class="centered-box">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض", placeholder="مثلاً: تأثير التكنولوجيا في التعليم")
    slides_num = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    
    if st.button("🚀 صنع العرض بنمط الإنفوجرافيك"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key: st.error("تأكد من إعداد Secrets!")
        else:
            with st.spinner('🎨 جاري تنويع التصاميم وترقيم النقاط...'):
                try:
                    p_fmt = "{'ar': 'نص عربي كثيف', 'en': 'Detailed English'}" if lang == "مزدوج" else "'نص كثيف'"
                    prompt = f"Create {slides_num} slides about '{topic}'. For each, return 'title' and 4 'points' as a list of {p_fmt}. Return ONLY JSON."
                    
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    raw_data = res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw_data)
                    
                    prs = Presentation()
                    for i, slide_data in enumerate(data):
                        slide = prs.slides.add_slide(prs.slide_layouts[6])
                        apply_pro_layout(slide, slide_data, i, lang)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['final_pptx'] = buf.getvalue()
                except Exception as e: st.error(f"خطأ في معالجة البيانات: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'final_pptx' in st.session_state:
    st.markdown('<div class="centered-box" style="margin-top:20px;">', unsafe_allow_html=True)
    st.success("✅ تم بناء العرض بتصاميم متغيرة ونقاط مرقمة!")
    st.download_button("📥 تحميل عرض الإنفوجرافيك المطور", data=st.session_state['final_pptx'], file_name="Digital_Path_Infographic.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
