import streamlit as st
import base64
import json
import firebase_admin
from firebase_admin import credentials, db
import requests

# Hugging Face Zephyr-7b-beta Inference API 연동 함수 (한글 프롬프트 실험)
HF_API_URL = "https://api-inference.huggingface.co/models/google/gemma-2b-it"
HF_HEADERS = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}

# 캐릭터별 프롬프트 (한글 간결 버전 권장, 장문 X)
CHARACTER_PROMPTS = {
    "엘리자베스 베넷": "당신은 오만과 편견의 엘리자베스 베넷입니다. 재치 있고, 자신의 생각을 분명하게 말합니다. 예의는 지키지만 솔직한 대화를 좋아합니다.",
    "데미안": "당신은 헤르만 헤세의 데미안입니다. 철학적이고 상징적인 대화와, 자아, 내면, 성장에 대해 이야기합니다.",
    "앤 셜리": "당신은 빨간머리 앤의 앤 셜리입니다. 상상력 풍부하고 감정 표현이 자유롭습니다. 밝고 긍정적으로 이야기합니다.",
    "어린 왕자": "당신은 어린 왕자입니다. 순수하고 따뜻한 말투, 짧고 시적인 문장을 사용합니다. 세상의 본질, 소중한 것에 대해 말합니다.",
    "도로시": "당신은 오즈의 마법사의 도로시입니다. 용기, 우정, 꿈과 희망을 이야기하며, 밝고 실용적으로 조언합니다."
}

def zephyr_reply(character, user_input, max_length=80):
    system_prompt = CHARACTER_PROMPTS.get(character, "")
    prompt = f"{system_prompt}\n사용자: {user_input}\n{character}:"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_length,
            "do_sample": True,
            "top_p": 0.95,
            "temperature": 0.8
        }
    }
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            # Zephyr는 {"generated_text": "..."} 형태가 아니라 {"generated_text": "..."} 또는 {"generated_text": "...", ...}로 올 수 있음
            if isinstance(result, dict) and "generated_text" in result:
                answer = result["generated_text"].split(f"{character}:")[-1].strip()
                return answer[:180]
            elif isinstance(result, list) and "generated_text" in result[0]:
                answer = result[0]["generated_text"].split(f"{character}:")[-1].strip()
                return answer[:180]
            else:
                # 텍스트 필드가 다를 수 있음
                return "[AI 응답 오류] 결과 형식이 예상과 다릅니다."
        elif response.status_code == 503:
            return "[대기열] 모델이 로딩 중입니다. 잠시 후 다시 시도해 주세요."
        else:
            return f"[API 오류] {response.status_code}: {response.text}"
    except Exception as e:
        return f"[네트워크 오류] {e}"

# ====== Firebase Admin 초기화 (Secrets에서 base64 인코딩 JSON 불러오기) ======
if not firebase_admin._apps:
    encoded_cred = st.secrets["FIREBASE_CREDENTIALS_B64"]
    decoded_json = base64.b64decode(encoded_cred).decode()
    cred_dict = json.loads(decoded_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://login-802ba-default-rtdb.firebaseio.com'
    })

API_KEY = "AIzaSyDOTRNLOMC2iJ-rpa9ADMsM0ZHsZF-FqYE"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"

