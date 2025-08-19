import streamlit as st

# ✅ 페이지 기본 설정
st.set_page_config(page_title="💼 MBTI 직업 추천기", page_icon="🌈", layout="centered")

# ✅ 제목
st.markdown(
    """
    <h1 style="text-align: center; color: #6C63FF;">
        🌈 MBTI 성격 유형 기반 직업 추천 💼
    </h1>
    <p style="text-align: center; font-size:18px; color:gray;">
        당신의 성격에 꼭 맞는 ✨꿈의 직업✨을 찾아보세요!
    </p>
    """,
    unsafe_allow_html=True
)

# ✅ MBTI 선택
mbti_types = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

user_mbti = st.selectbox("🔮 당신의 MBTI를 선택해주세요:", mbti_types)

# ✅ 직업 추천 데이터
job_recommendations = {
    "INTJ": ["🧠 과학자", "📊 전략 컨설턴트", "📈 데이터 분석가"],
    "INTP": ["💡 발명가", "🔬 연구원", "🤖 프로그래머"],
    "ENTJ": ["👔 기업 임원", "📊 경영 컨설턴트", "📣 프로젝트 매니저"],
    "ENTP": ["🚀 기업가", "📱 마케터", "⚡ 혁신가"],
    "INFJ": ["🎨 작가", "🤝 상담사", "🌍 사회운동가"],
    "INFP": ["📝 시인", "🎭 예술가", "🧘‍♀️ 심리상담사"],
    "ENFJ": ["👩‍🏫 교사", "🎤 스피커", "🤗 인사 담당자"],
    "ENFP": ["🎬 배우", "✈️ 여행가이드", "📣 크리에이터"],
    "ISTJ": ["📚 회계사", "⚖️ 판사", "🏢 공무원"],
    "ISFJ": ["🏥 간호사", "👨‍👩‍👧‍👦 사회복지사", "📑 사서"],
    "ESTJ": ["📊 관리자", "🛠️ 엔지니어", "🏛️ 행정가"],
    "ESFJ": ["💼 HR 매니저", "🍳 요리사", "🏥 간호조무사"],
    "ISTP": ["🔧 기술자", "✈️ 파일럿", "🏍️ 모험가"],
    "ISFP": ["🎨 디자이너", "🎶 음악가", "🌿 플로리스트"],
    "ESTP": ["💸 세일즈맨", "⚽ 운동선수", "🎤 MC"],
    "ESFP": ["🎭 배우", "🎉 이벤트 플래너", "🌍 여행 가이드"],
}

# ✅ 결과 출력
if user_mbti:
    st.markdown(
        f"""
        <h2 style="text-align:center; color:#FF69B4;">
            ✨ {user_mbti} 유형에게 어울리는 직업 추천 ✨
        </h2>
        """,
        unsafe_allow_html=True
    )

    recommendations = job_recommendations.get(user_mbti, ["❌ 추천 데이터 없음"])
    
    for job in recommendations:
        st.markdown(
            f"""
            <div style="background-color:#F9F7FE; padding:15px; 
                        border-radius:15px; margin:10px 0; 
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                <h4 style="margin:0;">{job}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

# ✅ 푸터
st.markdown(
    """
    <br>
    <hr>
    <p style="text-align:center; color:gray; font-size:14px;">
        🌟 Made with ❤️ using Streamlit 🌟
    </p>
    """,
    unsafe_allow_html=True
)
