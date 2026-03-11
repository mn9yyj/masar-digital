import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# --- واجهة المستخدم ---
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

with st.container():
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    topic = st.text_input("🎯 موضوع العرض الرئيسي")
    slides_num = st.select_slider("عدد الشرائح", options=[3, 5, 10, 15], value=5)
    lang = st.selectbox("🌐 اللغة", ["العربية", "English", "مزدوج"])
    generate_btn = st.button("🚀 صنع العرض المطور")
    st.markdown('</div>', unsafe_allow_html=True)

# --- معالج التصميم والمحتوى ---
if generate_btn and topic:
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("❌ خطأ: يرجى إضافة OPENROUTER_API_KEY في إعدادات Secrets")
    else:
        with st.spinner('جاري التحليل والتصميم...'):
            try:
                prompt = f"Create {slides_num} slides for '{topic}'. Provide very deep, detailed info. Language: {lang}. Return ONLY a clean JSON array: [{{'title': '...', 'body': '...'}}]"
                res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {api_key}"},
                                    json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
                
                response_data = res.json()
                if 'choices' not in response_data:
                    st.error(f"فشل الاتصال بالذكاء الاصطناعي. تأكد من شحن الرصيد أو صحة المفتاح.")
                else:
                    raw_content = response_data['choices'][0]['message']['content']
                    # تنظيف الـ JSON من أي علامات زائدة
                    clean_json = raw_content.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    prs = Presentation()
                    for item in data:
                        slide = prs.slides.add_slide(prs.slide_layouts[1])
                        # تصميم العنوان
                        title = slide.shapes.title
                        title.text = item.get('title', 'بدون عنوان')
                        # تصميم المحتوى الكثيف
                        body = slide.placeholders[1]
                        body.text = item.get('body', 'لا يوجد محتوى')
                        for p in body.text_frame.paragraphs:
                            p.font.size = Pt(12)
                            p.alignment = PP_ALIGN.RIGHT if lang != "English" else PP_ALIGN.LEFT
                    
                    buf = io.BytesIO()
                    prs.save(buf)
                    st.session_state['file'] = buf.getvalue()
                    st.session_state['name'] = topic
            except Exception as e:
                st.error(f"حدث خطأ في قراءة البيانات: {str(e)}")

if 'file' in st.session_state:
    st.markdown('<div class="centered-ui">', unsafe_allow_html=True)
    st.download_button("📥 تحميل البوربوينت النهائي", data=st.session_state['file'], file_name=f"{st.session_state['name']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