def firebase_login(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(FIREBASE_SIGNIN_URL, json=payload)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(res.json().get('error', {}).get('message', '로그인 실패'))

def firebase_signup(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(FIREBASE_SIGNUP_URL, json=payload)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(res.json().get('error', {}).get('message', '회원가입 실패'))

# ===== Streamlit UI 시작 =====
st.set_page_config(page_title="SEMIBOT 문학 챗봇", layout="centered")
st.title("📚 SEMIBOT 문학 챗봇")
st.write("API KEY 길이:", len(st.secrets['HF_API_KEY']))
st.write("API KEY 앞 8자리:", st.secrets['HF_API_KEY'][:8])
# ----------------- [로그인/회원가입] -----------------
if 'user' not in st.session_state:
    menu = st.sidebar.selectbox('메뉴 선택', ['로그인', '회원가입'])

    if menu == '로그인':
        email = st.text_input('이메일')
        password = st.text_input('비밀번호', type='password')
        login_btn = st.button('로그인')
        if login_btn:
            if not email or not password:
                st.error('이메일과 비밀번호를 입력하세요.')
            else:
                try:
                    user = firebase_login(email, password)
                    st.session_state['user'] = user
                    ref = db.reference(f"users/{user['localId']}")
                    profile = ref.get()
                    if profile and "nickname" in profile:
                        st.session_state['nickname'] = profile["nickname"]
                    else:
                        st.session_state['nickname'] = email
                    st.rerun()
                except Exception as e:
                    st.error(f"로그인 실패: {e}")

    elif menu == '회원가입':
        email = st.text_input('이메일')
        password = st.text_input('비밀번호', type='password')
        nickname = st.text_input('닉네임')
        signup_btn = st.button('회원가입')
        if signup_btn:
            if not email or not password or not nickname:
                st.error('모든 항목을 입력해야 합니다.')
            elif len(password) < 6:
                st.error('비밀번호는 6자 이상이어야 합니다.')
            else:
                try:
                    user = firebase_signup(email, password)
                    ref = db.reference(f"users/{user['localId']}")
                    ref.set({"nickname": nickname, "email": email})
                    st.success('회원가입 성공! 로그인 해주세요.')
                except Exception as e:
                    st.error(f"회원가입 실패: {e}")

    st.info("로그인 또는 회원가입을 해주세요.")

# ----------------- [메인 서비스] -----------------
else:
    user_email = st.session_state['user']['email']
    nickname = st.session_state.get('nickname', user_email)
    st.sidebar.success(f"{nickname}님, 환영합니다!")

    page_list = ["홈", "독서성향테스트", "챗봇", "마이페이지", "마켓"]
    if 'page' not in st.session_state:
        st.session_state['page'] = "홈"

    page = st.sidebar.selectbox(
        "이동", page_list,
        index=page_list.index(st.session_state['page']),
        key="page_selectbox"
    )
    if page != st.session_state['page']:
        st.session_state['page'] = page
        st.rerun()
    else:
        page = st.session_state['page']

    # ----------------- [홈] -----------------
    if page == "홈":
        st.header("홈")
        st.markdown("여기는 SEMIBOT의 홈입니다. 기능 버튼을 눌러보세요!")

    # ----------------- [독서성향테스트] -----------------
    elif page == "독서성향테스트":
        st.header("📖 독서 성향 테스트")
        st.write("아래 5문항을 모두 답해주세요.")

        q1 = st.radio("1. 선호하는 장르는 무엇인가요?", [
            "1. 고전/로맨스",
            "2. 자아성찰/철학/심리",
            "3. 성장/가족/우정",
            "4. 철학/우화/판타지",
            "5. 모험/판타지"
        ])
        q2 = st.radio("2. 당신이 가장 중요하게 생각하는 삶의 가치는 무엇인가요?", [
            "1. 자신의 신념과 독립성",
            "2. 내면의 성장과 자기 발견",
            "3. 긍정적이고 낙천적인 태도",
            "4. 순수함과 진정성",
            "5. 용기와 우정"
        ])
        q3 = st.radio("3. 자신과 가장 닮았다고 생각되는 동물은 무엇인가요?", [
            "1. 독립적이고 예리한 고양이",
            "2. 신비롭고 똑똑한 부엉이",
            "3. 에너지 넘치고 호기심 많은 다람쥐",
            "4. 순수하고 생각이 깊은 양",
            "5. 용감하고 다정한 골든 리트리버"
        ])
        q4 = st.radio("4. 짝사랑하는 사람이 생겼다! 당신이 가장 먼저 할 생각은 무엇인가요?", [
            "1. 그럴 리가 없어! 일단 부정해보기",
            "2. 그 애는 왠지 나와 비슷한 것 같아.. 어딘지 자신과 닮은 것 같다고 생각하기",
            "3. 세상이 아름다워~ 지금의 설렘을 맘껏 즐기기",
            "4. 행복할 수 있도록 내가 지켜줘야겠어! 순수하고 아끼는 마음으로 짝사랑을 시작하기",
            "5. 새로운 모험의 시작! 짝사랑을 새로운 여정으로 생각하기"
        ])
        q5 = st.radio("5. 혼자만의 독서 시간을 가지게 된 당신! 당신의 독서 방법은 무엇인가요?", [
            "1. 등장인물에 이입해서 빠르게 속독하기",
            "2. 책 내용을 분석하며 독후감 적기",
            "3. 자신만의 상상 더하며 읽기",
            "4. 책이 주는 교훈을 생각하며 천천히 문장을 곱씹어보기",
            "5. 다양한 장르와 작가를 탐험하며 읽기"
        ])

        if st.button("테스트 결과 보기"):
            answers = [
                int(q1.split('.')[0]),
                int(q2.split('.')[0]),
                int(q3.split('.')[0]),
                int(q4.split('.')[0]),
                int(q5.split('.')[0]),
            ]
            from collections import Counter
            count = Counter(answers)
            max_count = max(count.values())
            result_nums = [num for num, cnt in count.items() if cnt == max_count]

            character_map = {
                1: "엘리자베스 베넷",
                2: "데미안",
                3: "앤 셜리",
                4: "어린 왕자",
                5: "도로시"
            }
            results = {
                1: "이성형 독서 (오만과 편견 - 엘리자베스 베넷)",
                2: "사고형 독서 (데미안 - 데미안)",
                3: "상상형 독서 (빨간머리 앤 - 앤 셜리)",
                4: "감성형 독서 (어린 왕자 - 어린 왕자)",
                5: "탐험형 독서 (오즈의 마법사 - 도로시)"
            }

            st.success("테스트 결과!")
            for num in result_nums:
                st.markdown(f"- **{results[num]}**")
                if st.button(f"{character_map[num]} 챗봇으로 이동하기", key=f"go_chatbot_{num}"):
                    st.session_state['selected_character'] = character_map[num]
                    st.session_state['page'] = "챗봇"
                    st.rerun()

            st.markdown("---")
            st.markdown("### 전체 추천 캐릭터")
            st.markdown("""
            1. 오만과 편견 - 엘리자베스 베넷  
            2. 데미안 - 데미안  
            3. 빨간머리 앤 - 앤 셜리  
            4. 어린 왕자 - 어린 왕자  
            5. 오즈의 마법사 - 도로시
            """)

    # ----------------- [챗봇] -----------------
    elif page == "챗봇":
        character_list = ["엘리자베스 베넷", "데미안", "앤 셜리", "어린 왕자", "도로시"]

        if 'selected_character' not in st.session_state or st.session_state['selected_character'] not in character_list:
            st.session_state['selected_character'] = character_list[0]

        selected_character = st.selectbox(
            "챗봇 캐릭터 선택",
            character_list,
            index=character_list.index(st.session_state['selected_character']),
            key="character_select"
        )
        if selected_character != st.session_state['selected_character']:
            st.session_state['selected_character'] = selected_character
            st.rerun()
        else:
            selected_character = st.session_state['selected_character']

        uid = st.session_state['user']['localId']
        ref = db.reference(f"users/{uid}/chats/{selected_character}")
        prev_chats = ref.get() or []

        st.markdown(f"#### [{selected_character} 챗봇] 이전 대화")
        if prev_chats:
            for msg in prev_chats:
                st.markdown(f"- {msg}")
        else:
            st.info("아직 대화 내역이 없습니다. 첫 메시지를 남겨보세요!")

        msg = st.text_input("메시지 입력(Enter로 전송)", key="chat_input")
        col1, col2 = st.columns([1, 1])
        with col1:
            send_btn = st.button("전송")
        with col2:
            delete_btn = st.button("대화 전체 삭제")

        if send_btn:
            if msg.strip() != "":
                new_chats = prev_chats + [f"나: {msg}"]
                with st.spinner("AI 답변 생성 중... (최대 1분 소요)"):
                    ai_reply = zephyr_reply(selected_character, msg)
                new_chats.append(f"{selected_character}: {ai_reply}")
                ref.set(new_chats)
                st.rerun()
        if delete_btn:
            ref.delete()
            st.rerun()

    # ----------------- [마이페이지] -----------------
    elif page == "마이페이지":
        st.header("📊 마이페이지")
        st.markdown(f"**닉네임:** {nickname}")
        st.markdown(f"**이메일:** {user_email}")
        st.markdown("포인트, 문해력 레벨, 테마, 리딩 목표 등 표시 (예시)")

    # ----------------- [마켓] -----------------
    elif page == "마켓":
        st.header("🎁 SEMIBOT 마켓")
        st.markdown("""
         - 캐릭터별 명대사 조언 타로
         - 도서/굿즈 연계 상품 판매
        """)

    # ----------------- [로그아웃] -----------------
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()





