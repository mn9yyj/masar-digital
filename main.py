import streamlit as st
import requests, json, io, random
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


# -----------------------------
# إعداد واجهة التطبيق
# -----------------------------
st.set_page_config(page_title="مولد العروض الذكي", layout="wide")

st.markdown("""
<style>
.stApp{
background:#0e0e0e;
direction:rtl
}

.title{
text-align:center;
font-size:36px;
font-weight:900;
color:#00d2ff;
margin-bottom:20px
}

.stButton>button{
width:100%;
height:50px;
border-radius:15px;
background:linear-gradient(90deg,#00d2ff,#3a7bd5);
color:white;
font-weight:bold;
border:none
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">مولد عروض PowerPoint الذكي</div>', unsafe_allow_html=True)


# -----------------------------
# لوحة الألوان
# -----------------------------
palette = [
RGBColor(255,193,7),
RGBColor(255,87,34),
RGBColor(0,188,212),
RGBColor(63,81,181),
RGBColor(76,175,80)
]


# -----------------------------
# شريحة الغلاف
# -----------------------------
def cover_slide(slide,title,color):

    shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(2.5),Inches(2),
    Inches(5),Inches(1.8)
    )

    shape.fill.solid()
    shape.fill.fore_color.rgb=color
    shape.line.width=0

    tf=shape.text_frame
    p=tf.paragraphs[0]
    p.text=title
    p.font.size=Pt(40)
    p.font.bold=True
    p.font.color.rgb=RGBColor(255,255,255)
    p.alignment=PP_ALIGN.CENTER


# -----------------------------
# نقاط مرقمة
# -----------------------------
def bullet_slide(slide,title,points,color):

    title_box=slide.shapes.add_textbox(
    Inches(1),Inches(0.3),
    Inches(8),Inches(1)
    )

    p=title_box.text_frame.paragraphs[0]
    p.text=title
    p.font.size=Pt(30)
    p.font.bold=True
    p.alignment=PP_ALIGN.CENTER

    for i,pt in enumerate(points[:4]):

        top=Inches(1.5+i*1.2)

        circle=slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(0.8),top,
        Inches(0.5),Inches(0.5)
        )

        circle.fill.solid()
        circle.fill.fore_color.rgb=color

        num=slide.shapes.add_textbox(
        Inches(0.9),top,
        Inches(0.5),Inches(0.5)
        )

        num_tf=num.text_frame.paragraphs[0]
        num_tf.text=str(i+1)
        num_tf.font.size=Pt(14)
        num_tf.font.color.rgb=RGBColor(255,255,255)

        text=slide.shapes.add_textbox(
        Inches(1.6),top,
        Inches(8),Inches(1)
        )

        p=text.text_frame.paragraphs[0]
        p.text=str(pt)
        p.font.size=Pt(16)


# -----------------------------
# أعمدة
# -----------------------------
def column_slide(slide,title,points,color):

    title_box=slide.shapes.add_textbox(
    Inches(1),Inches(0.3),
    Inches(8),Inches(1)
    )

    p=title_box.text_frame.paragraphs[0]
    p.text=title
    p.font.size=Pt(30)
    p.font.bold=True
    p.alignment=PP_ALIGN.CENTER

    for i,pt in enumerate(points[:3]):

        box=slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1+i*3),
        Inches(2),
        Inches(2.5),
        Inches(2)
        )

        box.fill.solid()
        box.fill.fore_color.rgb=color

        tf=box.text_frame.paragraphs[0]
        tf.text=str(pt)
        tf.font.size=Pt(16)
        tf.font.color.rgb=RGBColor(255,255,255)
        tf.alignment=PP_ALIGN.CENTER


# -----------------------------
# دوائر إنفوجرافيك
# -----------------------------
def circle_infographic(slide,title,points,color):

    title_box=slide.shapes.add_textbox(
    Inches(1),Inches(0.3),
    Inches(8),Inches(1)
    )

    p=title_box.text_frame.paragraphs[0]
    p.text=title
    p.font.size=Pt(30)
    p.font.bold=True
    p.alignment=PP_ALIGN.CENTER

    for i,pt in enumerate(points[:4]):

        circle=slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(1.5+i*2),
        Inches(2.2),
        Inches(1.5),
        Inches(1.5)
        )

        circle.fill.solid()
        circle.fill.fore_color.rgb=color

        tf=circle.text_frame.paragraphs[0]
        tf.text=str(pt)
        tf.font.size=Pt(12)
        tf.font.color.rgb=RGBColor(255,255,255)
        tf.alignment=PP_ALIGN.CENTER


# -----------------------------
# خاتمة
# -----------------------------
def ending_slide(slide,title,color):

    circle=slide.shapes.add_shape(
    MSO_SHAPE.OVAL,
    Inches(4),
    Inches(1.5),
    Inches(2),
    Inches(2)
    )

    circle.fill.solid()
    circle.fill.fore_color.rgb=color

    tf=circle.text_frame.paragraphs[0]
    tf.text=title
    tf.font.size=Pt(26)
    tf.font.bold=True
    tf.font.color.rgb=RGBColor(255,255,255)
    tf.alignment=PP_ALIGN.CENTER


# -----------------------------
# واجهة الإدخال
# -----------------------------
topic=st.text_input("موضوع العرض")

slides_count=st.select_slider(
"عدد الشرائح",
options=[5,8,10,15],
value=8
)


# -----------------------------
# إنشاء العرض
# -----------------------------
if st.button("إنشاء العرض"):

    api_key=st.secrets.get("OPENROUTER_API_KEY")

    prompt=f"""
Create {slides_count} slides about {topic}
Return JSON only like:

[
{{"title":"title","points":["p1","p2","p3","p4"]}}
]
"""

    res=requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization":f"Bearer {api_key}"},
    json={
    "model":"google/gemini-2.0-flash-001",
    "messages":[{"role":"user","content":prompt}]
    })

    data=json.loads(
    res.json()["choices"][0]["message"]["content"].strip("`json")
    )

    prs=Presentation()

    for i,item in enumerate(data):

        slide=prs.slides.add_slide(prs.slide_layouts[6])
        color=random.choice(palette)

        if i==0:
            cover_slide(slide,item["title"],color)

        elif i==len(data)-1:
            ending_slide(slide,"الخاتمة",color)

        else:

            style=random.choice([
            "bullets",
            "columns",
            "circles"
            ])

            if style=="bullets":
                bullet_slide(slide,item["title"],item["points"],color)

            elif style=="columns":
                column_slide(slide,item["title"],item["points"],color)

            else:
                circle_infographic(slide,item["title"],item["points"],color)


    buf=io.BytesIO()
    prs.save(buf)

    st.download_button(
    "تحميل العرض",
    data=buf.getvalue(),
    file_name="presentation.pptx"
    )