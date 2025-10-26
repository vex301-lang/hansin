# -*- coding: utf-8 -*-
import io, re
from typing import List, Tuple
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="한신 초등 8컷 은유 만화", page_icon="✨")
st.title("✨ 한신 초등학교 친구들의 이야기 실력을 볼까요?")
st.caption("좋아하는 단어 3개와 8단 이야기로 나만의 만화를 만들어 보자! (각 칸을 '완성'해서 제출)")

BANNED_PATTERNS = [r"살인", r"죽이", r"폭력", r"피바다", r"학대", r"총", r"칼", r"폭탄",
    r"kill", r"murder", r"gun", r"knife", r"blood", r"assault", r"bomb",
    r"성\s*행위", r"야동", r"포르노", r"음란", r"가슴", r"성기", r"자위",
    r"porn", r"sex", r"xxx", r"nude", r"naked"]
BAN_RE = re.compile("|".join(BANNED_PATTERNS), re.IGNORECASE)

def words_valid(words: List[str]) -> Tuple[bool, str]:
    for w in words:
        if not w: return False, "단어 3개를 모두 입력해 주세요."
        if BAN_RE.search(w): return False, "적절하지 않은 단어입니다. 다시 입력해 주세요"
    return True, "OK"

colw1, colw2, colw3 = st.columns(3)
w1 = colw1.text_input("단어 1", max_chars=12, key="fav_w1")
w2 = colw2.text_input("단어 2", max_chars=12, key="fav_w2")
w3 = colw3.text_input("단어 3", max_chars=12, key="fav_w3")

TITLES = ["옛날에", "그리고 매일", "그러던 어느 날", "그래서", "그래서", "그래서", "마침내", "그날 이후"]
for i in range(8):
    st.session_state.setdefault(f"story_text_{i}", "")
    st.session_state.setdefault(f"story_done_{i}", False)

st.subheader("2) 8단 이야기 쓰기 ✍️ (각 칸을 완성으로 제출)")

for i, title in enumerate(TITLES):
    with st.form(f"story_form_{i}"):
        disabled = st.session_state[f"story_done_{i}"]
        val = st.text_area(title, height=70, value=st.session_state[f"story_text_{i}"], disabled=disabled, key=f"story_area_{i}")
        col1, col2 = st.columns([1,1])
        if not disabled:
            done = col1.form_submit_button("완성 ✅", use_container_width=True)
            if done:
                if len(val.strip()) == 0: st.warning("내용을 입력해 주세요!")
                else:
                    st.session_state[f"story_text_{i}"] = val.strip()
                    st.session_state[f"story_done_{i}"] = True
                    st.success(f"'{title}' 칸이 완성되었어요! ✨")
        else:
            edit = col2.form_submit_button("수정 ✏️", use_container_width=True)
            if edit:
                st.session_state[f"story_done_{i}"] = False
                st.info(f"'{title}' 칸을 다시 편집할 수 있어요.")

PALETTE = [(255,239,213),(224,255,255),(255,245,238),(240,255,240),
           (255,250,205),(230,230,250),(250,240,230),(245,255,250)]
BORDER, TEXT = (60,60,60), (40,40,40)

def draw_centered_text(draw, box, text, font, fill, wrap=18):
    lines, line = [], ""
    for ch in text:
        if ch == "\n": lines.append(line); line=""; continue
        if len(line)>=wrap and ch!=" ": lines.append(line); line=ch
        else: line+=ch
    if line: lines.append(line)
    x0,y0,x1,y1 = box
    h=sum(font.getbbox(ln)[3] for ln in lines)+(len(lines)-1)*4
    y=y0+((y1-y0)-h)//2
    for ln in lines:
        w=font.getbbox(ln)[2]; x=x0+((x1-x0)-w)//2
        draw.text((x,y),ln,fill=fill,font=font); y+=font.getbbox(ln)[3]+4

def make_face(words, size=(220,220)):
    img=Image.new("RGBA",size,(0,0,0,0));d=ImageDraw.Draw(img)
    cx,cy=size[0]//2,size[1]//2
    d.ellipse([cx-100,cy-100,cx+100,cy+100],fill=(255,224,189,255),outline=BORDER,width=4)
    d.ellipse([cx-45,cy-35,cx-20,cy-10],fill=(0,0,0,255));d.ellipse([cx+20,cy-35,cx+45,cy-10],fill=(0,0,0,255))
    d.arc([cx-40,cy-5,cx+40,cy+45],start=200,end=340,fill=(0,0,0,255),width=4)
    glyphs,colors=["★","♥","◆"],[(255,105,180,200),(135,206,250,200),(144,238,144,200)]
    for i,w in enumerate(words): d.text((10+i*70,10),glyphs[i%3],fill=colors[i%3])
    return img

def render_comic(words,texts):
    W,H=1600,900;PAD=20;COLS,ROWS=4,2
    panel_w=(W-PAD*(COLS+1))//COLS;panel_h=(H-PAD*(ROWS+1))//ROWS
    canvas=Image.new("RGB",(W,H),(255,255,255));draw=ImageDraw.Draw(canvas)
    try: title_font=ImageFont.truetype("DejaVuSans.ttf",26); body_font=ImageFont.truetype("DejaVuSans.ttf",20)
    except: title_font=body_font=ImageFont.load_default()
    face=make_face(words)
    titles=TITLES
    for i in range(8):
        r,c=divmod(i,COLS)
        x0=PAD+c*(panel_w+PAD); y0=PAD+r*(panel_h+PAD)
        x1,y1=x0+panel_w,y0+panel_h
        draw.rounded_rectangle([x0,y0,x1,y1],radius=18,fill=PALETTE[i%len(PALETTE)],outline=BORDER,width=2)
        canvas.paste(face,(x0+12,y0+12),face)
        draw.text((x0+250,y0+18),titles[i],fill=TEXT,font=title_font)
        box=(x0+240,y0+60,x1-16,y1-16)
        draw_centered_text(draw,box,texts[i][:160],body_font,TEXT)
    return canvas

if st.button("8컷 만화 만들기 ✨"):
    words=[w1.strip(),w2.strip(),w3.strip()]
    ok,msg=words_valid(words)
    if not ok: st.error(msg)
    elif not all(st.session_state[f"story_done_{i}"] for i in range(8)):
        st.warning("모든 칸을 완성해야 만화를 만들 수 있어요!")
    else:
        texts=[st.session_state[f"story_text_{i}"] for i in range(8)]
        img=render_comic(words,texts)
        st.image(img,caption="나만의 8컷 은유 만화",use_column_width=True)
        buf=io.BytesIO();img.save(buf,format="PNG");buf.seek(0)
        st.download_button("📥 PNG로 저장",data=buf,file_name="hanshin_8cut_comic.png",mime="image/png")
