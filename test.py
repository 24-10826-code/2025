# app.py
import math
import random
import io
from datetime import datetime, timedelta, time

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -------------------- App Setup --------------------
st.set_page_config(
    page_title="Study&Body",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Theme & CSS --------------------
PASTEL_BG = "#F9FAFB"
PRIMARY = "#7C3AED"       # violet-600
ACCENT = "#22C55E"        # green-500
WARN = "#F59E0B"          # amber-500
MUTED = "#94A3B8"         # slate-400
CARD_BG = "#FFFFFF"

st.markdown(
    f"""
    <style>
    @keyframes float {{
      0% {{ transform: translateY(0px); }}
      50% {{ transform: translateY(-6px); }}
      100% {{ transform: translateY(0px); }}
    }}
    .app-bg {{
      background: linear-gradient(180deg,{PASTEL_BG}, #fff);
    }}
    .card {{
      background:{CARD_BG};
      border:1px solid rgba(0,0,0,0.06);
      border-radius:20px;
      padding:18px 18px;
      box-shadow:0 6px 20px rgba(0,0,0,0.05);
    }}
    .chip {{
      display:inline-block;
      padding:4px 10px;
      border-radius:999px;
      background:rgba(124,58,237,0.08);
      color:{PRIMARY};
      font-weight:600;
      font-size:12px;
      border:1px solid rgba(124,58,237,0.2);
    }}
    .character {{
      border-radius:22px;
      padding:14px 16px;
      background:linear-gradient(135deg, rgba(124,58,237,0.09), rgba(34,197,94,0.10));
      border:1px solid rgba(0,0,0,0.06);
      box-shadow:0 8px 20px rgba(124,58,237,0.12);
      animation: float 5s ease-in-out infinite;
    }}
    .speech {{
      background:white;
      border-radius:16px;
      padding:10px 12px;
      border:1px solid rgba(0,0,0,0.06);
      display:inline-block;
      box-shadow:0 4px 14px rgba(0,0,0,0.05);
    }}
    .title {{
      font-size:28px; font-weight:800; letter-spacing:-0.4px;
    }}
    .subtitle {{
      color:{MUTED}; font-size:14px;
    }}
    .progress-label {{
      font-weight:700; color:#0f172a;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Session State --------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["과목", "주제", "예정(분)", "완료", "날짜"])

if "guide" not in st.session_state:
    st.session_state.guide = "뉴런"

if "chronotype" not in st.session_state:
    st.session_state.chronotype = "일반형"

# -------------------- Character System --------------------
CHARACTERS = {
    "뉴런": {
        "emoji": "🧠",
        "color": PRIMARY,
        "tag": "기억·집중 가이드",
        "line": [
            "시냅스를 튼튼하게 하려면 복습 주기를 지켜줘! 🔁",
            "25분 몰입 + 5분 휴식, 포모도로로 시냅스 폭발! 🍅",
            "수면이 곧 기억이다. 오늘 7시간은 약속! 😴",
        ],
    },
    "ATP 몬스터": {
        "emoji": "🔋",
        "color": ACCENT,
        "tag": "에너지 매니저",
        "line": [
            "포도당 저하 감지! 과일 한 조각이면 충분해 🍎",
            "과도한 카페인은 에너지 대출이야 ☕️ 적당히!",
            "스트레칭 60초면 미토콘드리아가 깨어난다 🧬",
        ],
    },
    "DNA 요정": {
        "emoji": "🧚‍♀️",
        "color": WARN,
        "tag": "리듬 & 회복",
        "line": [
            "서서히, 규칙적으로. 리듬이 유전자 발현을 돕지 ✨",
            "빛 노출 10분! 생체시계 리셋 완료 🌞",
            "단백질 간식은 회복의 핵심이야 🍗",
        ],
    },
}

def character_bubble(name: str, msg: str = None):
    c = CHARACTERS[name]
    pick = msg or random.choice(c["line"])
    st.markdown(
        f"""
        <div class="character">
          <div style="display:flex;gap:12px;align-items:center;">
            <div style="font-size:36px">{c['emoji']}</div>
            <div>
              <div style="font-weight:800;color:{c['color']};font-size:16px;">{name}</div>
              <div class="subtitle">{c['tag']}</div>
              <div class="speech" style="margin-top:8px;">{pick}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------- Sidebar --------------------
st.sidebar.title("Study&Body")
st.sidebar.caption("뇌와 몸을 동시에 챙기는 스마트 도우미 ✨")

st.sidebar.markdown("#### 가이드 캐릭터")
guide = st.sidebar.radio("선택", list(CHARACTERS.keys()), index=list(CHARACTERS.keys()).index(st.session_state.guide))
st.session_state.guide = guide
character_bubble(guide)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 네 리듬은?")
chronotype = st.sidebar.selectbox("크로노타입", ["아침형", "저녁형", "일반형"], index=["아침형","저녁형","일반형"].index(st.session_state.chronotype))
st.session_state.chronotype = chronotype
wake_time = st.sidebar.time_input("기상 시간", value=time(7, 0))
sleep_hours = st.sidebar.slider("수면 시간(시간)", 4.0, 10.0, 7.0, 0.5)
water_cups = st.sidebar.slider("물 섭취(컵/일)", 0, 12, 5)
caffeine = st.sidebar.slider("카페인(잔/일)", 0, 6, 1)

st.sidebar.markdown("---")
page = st.sidebar.radio("탐색", ["대시보드", "학습 플래너", "리듬 알림", "시너지 팁", "리포트 & 내보내기"])

# -------------------- Helper: Brain Energy Index --------------------
def brain_energy_index(sleep_hours: float, water: int, caffeine: int, study_minutes_today: int):
    # 간단한 휴리스틱 모델 (0~100)
    score = 50
    # 수면
    if 7 <= sleep_hours <= 9:
        score += 20
    else:
        score -= 10 * abs(8 - sleep_hours) / 2
    # 수분
    if water >= 6:
        score += 10
    elif water <= 2:
        score -= 8
    # 카페인
    if caffeine == 0:
        score += 4
    elif caffeine <= 2:
        score += 2
    else:
        score -= 6 * (caffeine - 2)
    # 공부 시간 (과도/부족 보정)
    if study_minutes_today < 30:
        score -= 5
    elif study_minutes_today > 360:
        score -= 5
    else:
        score += min(12, study_minutes_today / 30 * 2)
    return max(0, min(100, round(score)))

def energy_curve(chronotype: str, wake: time):
    # 24시간 에너지 곡선 (0~1)
    xs = np.arange(0, 24, 0.5)
    wake_hour = wake.hour + wake.minute/60
    peak_shift = {"아침형": -1.0, "일반형": 0.0, "저녁형": 2.0}[chronotype]
    base_peak = wake_hour + 3.5 + peak_shift
    second_peak = base_peak + 7.5
    curve = 0.55 + 0.3*np.exp(-0.5*((xs-base_peak)/1.6)**2) + 0.2*np.exp(-0.5*((xs-second_peak)/2.2)**2)
    curve = np.clip(curve, 0, 1)
    return xs, curve

def suggested_blocks(xs, curve, n=3):
    # 상위 n개 집중 블록 (30분 단위)
    top_idx = np.argsort(curve)[-n:]
    slots = []
    for i in sorted(top_idx):
        h = xs[i]
        hh = int(h)
        mm = int((h - hh) * 60)
        start = time(hh, mm)
        end_dt = (datetime.combine(datetime.today(), start) + timedelta(minutes=60)).time()
        slots.append((start, end_dt, round(curve[i],2)))
    return slots

# -------------------- Header --------------------
st.markdown(
    f"""
    <div class="title">Study&Body <span class="chip">학습 × 리듬 × 귀여움</span></div>
    <div class="subtitle">공부 플래너와 생체리듬 알림을 한 곳에. 뉴런·ATP·DNA 캐릭터가 동행합니다.</div>
    """,
    unsafe_allow_html=True,
)
st.write("")

# -------------------- Pages --------------------
def page_dashboard():
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("### 📊 오늘 한눈에 보기")
        today = pd.Timestamp.today().date().isoformat()
        df = st.session_state.tasks
        studied_today = df[(df["날짜"] == today) & (df["완료"] == True)]["예정(분)"].sum() if not df.empty else 0
        bei = brain_energy_index(sleep_hours, water_cups, caffeine, int(studied_today))

        # gauge-like chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bei,
            number={'suffix': " / 100"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': PRIMARY},
                'steps': [
                    {'range': [0, 40], 'color': "#fee2e2"},
                    {'range': [40, 70], 'color': "#fef3c7"},
                    {'range': [70, 100], 'color': "#dcfce7"},
                ],
                'threshold': {'line': {'color': ACCENT, 'width': 4}, 'thickness': 0.75, 'value': 70}
            }
        ))
        fig.update_layout(height=250, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f"""
            <div class="card">
                <div class="progress-label">오늘 공부 시간</div>
                <div style="height:10px;background:#e5e7eb;border-radius:999px;overflow:hidden;margin-top:8px;">
                    <div style="width:{min(100, studied_today/240*100)}%;height:100%;background:{ACCENT};"></div>
                </div>
                <div class="subtitle" style="margin-top:6px;">완료 {int(studied_today)}분 / 목표 240분</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        xs, curve = energy_curve(st.session_state.chronotype, wake_time)
        slots = suggested_blocks(xs, curve, n=3)

        st.markdown("### ⏰ 오늘의 집중 골든타임")
        colA, colB, colC = st.columns(3)
        for (start, end, power), col in zip(slots, [colA, colB, colC]):
            with col:
                st.markdown(
                    f"""
                    <div class="card">
                        <div style="font-size:22px;">⚡ {start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}</div>
                        <div class="subtitle">예상 집중도 {int(power*100)}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with right:
        st.markdown("### 🧩 캐릭터 피드")
        character_bubble(st.session_state.guide)
        if bei < 60:
            character_bubble("ATP 몬스터", "에너지 저하 경보! 물을 1컵 마시고 60초 스트레칭 어때? 💧🧎")
        else:
            character_bubble("뉴런", "지금 장기기억으로 전환할 찬스! 5문제만 복습하자 🔁")

def page_planner():
    st.markdown("### 🗂️ 학습 플래너")
    with st.container():
        c1, c2, c3, c4 = st.columns([1, 1.2, 0.8, 0.8])
        subj = c1.selectbox("과목", ["화학", "생명과학", "약학", "수학", "영어", "기타"])
        topic = c2.text_input("주제/단원", placeholder="예: 산화·환원, 유전자 발현 등")
        minutes = c3.number_input("예정(분)", 10, 300, 40, 10)
        date_str = c4.date_input("날짜").isoformat()

        add = st.button("➕ 추가", use_container_width=False)
        if add and topic.strip():
            st.session_state.tasks = pd.concat(
                [
                    st.session_state.tasks,
                    pd.DataFrame([{"과목": subj, "주제": topic.strip(), "예정(분)": int(minutes), "완료": False, "날짜": date_str}])
                ],
                ignore_index=True
            )
            st.success("계획이 추가됐어요! ✅")

    st.write("")
    df = st.session_state.tasks
    if df.empty:
        st.info("아직 계획이 없어요. 위에서 항목을 추가해보세요!")
        return

    # Editable planner
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        column_config={
            "완료": st.column_config.CheckboxColumn("완료"),
            "예정(분)": st.column_config.NumberColumn("예정(분)", min_value=0, step=5),
        },
    )
    st.session_state.tasks = edited

    # Summary
    today = pd.Timestamp.today().date().isoformat()
    done_mins = edited[(edited["날짜"] == today) & (edited["완료"] == True)]["예정(분)"].sum()
    total_mins = edited[edited["날짜"] == today]["예정(분)"].sum()
    pct = 0 if total_mins == 0 else int(done_mins / total_mins * 100)
    st.markdown(
        f"""
        <div class="card">
          <div style="display:flex;gap:16px;align-items:center;">
            <div style="font-size:28px;">📈</div>
            <div>
              <div class="progress-label">오늘 진행률 {pct}%</div>
              <div class="subtitle">완료 {int(done_mins)}분 / 전체 {int(total_mins)}분</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def page_rhythm():
    st.markdown("### ⏱️ 리듬 알림 & 집중 타이머")
    xs, curve = energy_curve(st.session_state.chronotype, wake_time)

    # chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=curve, mode="lines", name="에너지"))
    fig.update_layout(
        height=260,
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis_title="시각(시)",
        yaxis_title="예상 에너지(정규화)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 🔔 추천 알림 문구 (예시)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("• 물 1컵: 집중 전 10분 알림 — “수분 보충으로 시냅스 전도 업! 💧”")
        st.write("• 눈 휴식: 25분 집중 후 5분 — “20-20-20 규칙, 먼 곳 보기 👀”")
        st.write("• 간식: 저혈당 방지 — “과일 한 조각으로 ATP 충전 🔋”")
    with col2:
        st.write("• 스트레칭: 매 시간 60초 — “근육 펌프 → 뇌혈류 ↑ 🧎”")
        st.write("• 카페인 컷오프: 잠자기 8시간 전 — “수면 방해 방지 ☕️🚫”")
        st.write("• 가벼운 산책: 오후 슬럼프 — “빛+움직임 → 각성 ↑ 🚶”")

    st.markdown("#### ⏳ 포모도로 타이머(로컬)")
    st.caption("Streamlit은 백그라운드 타이머 지속이 제한적이라 탭을 유지해 주세요. 세션 단위로 작동합니다.")
    work = st.number_input("집중(분)", 10, 60, 25, 5)
    rest = st.number_input("휴식(분)", 3, 20, 5, 1)
    rounds = st.number_input("라운드", 1, 12, 4, 1)
    if st.button("타이머 시작/리셋"):
        st.session_state.pomo = {"work": work, "rest": rest, "rounds": rounds, "start": datetime.now()}

    if "pomo" in st.session_state:
        elapsed = (datetime.now() - st.session_state.pomo["start"]).total_seconds()
        cycle = (st.session_state.pomo["work"] + st.session_state.pomo["rest"]) * 60
        round_idx = int(elapsed // cycle) + 1
        within = elapsed % cycle
        phase = "집중" if within < st.session_state.pomo["work"]*60 else "휴식"
        remain = (st.session_state.pomo["work"]*60 - within) if phase=="집중" else (cycle - within)
        remain = max(0, int(remain))
        m, s = divmod(remain, 60)

        st.markdown(
            f"""
            <div class="card">
              <div style="font-size:20px;">현재: <b>{phase}</b> | 라운드 {min(round_idx, st.session_state.pomo['rounds'])}/{st.session_state.pomo['rounds']}</div>
              <div style="margin-top:6px;" class="subtitle">남은시간 {m:02d}:{s:02d}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def synergy_tip(subject: str):
    tips = {
        "화학": [
            "산염기 단원 공부 전 물 1컵 → 집중 유지에 도움 💧",
            "모형 그리기(루이스/구조식)를 말로 설명하면 장기기억 전환 ↑ 🗣️",
            "카페인 과다 금지 — 불안감 ↑로 계산 실수 ↑ ☕️⚠️",
        ],
        "생명과학": [
            "광합성·세포호흡은 단계 플로차트로 정리하면 효과적 🔁",
            "30분 공부 후 3분 산책 → 각성도 올리고 기억 고정 🚶",
            "단백질 간식(계란/요거트) → 포만감과 주의집중 유지 🍳",
        ],
        "약학": [
            "약물동태(PK) 그래프는 축과 단위를 먼저 고정 → 혼동 방지 📉",
            "약물 상호작용은 사례 위주로 카드화해 반복 복습 🃏",
            "카페인 컷오프 시간을 확보(취침 8h 전) → 기억 통합에 필수 😴",
        ],
        "수학": [
            "예제→유사문제→응용 순서로 난이도 사다리 만들기 🪜",
            "오답노트는 ‘왜’에 집중. 규칙 추출이 핵심 🧠",
            "문제 풀이 중 말하기(생각 크게 말하기)로 메타인지 강화 🗣️",
        ],
        "영어": [
            "섀도잉 10분 + 단어 10개. 듣기와 어휘의 동시 강화 🎧",
            "수면 전 5분 단어 복습 → 수면 중 기억 강화 효과 ✨",
            "짧은 문장으로 자기표현 — 문법이 살아난다 ✍️",
        ],
        "기타": [
            "작은 목표 쪼개기 → 완료 도파민을 자주 얻자 ✅",
            "휴대폰 방해 최소화: 알림 끄기/집중 모드 🔕",
            "의자에서 60초 스트레칭 → 뇌혈류 개선 🧎",
        ],
    }
    return tips.get(subject, tips["기타"])

def page_synergy():
    st.markdown("### 🧪 학습 × 건강 시너지 팁")
    df = st.session_state.tasks
    today = pd.Timestamp.today().date().isoformat()
    today_subj = df[df["날짜"] == today]["과목"].unique().tolist() if not df.empty else []
    pick_subj = st.selectbox("과목 선택", ["화학", "생명과학", "약학", "수학", "영어", "기타"], index=0 if not today_subj else  ["화학","생명과학","약학","수학","영어","기타"].index(today_subj[0]) if today_subj[0] in ["화학","생명과학","약학","수학","영어","기타"] else 0)

    colA, colB = st.columns([1, 1])
    with colA:
        for tip in synergy_tip(pick_subj):
            st.markdown(f"- {tip}")
    with colB:
        # character comment
        if pick_subj in ["화학", "생명과학", "약학"]:
            who = "뉴런" if pick_subj != "약학" else "DNA 요정"
        else:
            who = "ATP 몬스터"
        character_bubble(who)

    st.markdown("---")
    st.markdown("#### 🎴 빠른 플래시카드 (랜덤 5)")
    cards = {
        "화학": [
            ("산화수란?", "원자가 전자를 잃거나 얻을 때의 가상 전하수"),
            ("르샤틀리에 원리", "평형을 방해하면 이를 상쇄하는 방향으로 이동"),
            ("엔탈피(ΔH)", "압력 일정한 과정에서 방출/흡수되는 열에너지"),
            ("Ka와 pKa 관계", "pKa = -log(Ka), 작을수록 강산"),
            ("전기음성도", "공유전자쌍을 끌어당기는 능력"),
        ],
        "생명과학": [
            ("세포호흡 장소", "해당과정-세포질, TCA/ETC-미토콘드리아"),
            ("전사와 번역", "DNA→mRNA(전사), mRNA→단백질(번역)"),
            ("ATP 의미", "에너지 통화, 인산 결합의 가수분해로 에너지 방출"),
            ("삼투", "농도 차이에 따른 수분의 이동"),
            ("시냅스 가소성", "사용에 따라 연결 강도가 변함"),
        ],
        "약학": [
            ("약물동태 PK", "흡수-분포-대사-배설(ADME)"),
            ("반감기 의미", "농도가 절반이 되는 시간"),
            ("효능 vs 효력", "효능: 최대효과, 효력: EC50/효과강도"),
            ("치료지수 TI", "LD50/ED50, 클수록 안전"),
            ("CYP450 역할", "약물 대사의 주요 효소계"),
        ],
    }
    bundle = cards.get(pick_subj, random.choice(list(cards.values())))
    sample = random.sample(bundle, k=min(5, len(bundle)))
    with st.expander("카드 펼치기/접기"):
        for q, a in sample:
            with st.container():
                st.markdown(f"**Q. {q}**")
                if st.toggle("정답 보기", key=f"card-{q}"):
                    st.success(a)

def page_report():
    st.markdown("### 📘 리포트 & 내보내기")
    df = st.session_state.tasks.copy()
    if df.empty:
        st.info("데이터가 없어요. 학습 계획을 추가해보세요!")
        return

    today = pd.Timestamp.today().date().isoformat()
    studied = df[(df["날짜"] == today) & (df["완료"] == True)]["예정(분)"].sum()
    bei = brain_energy_index(sleep_hours, water_cups, caffeine, int(studied))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("오늘 공부(분)", int(studied))
    with col2:
        st.metric("Brain Energy Index", bei)
    with col3:
        st.metric("수면(시간)", sleep_hours)

    # Heatmap-like subject summary
    summary = df.groupby(["날짜", "과목"])["예정(분)"].sum().unstack(fill_value=0)
    st.markdown("#### 📅 과목별 학습 분포")
    st.dataframe(summary, use_container_width=True)

    # Export
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ 플래너 CSV 다운로드", csv, file_name="studybody_planner.csv", mime="text/csv")

    # Character closing
    if bei >= 70:
        character_bubble("뉴런", "데이터가 말해! 오늘은 기억 고정하기 좋은 날이야 🔒")
    else:
        character_bubble("DNA 요정", "리듬 조정이 필요해. 빛 노출 & 물 1컵부터 시작해봐 🌞💧")

# -------------------- Router --------------------
if page == "대시보드":
    page_dashboard()
elif page == "학습 플래너":
    page_planner()
elif page == "리듬 알림":
    page_rhythm()
elif page == "시너지 팁":
    page_synergy()
else:
    page_report()

