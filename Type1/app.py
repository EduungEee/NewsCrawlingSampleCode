"""
AI 뉴스 어시스턴트 - 리팩터링된 메인 애플리케이션
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# 로컬 모듈 임포트
from database import NewsDatabase
from news_scraper import NewsScraper

from enhanced_news_summarizer import EnhancedNewsSummarizer
from ui_components import (
    render_header, render_navigation, render_sidebar,
    render_news_table, render_news_selection, render_summary_result,
    render_detailed_news_summary,
    render_db_news_selection, render_agency_buttons
)
# PPT 스타일 전역 CSS 적용
st.markdown("""
<style>
    /* PPT 이미지 스타일 적용 */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* 버튼 스타일 개선 */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 성공/에러 메시지 스타일 */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #10b981;
        border-radius: 8px;
        color: #065f46; /* 짙은 녹색 텍스트 */
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        border-radius: 8px;
        color: #991b1b; /* 짙은 빨간색 텍스트 */
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        color: #92400e; /* 짙은 주황색 텍스트 */
    }
    
    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        color: #1e40af; /* 짙은 파란색 텍스트 */
    }

    /* 사이드바 텍스트 흰색 강제 적용 */
    [data-testid="stSidebar"] {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: white !important;
    }
    
    /* 사이드바 입력 필드 라벨 */
    .st-emotion-cache-16idsys p {
        color: white !important;
    }
    
    /* 기본 텍스트 색상 강제 (라이트 모드 기준) */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }
    
    /* 헤더나 특정 컴포넌트의 흰색 텍스트는 유지해야 함으로 구체성 높임 */
    .main-header h1, .main-header p {
        color: white !important;
    }
    
    .summary-box h3, .summary-box p {
        color: white !important;
    }
    
    .stButton > button {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .page-button {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .page-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .news-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .summary-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .content-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """세션 상태 초기화"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'news'
    if 'selected_news' not in st.session_state:
        st.session_state.selected_news = None
    if 'news_summary' not in st.session_state:
        st.session_state.news_summary = None
    if 'db' not in st.session_state:
        st.session_state.db = NewsDatabase()

def show_news_page():
    """뉴스 요약 페이지"""
    st.header("📰 뉴스 요약")
    
    if 'news_list' in st.session_state and st.session_state.news_list:
        news_list = st.session_state.news_list
        category = st.session_state.selected_category
        
        # 뉴스 테이블 렌더링
        df = render_news_table(news_list, category)
        
        # 뉴스 선택
        selected_index = render_news_selection(news_list)
        
        if st.button("📄 선택한 뉴스 요약하기"):
            selected_news = news_list[selected_index]
            st.session_state.selected_news = selected_news
            
            # API 키 확인
            if not st.session_state.get('api_key'):
                st.error("❌ OpenAI API 키가 필요합니다. 왼쪽 사이드바에서 API 키를 입력하고 테스트해주세요.")
                return
            
            if not st.session_state.get('api_key_valid'):
                st.error("❌ API 키가 유효하지 않습니다. 왼쪽 사이드바에서 '🔍 API 키 테스트' 버튼을 클릭해주세요.")
                return
            
            # 기존 요약본 확인
            db = st.session_state.db
            existing_news = db.get_news_by_url(selected_news['url'])
            
            if existing_news:
                # 기존 요약본이 있는 경우
                st.success("✅ 이미 요약된 뉴스입니다! 기존 요약본을 불러옵니다.")
                
                # 기존 요약본 표시
                st.subheader("📄 기존 뉴스 요약")
                st.markdown(f"**제목:** {existing_news['title']}")
                st.markdown(f"**URL:** {existing_news['url']}")
                st.markdown(f"**요약 생성 시간:** {existing_news['created_at']}")
                st.markdown(f"**카테고리:** {existing_news['category']}")
                st.markdown(f"**뉴스 소스:** {existing_news['source_name']}")
                
                st.markdown("### 📝 요약 내용")
                st.write(existing_news['summary'])
                
                # 세션 상태 업데이트
                st.session_state.news_summary = existing_news['summary']
                st.session_state.current_news_id = existing_news['id']
                
                return
            
            # 진행 상황 표시
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            try:
                # 1단계: API 키 확인
                status_text.text("🔑 API 키 확인 중...")
                progress_bar.progress(10)
                
                # API 키가 변경되었거나 요약기가 없으면 새로 초기화
                current_api_key = st.session_state.get('api_key')
                if ('enhanced_summarizer' not in st.session_state or 
                    not hasattr(st.session_state.enhanced_summarizer, 'api_key') or 
                    st.session_state.enhanced_summarizer.api_key != current_api_key):
                    st.session_state.enhanced_summarizer = EnhancedNewsSummarizer(current_api_key)
                
                summarizer = st.session_state.enhanced_summarizer
                
                # API 키 유효성 재확인
                if not current_api_key:
                    st.error("❌ OpenAI API 키가 설정되지 않았습니다. 왼쪽 사이드바에서 API 키를 입력해주세요.")
                    return
                
                if not summarizer.use_openai:
                    st.error("❌ OpenAI API 키가 유효하지 않습니다. 왼쪽 사이드바에서 '🔍 API 키 테스트' 버튼을 클릭해주세요.")
                    return
                
                # 2단계: 뉴스 내용 스크래핑 및 상세 요약
                status_text.text("🔍 뉴스 내용을 가져오는 중...")
                progress_bar.progress(30)
                
                # 향상된 뉴스 요약 (상세 요약 + 본문)
                result = summarizer.summarize_news_detailed(
                    selected_news['url'], 
                    selected_news['title']
                )
                
                # 3단계: 요약 완료
                progress_bar.progress(80)
                status_text.text("📄 뉴스 요약 완료!")
                
                # API 키 오류 확인
                if isinstance(result, str) and result.startswith("❌"):
                    st.error(result)
                    return
                
                # 4단계: 완료
                progress_bar.progress(100)
                status_text.text("✅ 뉴스 요약이 완료되었습니다!")
                
                # 진행 상황 컨테이너 숨기기
                progress_container.empty()
                
                # 결과 표시
                if isinstance(result, dict):
                    st.session_state.news_summary = result['summary']
                    st.session_state.news_full_content = result['full_content']
                    
                    # 자동으로 DB에 저장
                    try:
                        db = st.session_state.db
                        source_name = selected_news.get('source_name', '기본')
                        news_id = db.save_news_summary(
                            title=selected_news['title'],
                            url=selected_news['url'],
                            category=category,
                            source_name=source_name,
                            summary=result['summary']
                        )
                        
                        if news_id:
                            st.session_state.current_news_id = news_id
                            st.success("✅ 뉴스 요약이 데이터베이스에 저장되었습니다!")
                        else:
                            st.warning("⚠️ 뉴스 저장에 실패했습니다.")
                    except Exception as e:
                        st.error(f"❌ 데이터베이스 저장 중 오류가 발생했습니다: {e}")
                    
                    # 상세 요약 표시
                    st.subheader("📄 상세 뉴스 요약")
                    st.markdown(f"**제목:** {result['title']}")
                    st.markdown(f"**URL:** {result['url']}")
                    st.markdown(f"**스크래핑 시간:** {result['scraped_at']}")
                    
                    st.markdown("### 📝 요약 내용")
                    st.write(result['summary'])
                    
                else:
                    st.error("❌ 뉴스 요약에 실패했습니다. 다시 시도해주세요.")
                
            except Exception as e:
                st.error(f"❌ 뉴스 요약 중 오류가 발생했습니다: {e}")
                return
        
    else:
        st.info("👈 왼쪽 사이드바에서 뉴스 주제를 선택하고 언론사를 클릭하세요.")
        
        # 언론사 버튼 렌더링
        db = st.session_state.db
        category = st.session_state.selected_category if 'selected_category' in st.session_state else "정치"
        sources = db.get_news_sources(category)
        
        # 사이드바에서 선택된 언론사 필터링
        sidebar_source = st.session_state.get('source_select', '전체')
        if sidebar_source != "전체":
            sources = [s for s in sources if s['source_name'] == sidebar_source]
        
        selected_source = render_agency_buttons(sources)
        
        if selected_source:
            with st.spinner(f"🔍 {selected_source['source_name']}에서 뉴스 수집 중..."):
                try:
                    scraper = NewsScraper()
                    news_list = scraper.get_news_by_category(category, selected_source['source_name'])
                    
                    if news_list:
                        st.session_state.news_list = news_list
                        st.session_state.selected_category = category
                        st.success(f"✅ {len(news_list)}개의 뉴스를 가져왔습니다!")
                        st.rerun()
                    else:
                        st.warning("⚠️ 뉴스를 찾을 수 없습니다.")
                except Exception as e:
                    st.error(f"❌ 뉴스 수집 중 오류가 발생했습니다: {e}")

        # 스크래핑 문제 해결 가이드
        with st.expander("🔧 스크래핑 문제 해결 가이드"):
            st.markdown("""
            **뉴스 스크래핑이 작동하지 않는 경우:**
            
            1. **네트워크 연결 확인**: 인터넷 연결이 안정적인지 확인하세요
            2. **뉴스 소스 등록**: 뉴스 소스 관리에서 신뢰할 수 있는 뉴스 사이트를 등록하세요
            3. **다른 카테고리 시도**: 일부 카테고리는 접근이 제한될 수 있습니다
            4. **샘플 데이터 사용**: 스크래핑이 실패해도 샘플 데이터로 기능을 테스트할 수 있습니다
            
            **지원하는 뉴스 사이트:**
            - 한국일보: https://www.hankookilbo.com/News/Politics
            - 연합뉴스: https://www.yna.co.kr/news?site=navi_latest_depth01
            - ZDNet: https://zdnet.co.kr/news/
            - 조선일보: https://www.chosun.com/politics/
            - 중앙일보: https://www.joongang.co.kr/politics
            """)



def show_sources_page():
    """언론사 설정 페이지"""
    st.header("📰 언론사 설정")
    
    db = st.session_state.db
    
    # 탭 생성 (단일 탭으로 변경)
    st.subheader("📝 새로운 언론사 등록")
        
    col1, col2 = st.columns(2)
    with col1:
        source_name = st.text_input("언론사명", placeholder="예: 한국일보, 조선일보, 중앙일보")
    
    with col2:
        categories = ["정치", "경제", "사회", "국제", "문화", "연예", "스포츠", "사람", "라이프", "오피니언"]
        category = st.selectbox("카테고리", categories)
    
    url = st.text_input("뉴스 페이지 URL", placeholder="https://example.com/news/category")
    
    if st.button("💾 언론사 등록", use_container_width=True):
        if source_name and category and url:
            success = db.add_news_source(source_name, category, url)
            if success:
                st.success(f"✅ {source_name}의 {category} 카테고리가 등록되었습니다!")
                st.rerun()
            else:
                st.error("❌ 언론사 등록에 실패했습니다.")
        else:
            st.warning("⚠️ 모든 필드를 입력해주세요.")
    
    st.markdown("---")
    
    # 등록된 언론사 목록
    st.subheader("📋 등록된 언론사 목록")
    
    # 카테고리별 필터
    all_categories = db.get_categories()
    if all_categories:
        col1, col2 = st.columns(2)
        with col1:
            selected_category_filter = st.selectbox("카테고리 필터", ["전체"] + all_categories)
        with col2:
            # 업체별 필터
            all_sources = db.get_news_sources()
            all_source_names = list(set([s['source_name'] for s in all_sources]))
            selected_source_filter = st.selectbox("언론사 필터", ["전체"] + all_source_names)
        
        if selected_category_filter == "전체":
            sources = db.get_news_sources()
        else:
            sources = db.get_news_sources(selected_category_filter)
        
        # 업체별 필터링
        if selected_source_filter != "전체":
            sources = [s for s in sources if s['source_name'] == selected_source_filter]
        
        if sources:
            # DataFrame으로 표시
            df_data = []
            for source in sources:
                df_data.append({
                    '언론사': source['source_name'],
                    '카테고리': source['category'],
                    'URL': source['url'],
                    '등록일': source['created_at'][:10]
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # 삭제 기능
            st.subheader("🗑️ 언론사 삭제")
            delete_options = [f"{s['source_name']} - {s['category']}" for s in sources]
            selected_delete = st.selectbox("삭제할 언론사를 선택하세요", delete_options)
            
            if st.button("🗑️ 선택한 언론사 삭제", type="secondary"):
                if selected_delete:
                    source_name, category = selected_delete.split(" - ")
                    success = db.delete_news_source(source_name, category)
                    if success:
                        st.success(f"✅ {source_name}의 {category} 카테고리가 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 언론사 삭제에 실패했습니다.")
        else:
            st.info("📝 등록된 언론사가 없습니다.")
    else:
        st.info("📝 등록된 언론사가 없습니다.")
    



def main():
    """메인 애플리케이션"""
    # 세션 상태 초기화
    initialize_session_state()
    
    # 헤더 렌더링
    render_header()
    
    # 네비게이션 렌더링
    render_navigation()
    
    # 사이드바 렌더링 (뉴스 가져오기 버튼 로직 제거)
    selected_category, selected_source, _ = render_sidebar()
    
    # 카테고리 변경 시 초기화
    if 'selected_category' not in st.session_state or st.session_state.selected_category != selected_category:
        st.session_state.selected_category = selected_category
        st.session_state.news_list = []  # 리스트 초기화
    
    
    # 메인 컨텐츠
    # 메인 컨텐츠
    if st.session_state.current_page == 'news':
        show_news_page()
    elif st.session_state.current_page == 'sources':
        show_sources_page()

if __name__ == "__main__":
    main()
