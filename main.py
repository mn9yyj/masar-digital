import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- 1. واجهة المستخدم (Dark Mode UI) ---
st.set_page_config(page_title="المسار 🖥️ الرقمي - نسخة الإنفوجرافيك", layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #0b0b0b; direction: rtl; }
    .brand { font-size: 38px; font-weight: 900; text-align: center; color: #00d2ff; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 25px !important; background: linear-gradient(135deg, #00d2ff, #3a7bd5) !important; height: 50px; font-weight: bold; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي - Infographic Mode</div>', unsafe_allow_html=True)

# --- 2. محرك رسم الإنفوجرافيك (لتحقيق نتيجة الصور) ---
def apply_infographic_theme(slide, item, index):
    # مصفوفة ألوان متغيرة لكل شريحة لتعطي شكل القوالب الاحترافية
    colors = [RGBColor(0, 210, 255), RGBColor(58, 123, 213), RGBColor(255, 159, 67), RGBColor(238, 82, 83)]
    color = colors[index % len(colors)]

    # أ) رسم "الكرة الجمالية" في زاوية الشريحة (كما في الصور)
    ball = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1), Inches(-1), Inches(3), Inches(3))
    ball.fill.solid()
    ball.fill.fore_color.rgb = color
    ball.line.width = 0

    # ب) العنوان الرئيسي (في منتصف الهيدر العلوي)
    title_box = slide.shapes.add_textbox(Inches(2), Inches(0.3), Inches(6), Inches(1))
    p_title = title_box.text_frame.paragraphs[0]
    p_title.text = str(item.get('title', ''))
    p_title.font.size, p_title.font.bold = Pt(28), True
    p_title.font.color.rgb = RGBColor(44, 62, 80)
    p_title.alignment = PP_ALIGN.CENTER

    # ج) توزيع النقاط (مثل القالب رقم 10 ورقم 1)
    points = item.get('points', [])
    for i, pt in enumerate(points[:4]): # نأخذ أول 4 نقاط فقط لنوزعها هندسياً
        left = Inches(0.5 + (i % 2) * 4.5)
        top = Inches(1.8 + (i // 2) * 2.2)
        
        # رسم دائرة صغيرة لكل نقطة
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, Inches(0.4), Inches(0.4))
        dot.fill.solid()
        dot.fill.fore_color.rgb = color
        
        # إضافة مربع النص بجانب الدائرة
        box = slide.shapes.add_textbox(left + Inches(0.5), top, Inches(3.8), Inches(2))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = str(pt)
        p.font.size = Pt(12)
        p.alignment = PP_ALIGN.RIGHT

# --- 3. طلب البيانات من الذكاء الاصطناعي بنمط الإنفوجرافيك ---
with st.container():
    topic = st.text_input("🎯 موضوع العرض", placeholder="مثلاً: جامعة أم القرى")
    slides_count = st.select_slider("عدد الشرائح", options=[3, 5, 10], value=5)
    
    if st.button("🚀 إصدار الإنفوجرافيك المطور"):
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key: st.error("تأكد من إعداد Secrets!")
        else:
            with st.spinner('🎨 جاري هندسة الشريحة وتوزيع العناصر...'):
                try:
                    # طلب النقاط مقسمة بدلاً من فقرة واحدة
                    prompt = f"Create {slides_count} academic slides about '{topic}'. For each slide, provide a 'title' and exactly 4 detailed 'points' in Arabic. Return ONLY JSON array: [{{'title': '...', 'points': ['...', '...', '...', '...']}}]"
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers={"Authorization": f"Bearer {api_key}"},
                                        json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                    
                    data = json.loads(res.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
                    prs = Presentation()
                    for i, slide_data in enumerate(data):
                        slide = prs.slides.add_slide(prs.slide_layouts[6])
                        apply_infographic_theme(slide, slide_data, i)
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['f_info'] = buf.getvalue()
                except Exception as e: st.error(f"حدث خطأ في قراءة البيانات: {e}")

if 'f_info' in st.session_state:
    st.download_button("📥 تحميل الإنفوجرافيك", data=st.session_state['f_info'], file_name="Infographic.pptx")
