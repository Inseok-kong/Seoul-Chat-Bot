# app.py (Streamlit UI + Persona + 언어 선택 + 스타일링 + 로그 + 경로)
import streamlit as st
import pandas as pd
import time
from rag import get_rag_answer
from persona import create_persona
from translate import translate_text
from map_utils import extract_locations, show_locations_on_map
from chat_logger import log_chat

# ----- UI 설정 -----
st.set_page_config(page_title="서울 문화 추천 챗봇", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f9f9f9; font-family: 'Nanum Gothic', sans-serif;}
    .stTextInput > div > div > input {font-size: 16px;}
    .stSelectbox > div > div > div {font-size: 16px;}
    </style>
""", unsafe_allow_html=True)

st.title("🎨 서울 문화 탐험 챗봇")
st.markdown("서울시의 야경, 음식, 관광지, 문화행사에 대해 궁금한 걸 물어보세요!")

# ----- 사이드바에서 사용자 정보 받기 -----
st.sidebar.header("📌 당신에 대해 알려주세요")

# (1) 성별
gender = st.sidebar.selectbox("성별", ["남성", "여성"])

# (2) 나이대
age = st.sidebar.selectbox("나이대", ["10대", "20대", "30대", "40대", "50대 이상"])

# (3) 거주 지역
region = st.sidebar.selectbox("거주 지역", ["서울", "수도권(서울 외 경기/인천)", "그 외 지역"])

# (4) 언어 선택
language = st.sidebar.selectbox("답변 받을 언어", ["한국어", "English", "日本語", "中文"])

# (5) 현재 위치 기반 추천 포함 여부
use_location = st.sidebar.checkbox("현재 위치를 질문에 반영할까요?")
location = ""
if use_location:
    location = st.sidebar.text_input("현재 위치를 입력하세요 (예: 강남구)")

# Persona 생성
persona = create_persona(gender, age, region)
st.sidebar.markdown(f"🧍 **[당신의 Persona]**\n{persona}")

# ----- 질문 받기 -----
st.markdown("## 🤖 궁금한 걸 입력해 보세요!")
question = st.text_input("질문 입력", placeholder="예: 서울에서 데이트하기 좋은 야경 명소 추천해줘")

if question:
    with st.spinner("답변을 생성 중입니다..."):
        translated_question = translate_text(question, language)
        answer = get_rag_answer(translated_question, persona, use_location, location)
        translated_answer = translate_text(answer, language)

        # 한 글자씩 출력 효과
        st.markdown("### 💬 답변")
        answer_container = st.empty()
        full_text = ""
        for char in translated_answer:
            full_text += char
            answer_container.markdown(
                f"<div style='font-size:18px; line-height:1.6;'>{full_text}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.03)

        # 로그 저장
        log_chat(question, translated_answer, language)

        # 지도 표시 + 경로 연결
        places = extract_locations(translated_answer)
        if places:
            st.markdown("### 🗺️ 추천 장소 지도 및 경로")
            show_locations_on_map(places, start_point=location if use_location else None)
