
import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# --- OpenAI API KEY ---
# 1. .env의 OPENAI_API_KEY 우선 사용, 없으면 하드코딩 값 사용
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY or API_KEY.strip() == "":
    # 여기에 실제로 유효한 OpenAI API Key를 입력하세요
    API_KEY = "sk-여기에_실제_유효한_API_KEY_입력"
openai.api_key = API_KEY

import requests
from datetime import datetime

# 타로 카드 정보 (카드명, 의미, 프롬프트)
tarot_cards = [
    ("The Fool", "새로운 시작, 자유, 순수함, 모험", "A tarot card of The Fool, vibrant, mystical, detailed, fantasy art"),
    ("The Magician", "의지, 창조, 자원, 힘", "A tarot card of The Magician, magical, powerful, detailed, fantasy art"),
    ("The High Priestess", "직관, 신비, 잠재력, 지혜", "A tarot card of The High Priestess, mysterious, wise, detailed, fantasy art"),
    ("The Empress", "풍요, 모성, 자연, 창조성", "A tarot card of The Empress, abundant, nurturing, detailed, fantasy art"),
    ("The Emperor", "권위, 구조, 통제, 안정", "A tarot card of The Emperor, authoritative, structured, detailed, fantasy art"),
    ("The Hierophant", "전통, 신념, 영적 지도", "A tarot card of The Hierophant, spiritual, traditional, detailed, fantasy art"),
    ("The Lovers", "사랑, 조화, 관계, 선택", "A tarot card of The Lovers, romantic, harmonious, detailed, fantasy art"),
    ("The Chariot", "승리, 의지, 결단력", "A tarot card of The Chariot, victorious, determined, detailed, fantasy art"),
    ("Strength", "용기, 인내, 힘, 자제력", "A tarot card of Strength, courageous, patient, detailed, fantasy art"),
    ("The Hermit", "고독, 탐구, 내면의 지혜", "A tarot card of The Hermit, introspective, wise, detailed, fantasy art")
]

st.set_page_config(page_title="AI 타로카드 3장 뽑기", page_icon="🃏")
st.title("🃏 AI 타로카드 3장 뽑기")
st.write(f"오늘 날짜: {datetime.now().strftime('%Y-%m-%d')}")



if not API_KEY or API_KEY.startswith("sk-여기에"):
    st.error("OpenAI API Key가 설정되지 않았거나 올바르지 않습니다. .env 파일에 OPENAI_API_KEY를 등록하거나, 코드에 유효한 키를 입력하세요.")
else:
    st.info("아래 버튼을 눌러 타로카드 3장을 AI로 생성하세요.")
    if st.button("타로카드 3장 생성하기"):
        # 3장 무작위 선택
        selected = st.session_state.get('selected_cards')
        if not selected:
            import random
            selected = random.sample(tarot_cards, 3)
            st.session_state['selected_cards'] = selected
        else:
            selected = st.session_state['selected_cards']

        images = []
        for card in selected:
            prompt = card[2]
            try:
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )
                image_url = response.data[0].url
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    st.error("이미지 생성 API 사용량 제한(429)에 도달했습니다. 잠시 후 다시 시도하거나, OpenAI 계정의 사용량/결제 상태를 확인하세요.")
                elif "401" in err_msg or "invalid_api_key" in err_msg:
                    st.error("API Key가 올바르지 않거나 권한이 없습니다. 유효한 OpenAI API Key를 사용하세요.")
                elif "400" in err_msg and "size" in err_msg:
                    st.error("이미지 크기 파라미터가 잘못되었습니다. 지원되는 크기(1024x1024, 1024x1792, 1792x1024)만 사용하세요.")
                else:
                    st.error(f"이미지 생성 오류: {e}")
                image_url = None
            images.append(image_url)

        st.session_state['tarot_images'] = images

    # 이미지가 있으면 보여주기
    if 'tarot_images' in st.session_state and 'selected_cards' in st.session_state:
        st.write("아래 카드 중 하나를 선택하세요:")
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if st.session_state['tarot_images'][i]:
                if col.button(f"카드 {i+1} 선택"):
                    st.session_state['chosen'] = i
            col.image(st.session_state['tarot_images'][i], use_column_width=True)

        if 'chosen' in st.session_state:
            idx = st.session_state['chosen']
            card_name, meaning, _ = st.session_state['selected_cards'][idx]
            st.success(f"오늘의 타로: {card_name}\n의미: {meaning}")
