import streamlit as st
import requests, json, io
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


# ---------------------------
# واجهة التطبيق
# ---------------------------
st.set_page_config(page_title="المسار الرقمي", layout="wide")

st.markdown("""
<style>
.stApp {background:#0e0e0e;direction:rtl}
.brand{
font-size:35px;
font-weight:900;
text-align:center;
color:#00d2ff;
margin:20px
}
.stButton>button{
width:100%;
border-radius:20px;
height:50px;
font-weight:bold;
background:linear-gradient(90deg,#00d2ff,#3a7bd5);
border:none
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">المسار الرقمي 🖥️ مولد العروض</div>', unsafe_allow_html=True)


# ---------------------------
# محرك تصميم الشرائح
# ---------------------------
def apply_pro_layout(slide, item, index):

    palette = [
        RGBColor(255,193,7),
        RGBColor(255,87,34),
        RGBColor(0,188,212),
        RGBColor(63,81,181)
    ]

    color = palette[index % len(palette)]
    style = index % 5


    # ----------------
    # شريحة الغلاف
    # ----------------
    if style == 0:

        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(2.5), Inches(2),
            Inches(5), Inches(1.5)
        )

        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.width = 0

        tf = shape.text_frame
        p = tf.paragraphs[0]

        p.text = item.get("title","العنوان الرئيسي")
        p.font.size = Pt(36)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER



    # ----------------
    # نقاط مرقمة
    # ----------------
    elif style == 1:

        title = slide.shapes.add_textbox(
            Inches(1), Inches(0.3),
            Inches(8), Inches(1)
        )

        p = title.text_frame.paragraphs[0]
        p.text = item.get("title","العنوان")
        p.font.size = Pt(28)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER

        points = item.get("points",[])

        for i,pt in enumerate(points[:4]):

            top = Inches(1.5 + i*1.2)

            circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(0.8), top,
                Inches(0.5), Inches(0.5)
            )

            circle.fill.solid()
            circle.fill.fore_color.rgb = color

            num = slide.shapes.add_textbox(
                Inches(0.9), top,
                Inches(0.5), Inches(0.5)
            )

            num_tf = num.text_frame.paragraphs[0]
            num_tf.text = str(i+1)
            num_tf.font.size = Pt(14)
            num_tf.font.color.rgb = RGBColor(255,255,255)

            text = slide.shapes.add_textbox(
                Inches(1.5), top,
                Inches(8), Inches(1)
            )

            p = text.text_frame.paragraphs[0]
            p.text = str(pt)
            p.font.size = Pt(16)



    # ----------------
    # أعمدة
    # ----------------
    elif style == 2:

        title = slide.shapes.add_textbox(
            Inches(1), Inches(0.3),
            Inches(8), Inches(1)
        )

        p = title.text_frame.paragraphs[0]
        p.text = item.get("title","العنوان")
        p.font.size = Pt(28)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER

        points = item.get("points",[])

        for i,pt in enumerate(points[:3]):

            box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(1 + i*3),
                Inches(2),
                Inches(2.5),
                Inches(2)
            )

            box.fill.solid()
            box.fill.fore_color.rgb = color

            tf = box.text_frame.paragraphs[0]

            tf.text = str(pt)
            tf.font.size = Pt(14)
            tf.font.color.rgb = RGBColor(255,255,255)
            tf.alignment = PP_ALIGN.CENTER



    # ----------------
    # نص + شكل
    # ----------------
    elif style == 3:

        title = slide.shapes.add_textbox(
            Inches(1), Inches(0.3),
            Inches(8), Inches(1)
        )

        p = title.text_frame.paragraphs[0]
        p.text = item.get("title","العنوان")
        p.font.size = Pt(26)
        p.font.bold = True

        rect = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(6),
            Inches(2),
            Inches(3),
            Inches(2)
        )

        rect.fill.solid()
        rect.fill.fore_color.rgb = color

        text = slide.shapes.add_textbox(
            Inches(1),
            Inches(2),
            Inches(4.5),
            Inches(2)
        )

        p = text.text_frame.paragraphs[0]
        p.text = "\n".join(item.get("points",[]))
        p.font.size = Pt(16)



    # ----------------
    # الخاتمة
    # ----------------
    else:

        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(4),
            Inches(1.5),
            Inches(2),
            Inches(2)
        )

        circle.fill.solid()
        circle.fill.fore_color.rgb = color

        tf = circle.text_frame.paragraphs[0]

        tf.text = "الخاتمة"
        tf.font.size = Pt(24)
        tf.font.bold = True
        tf.font.color.rgb = RGBColor(255,255,255)
        tf.alignment = PP_ALIGN.CENTER


# ---------------------------
# واجهة الإدخال
# ---------------------------
topic = st.text_input("موضوع العرض")

count = st.select_slider(
"عدد الشرائح",
options=[3,5,10],
value=5
)


# ---------------------------
# إنشاء العرض
# ---------------------------
if st.button("إنشاء العرض"):

    api_key = st.secrets.get("OPENROUTER_API_KEY")

    prompt = f"""
Create {count} slides about {topic}.
Return JSON only like:
[
{{"title":"title","points":["p1","p2","p3","p4"]}}
]
"""

    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model":"google/gemini-2.0-flash-001",
            "messages":[{"role":"user","content":prompt}]
        }
    )

    data = json.loads(
        res.json()["choices"][0]["message"]["content"]
        .strip("`json")
    )

    prs = Presentation()

    for i,slide_data in enumerate(data):

        slide = prs.slides.add_slide(
            prs.slide_layouts[6]
        )

        apply_pro_layout(
            slide,
            slide_data,
            i
        )

    buf = io.BytesIO()

    prs.save(buf)

    st.download_button(
        "تحميل العرض",
        data=buf.getvalue(),
        file_name="presentation.pptx"
    )