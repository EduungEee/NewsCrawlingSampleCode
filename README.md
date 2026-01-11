# 📰 AI 뉴스 어시스턴트

뉴스 스크래핑, AI요약 위한 Streamlit 애플리케이션

## 🚀 빠른 시작

### 설치

1. **가상환경 생성**
```bash
python -m venv venv
```

2. **가상환경 활성화**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **라이브러리 설치**
```bash
pip install -r requirements.txt
```

4. **앱 실행**
```bash
streamlit run app.py
```

## 📋 주요 기능

### 🔍 뉴스 스크래핑
- **다중 뉴스 사이트 지원**: 한국일보, 연합뉴스, ZDNet, 조선일보, 중앙일보
- **고도화된 스크래핑**: requests + Selenium 이중 백업 시스템
- **실시간 모니터링**: 스크래핑 진행 상황 실시간 표시

### 📄 뉴스 요약
- **전체 내용 스크래핑**: 뉴스 URL의 전체 내용을 가져와서 요약
- **GPT API 연동**: OpenAI GPT-3.5-turbo를 사용한 고품질 요약
- **진행 상황 표시**: 단계별 진행률과 상태 메시지

### 💾 데이터 관리
- **SQLite 데이터베이스**: 뉴스 소스, 요약, 관심 뉴스 저장
- **관심 뉴스**: 마음에 드는 뉴스를 관심 목록에 추가
- **뉴스 소스 관리**: 커스텀 뉴스 사이트 등록 및 관리

## 🛠️ 기술 스택

### 프론트엔드
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Pandas**: 데이터 처리 및 표시

### 백엔드
- **Python 3.8+**: 메인 프로그래밍 언어
- **SQLite**: 데이터베이스
- **OpenAI API**: AI 요약 및 컨텐츠 생성

### 웹 스크래핑
- **requests**: HTTP 요청
- **BeautifulSoup**: HTML 파싱
- **Selenium**: 동적 콘텐츠 처리
- **Chrome WebDriver**: 브라우저 자동화

## 📁 프로젝트 구조

```
프로젝트/
├── app.py                    # 메인 애플리케이션
├── database.py               # 데이터베이스 관리
├── news_scraper.py           # 뉴스 스크래핑
├── news_summarizer.py        # 뉴스 요약
├── news_content_scraper.py   # 뉴스 내용 스크래핑
├── ui_components.py          # UI 컴포넌트
├── requirements.txt          # 필요한 라이브러리
└── README.md                # 프로젝트 설명
```

## 🔧 설정

### OpenAI API 키 설정
1. [OpenAI 웹사이트](https://platform.openai.com/api-keys)에서 API 키 발급
2. 앱 실행 후 왼쪽 사이드바에서 API 키 입력
3. "🔍 API 키 테스트" 버튼으로 유효성 확인

### 뉴스 소스 등록
1. "⚙️ 뉴스 소스 관리" 페이지로 이동
2. 뉴스 업체명, 카테고리, URL 입력
3. "💾 뉴스 소스 등록" 버튼 클릭

## 🎯 사용 방법

### 1. 뉴스 수집
1. 왼쪽 사이드바에서 뉴스 업체 선택
2. 뉴스 주제(카테고리) 선택
3. "📡 뉴스 가져오기" 버튼 클릭

### 2. 뉴스 요약
1. 수집된 뉴스 목록에서 원하는 뉴스 선택
2. "📄 선택한 뉴스 요약하기" 버튼 클릭
3. AI가 뉴스 전체 내용을 분석하여 요약 제공

### 3. 컨텐츠 생성
1. "🎨 컨텐츠 생성" 페이지로 이동
2. 요약된 뉴스 또는 관심 뉴스 선택
3. 컨텐츠 생성 프롬프트 입력
4. "🎨 컨텐츠 생성하기" 버튼 클릭

## 🐛 문제 해결

### Chrome WebDriver 오류
```bash
# Chrome 브라우저가 설치되어 있는지 확인
# Windows: C:\Program Files\Google\Chrome\Application\chrome.exe
```

### OpenAI API 오류
- API 키가 올바른지 확인
- API 사용량 한도 확인
- 네트워크 연결 상태 확인

### 라이브러리 설치 오류
```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Python 3.8+ 버전 사용
2. 모든 라이브러리 설치 완료
3. OpenAI API 키 유효성
4. 네트워크 연결 상태

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
