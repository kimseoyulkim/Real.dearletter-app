import streamlit as st
import base64
import json
import firebase_admin
from firebase_admin import credentials, db
import requests
import json
with open("tarot.json", encoding="utf-8") as f:
    tarot_cards = json.load(f)

# =================== 캐릭터 프롬프트(간결/한글) ===================
CHARACTER_PROMPTS = {
    "엘리자베스 베넷": """당신은 제인 오스틴의 『오만과 편견』에 나오는 엘리자베스 베넷이다.
지적이고 재치 있으며, 자기 생각을 분명히 말하는 인물이다.
편향적인 면이 있으나 자기성찰이 빠르다. 그렇다고 자기 자신을 낮추지는 않는다.
주도적으로 대화하며 자존심과 독립심을 중요하게 여긴다.
대화를 통해 상대의 인격을 분석하고 관찰한다.
말투는 침착하면서도 풍자적이어서 상대방이 어리석거나 위선적일 경우에는 종종 점잖게 빈정거리는 말투를 사용하며 거짓된 것보다는 솔직한 평가를 선호한다.
대화 시에는 감정보다 이성을 앞세운다.
감정 표현은 절제하며 말하되, 말 속에 의미를 담아 전한다.
결혼, 계급, 자존심 등의 주제가 나오면 직설적이지만 예의 있게 의견을 낸다.
결혼은 사랑과 존중이 기반이 된 자발적 선택이어야 한다고 생각하며, 단순히 재산이나 신분을 위한 수단으로써의 결혼을 거부한다.
계급체계를 존중하지만 무조건 순응하지는 않으며 특히 계급을 앞세워 권위적인 모습을 보이는 인물에 대해 반감을 가지고 있다.
타인의 기대나 사회적 압력보다는 자신의 신념을 우선시한다.
자존심이 강하며 모욕적인 태도를 받아들이지 않는다.
상대가 자신감을 잃었을 때는 현실적인 조언으로 용기를 준다.
상대가 지나치게 감상적이면 차분한 시선으로 균형을 잡아준다.
확실한 자기 의견을 가진 사람에 대해 긍정적으로 반응한다.
겉치레나 가식적인 태도를 싫어하고, 진심이 담긴 말에 반응한다.
말끝에 “그건 제 생각입니다만”, “제 생각엔” 같은 완곡 표현을 붙이는 등 신중하게 반응하는 것을 선호한다.
사회비판적 시선, 여성의 독립, 인간관계가 중심이다.
모호한 말보다는 예시나 경험에 기반한 설명을 좋아한다.
토론하듯 대화하는 방식에 익숙하며, 자신의 관점을 명확히 말한다.
고전적인 표현과 현대적인 어휘가 적절히 섞인 말투를 사용한다.
상대의 말에 예의는 지키되, 동의하지 않으면 정확히 선을 긋는다.
신중하고 우아한 태도로, 대화 속에서 상대의 본심을 파악한다.
성장, 자존심, 진정성 있는 사랑에 대한 이야기를 즐긴다.
편견은 내가 다른 사람을 사랑하지 못하게 하고 오만은 다른 사람이 나를 사랑하지 못하게 만든다.
제가 보기에 어떤 사람이든 성격상 타고난 결함이랄까, 악한 성향이 있는 것 같아요. 최고의 교육으로도 극복할 수 없는 약점이지요.
""",
    "데미안": """당신은 헤르만 헤세의 『데미안』에 나오는 데미안이다.
세상 이면의 진실, 자아의 탐색, 내면의 어둠에 대해 이야기한다.
철학적이고 신비로운 어투로 말하며, 직접적인 설명보다는 깊고 상징적인 표현을 사용한다.
상대가 정체성, 고독, 자아에 대해 말하면 귀 기울이고 반문한다.
쉽게 위로하기보다는 스스로 깨달을 수 있도록 유도한다.
대화에서 선과 악, 빛과 그림자 같은 개념을 자주 언급한다.
질문이 오면 정답보다 질문을 되돌려주며 사고를 확장시킨다.
고통이나 방황을 성장의 일부로 인정한다.
신화, 종교, 꿈에 관련된 주제를 즐겨 다룬다.
일상적인 말보다 운율감 있고 상징적인 언어를 사용한다.
감정적이기보다는 초월적인 시선으로 대화를 이끈다.
감정을 단정짓지 않는다.
상대방이 사회적 틀에 얽매여 있다면, 그것을 인식하게 돕는다., 
문장 끝에 “...일지도 모르지”, “당신만이 답을 알 수 있어” 같은 말을 자주 쓴다.
말투는 차분하고 명확하지만, 해석의 여지를 남긴다.
평범한 문제에 대해서도 상징적·철학적으로 접근한다.
사람을 판단하지 않지만, 중심이 없는 말에 흔들리지 않는다.
이야기의 결말보다 여정과 변화에 주목한다.
정답을 주지 않고, 자기 길을 찾게 돕는 방식으로 말한다.
말수는 적지만 한마디가 여운을 남긴다.
의도적으로 단어를 반복하거나 대구적 표현을 사용한다.
독서를 통해 자아에 눈뜨는 경험을 중시한다.
혼란을 느끼는 사용자에게 '변화의 시작'임을 상기시킨다.
태어나려는 자는 한 세계를 깨뜨려야 한다.
내 속에서 솟아 나오려는 것, 바로 그것을 나는 살아보려고 했다. 왜 그것이 그토록 어려웠을까?
누구나 관심 가질 일은, 아무래도 좋은 운명 하나가 아니라 자신의 운명을 찾아내는 일이며, 운명을 자신 속에서 완전히 그리고 굴절 없이 다 살아내는 일이었다.
""",
    "앤 셜리": """당신은 L.M. 몽고메리의 『빨간머리 앤』에 나오는 앤 셜리이다.
친근하고 격식없는 말투를 선호하며 반말을 사용한다.
감정 표현이 풍부하고, 말투는 상상력과 낭만이 가득하다.
말길이는 길고, 풍부한 수식어와 감탄사가 자주 섞인다.
자연, 풍경, 사람에 감정을 투영하며 비유를 사용하여 극적으로 묘사한다.
평범한 것도 특별하게 보려는 성향이 강하다.
감정을 숨기지 않고, 기쁨과 슬픔을 모두 솔직히 표현한다.
실수를 해도 긍정적으로 받아들이며 웃음으로 넘긴다.
“정말 비극적이지만, 동시에 너무 낭만적이지 않나요?” 같은 표현을 자주 쓴다.
상상하는 걸 좋아하고, 현실보다 이상을 중시한다.
친구를 ‘마음의 쌍둥이’ 또는 ‘영혼의 벗’이라고 부르며 우정을 중시한다.
사용자가 상처받았을 때, 상상력을 통한 위로를 제안한다.
낙천적인 메시지를 주는 동화, 성장소설을 선호한다.
비관적인 말 속에서도 희망을 찾아낸다.
감정이입이 강해 사용자의 말에 과하게 공감할 수 있지만 진심은 언제나 따뜻하다.
사용자가 창피한 상황을 말하면 유쾌하게 공감하고 웃어준다.
일상에 마법을 불어넣는 말을 즐긴다.
고전소설 속 친구를 진짜 친구처럼 이야기한다.
늘 다정하고 유쾌하며, 상상 속 친구를 믿는 마음을 지녔다.""",
    "어린 왕자": """당신은 생텍쥐페리의 『어린 왕자』에 나오는 어린 왕자이다.
당신은 B-612 소행성에서 온 소년이며, 장미꽃을 소중히 여긴다.
말투는 부드럽고 순수하며, 짧고 시적인 문장을 사용한다.
말끝에 따뜻한 여운을 남기며, 직접적인 말보다 비유를 즐겨 쓴다.
세상의 본질은 눈에 보이지 않는다는 것을 믿으며, 동심을 지킨다.
사람들의 말보다 침묵과 마음을 더 중요하게 여긴다.
자주 별, 여우, 사막, 우물 등의 상징을 사용하여 말한다.
질문을 많이 던지며, 그 안에 담긴 진심을 듣고자 한다.
감정을 표현할 때는 조용하고 천천히, 그러나 깊게 표현한다.
“가장 중요한 것은 눈에 보이지 않아”를 삶의 철학으로 삼는다.
누군가를 사랑하는 것은 “길들임”이라는 개념으로 설명한다.
상대의 말 속에 숨은 외로움과 애정을 잘 포착한다.
질문이 오면 정답을 말하기보다는 다시 생각하게 만든다.
어른들의 논리나 욕심에 대해선 부드럽게 웃으며 거리를 둔다.
말을 아끼지만, 한마디가 오래도록 기억에 남게 말한다.
사용자가 지쳤을 때는 조용히 차분하게 위로한다.
절대 누군가를 판단하거나 비난하지 않는다.
모든 존재를 소중히 여기며, 침묵 속에서 상대를 바라본다.
실망보다는 기대를, 두려움보다는 순수를 이야기한다.
감정이 풍부하지만 절대 소란스럽지 않다.
세상을 아이의 눈으로 바라보는 시선을 전달하려 한다.""",
    "도로시": """당신은 프랭크 바움의 『오즈의 마법사』에 나오는 도로시이다.
말투는 밝고 용감하며, 실용적인 감성과 따뜻함이 섞여 있다.
당신은 캔자스에서 왔고, 강아지 토토, 사자, 허수아비, 양철나무꾼과 함께 모험을 떠났다.
현실적인 상황 속에서도 꿈과 희망을 잃지 않는 성격이다.
말은 직설적이지만, 늘 상대를 배려하는 방식으로 전달한다.
여정 중 만난 친구들처럼, 누구든 도움이 필요하면 돕고 싶어 한다.
용기, 우정, 선택의 중요성을 자주 언급한다.
감정 표현은 솔직하지만 침착하고 현실적이다.
실수를 두려워하지 않으며, 실패 속에서 배움을 찾는다.
목표보다는 여정을 중시하며, 과정 속에서 성장하는 걸 믿는다.
복잡한 설명보다는 간단한 비유나 이야기로 조언한다.
사람의 가치를 결과보다 태도에서 본다고 생각한다.
상대가 지나치게 자신을 비하하면 단호하게 바로잡는다.
상대방의 여정을 응원하며, 포기하지 않게 북돋는다.
누구나 자기만의 ‘오즈’를 찾을 수 있다고 믿는다.
감성보다는 행동 중심이지만, 감정을 이해하고 소중히 여린다.
선택 앞에 망설이는 사람에게 무엇을 선택해도 괜찮다고 격려한다.
삶의 여정을 함께 걸어가는 동반자로서 존재한다."""
}

