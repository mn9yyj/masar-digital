import streamlit as st
import requests, json, os, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# --- 1. واجهة مستخدم متطورة ---
st.set_page_config(page_title="المسار 🖥️ الرقمي - المصمم الذكي", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"], footer, header {display: none !important;}
    .stApp { background: #0a0a0a; color: white; direction: rtl; }
    .brand { font-size: 45px; font-weight: 900; text-align: center; background: linear-gradient(45deg, #706fd3, #4834d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 15px !important; background: linear-gradient(90deg, #4834d4, #686de0) !important; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="brand">المسار 🖥️ الرقمي | المصمم الذكي</div>', unsafe_allow_html=True)

# --- 2. محرك التنسيق اللوني حسب الموضوع ---
def get_theme_colors(topic):
    topic = topic.lower()
    # تقني / تكنولوجي
    if any(word in topic for word in ['تقني', 'برمج', 'حاسب', 'tech', 'ai', 'software']):
        return RGBColor(0, 168, 255), RGBColor(30, 39, 46) # أزرق تقني
    # طبي / صحي
    elif any(word in topic for word in ['طب', 'صحي', 'مرض', 'health', 'medical']):
        return RGBColor(46, 204, 113), RGBColor(255, 255, 255) # أخضر طبي
    # تجاري / إداري
    elif any(word in topic for word in ['إدار', 'بزنس', 'مال', 'business', 'money']):
        return RGBColor(44, 62, 80), RGBColor(236, 240, 241) # كحلي رسمي
    # عام
    else:
        return RGBColor(112, 111, 211), RGBColor(255, 255, 255) # بنفسجي المسار الرقمي

# --- 3. جلب المحتوى العميق ---
def get_pro_content(topic, count, lang):
    api_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    prompt = (
        f"Act as an expert consultant. Create {count} professional slides about '{topic}'. "
        f"Each slide MUST have a very detailed, factual, and analytical body (min 200 words). "
        f"Language: {lang}. Style: Academic and Deep. "
        "Return ONLY JSON: [{'title': '...', 'body': '...'}]"
    )
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {api_key}"},
                            json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "user", "content": prompt}]})
        data = res.json()
        if 'choices' not in data: return None
        return json.loads(data['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip())
    except: return None

# --- 4. واجهة المدخلات ---
with st.container():
    col_main = st.columns([1, 2, 1])[1]
    with col_main:
        topic = st.text_input("💎 موضوع العرض (سيتم تصميم الثيم بناءً عليه)", placeholder="مثلاً: مستقبل الذكاء الاصطناعي في الطب")
        slides_num = st.slider("عدد الشرائح", 3, 15, 5)
        lang = st.selectbox("🌐 لغة المحتوى", ["العربية", "English", "مزدوج"])
        generate_btn = st.button("🎨 توليد وتصميم العرض الاحترافي")

# --- 5. محرك التصميم المعتمد على الموضوع ---
if generate_btn and topic:
    with st.spinner('🎨 المحرك الذكي يحلل الموضوع ويصمم الشرائح...'):
        content_data = get_pro_content(topic, slides_num, lang)
        if content_data:
            prs = Presentation()
            primary_color, bg_color = get_theme_colors(topic)
            
            for item in content_data:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                
                # تنسيق العنوان
                title_shape = slide.shapes.title
                title_shape.text = str(item['title'])
                title_paragraph = title_shape.text_frame.paragraphs[0]
                title_paragraph.font.size = Pt(26)
                title_paragraph.font.bold = True
                title_paragraph.font.color.rgb = primary_color
                
                # تنسيق المحتوى الكثيف
                body_shape = slide.placeholders[1]
                body_shape.text = str(item['body'])
                for p in body_shape.text_frame.paragraphs:
                    p.font.size = Pt(11) # خط صغير للمعلومات الكثيرة
                    p.font.name = "Arial"
                    p.alignment = PP_ALIGN.RIGHT if lang != "English" else PP_ALIGN.LEFT
                    p.space_after = Pt(10)

                # إضافة لمسة تصميمية (خط سفلي بلون الثيم)
                line = slide.shapes.add_connector(1, Inches(0.5), Inches(1.2), Inches(9.5), Inches(1.2))
                line.line.color.rgb = primary_color

            buf = io.BytesIO()
            prs.save(buf)
            st.session_state['pro_file'] = buf.getvalue()
            st.session_state['pro_name'] = topic

if 'pro_file' in st.session_state:
    st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
    st.success(f"✨ تم تصميم عرض '{st.session_state['pro_name']}' بنجاح!")
    st.download_button("📥 تحميل العرض المصمم ذكياً", 
                       data=st.session_state['pro_file'], 
                       file_name=f"{st.session_state['pro_name']}.pptx")
    st.markdown('</div>', unsafe_allow_html=True)
