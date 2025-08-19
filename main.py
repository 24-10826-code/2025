import streamlit as st

st.set_page_config(page_title="MBTI 직업 추천", page_icon="💼", layout="centered")

st.title("💼 MBTI 기반 직업 추천")
st.write("당신의 MBTI 성격 유형에 따라 잘 맞는 직업을 추천해드립니다!")
mbti_types = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

user_mbti = st.selectbox("당신의 MBTI를 선택하세요:", mbti_types)
job_recommendations = {
    "INTJ": ["과학자", "전략 컨설턴트", "데이터 분석가"],
    "INFP": ["작가", "상담사", "예술가"],
    "ENTP": ["기업가", "마케터", "기술 혁신가"],
    "ESFP": ["배우", "이벤트 플래너", "여행 가이드"],
    # ... 나머지 유형도 채우기
}
if user_mbti:
    st.subheader(f"✨ {user_mbti} 유형에게 어울리는 직업 추천")
    recommendations = job_recommendations.get(user_mbti, ["추천 데이터 없음"])
    for job in recommendations:
        st.write(f"- {job}")