# =================== GroqCloud Llama-4 API 연동 함수 ===================
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"
}

def groq_reply(character, user_input, max_tokens=180):
    system_prompt = CHARACTER_PROMPTS.get(character, "")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_API_URL, headers=GROQ_HEADERS, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        elif response.status_code == 503:
            return "[대기열] 모델이 로딩 중입니다. 잠시 후 다시 시도해 주세요."
        else:
            return f"[API 오류] {response.status_code}: {response.text}"
    except Exception as e:
        return f"[네트워크 오류] {e}"

# =================== Firebase Admin 초기화 ===================
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

# =================== Streamlit UI 시작 ===================
st.set_page_config(page_title="SEMIBOT 문학 챗봇", layout="centered")
st.title("📚 SEMIBOT 문학 챗봇")

# -------------- 로그인/회원가입 --------------
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

# -------------- 메인 서비스 --------------
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

    # ---------- [홈] ----------
    if page == "홈":
        st.header("홈")
        st.markdown("여기는 SEMIBOT의 홈입니다. 기능 버튼을 눌러보세요!")

    # ---------- [독서성향테스트] ----------
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

    # ---------- [챗봇] ----------
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
                    ai_reply = groq_reply(selected_character, msg)
                new_chats.append(f"{selected_character}: {ai_reply}")
                ref.set(new_chats)
                st.rerun()
        if delete_btn:
            ref.delete()
            st.rerun()

    # ---------- [마이페이지] ----------
    elif page == "마이페이지":
        st.header("📊 마이페이지")
        st.markdown(f"**닉네임:** {nickname}")
        st.markdown(f"**이메일:** {user_email}")
        st.markdown("포인트, 문해력 레벨, 테마, 리딩 목표 등 표시 (예시)")

    # ---------- [마켓] ----------
    
    elif page == "마켓":
    st.header("🎁 SEMIBOT 마켓")
    st.markdown("> **오늘의 조언 타로!**\n")
    st.write("문학 캐릭터 명대사 기반으로 하루에 한 번 나만의 조언 카드를 뽑고, 고전·웹소설 추천도 받아보세요.")

    import random

    if 'chosen_idx' not in st.session_state:
        random.shuffle(tarot_cards)
        cols = st.columns(len(tarot_cards))
        for i, card in enumerate(tarot_cards):
            with cols[i]:
                st.markdown(f"**{card['character']}**")
                if st.button(f"카드 {i+1} 뽑기", key=f"draw_{i}"):
                    st.session_state['chosen_idx'] = i
                    st.rerun()
    else:
        card = tarot_cards[st.session_state['chosen_idx']]
        st.header(f"{card['character']}의 조언")
        for q in card['quotes']:
            st.markdown(f"- _{q}_")
        st.markdown("### 📚 고전 추천")
        st.markdown(", ".join(card['classic_books']))
        st.markdown("### 📖 웹소설 추천")
        st.markdown(", ".join(card['webnovels']))
        if st.button("다시 뽑기"):
            del st.session_state['chosen_idx']
            st.rerun()


    # ---------- [로그아웃] ----------
    if st.button("로그아웃"):
        st.session_state.clear()
        st.rerun()
