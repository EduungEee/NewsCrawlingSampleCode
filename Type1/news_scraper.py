"""
뉴스 스크래핑 관련 기능
"""
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from database import NewsDatabase

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_news_by_category(self, category, source_name=None):
        """카테고리별 뉴스를 가져오는 함수"""
        try:
            # DB에서 뉴스 소스 확인
            db = NewsDatabase()
            sources = db.get_news_sources(category)
            
            if not sources:
                return self._get_sample_news(category)
            
            # 특정 소스가 지정된 경우
            if source_name:
                sources = [s for s in sources if s['source_name'] == source_name]
            
            if not sources:
                return self._get_sample_news(category)
            
            # 모든 소스에서 뉴스 수집
            all_news = []
            for source in sources:
                try:
                    news_list = self._scrape_from_source(source, category)
                    all_news.extend(news_list)
                except Exception as e:
                    print(f"{source['source_name']} 스크래핑 실패: {e}")
                    continue
            
            return all_news if all_news else self._get_sample_news(category)
            
        except Exception as e:
            print(f"스크래핑 중 오류 발생: {e}")
            return self._get_sample_news(category)
    
    def _scrape_from_source(self, source, category):
        """특정 소스에서 뉴스 스크래핑"""
        try:
            print(f"🔍 {source['source_name']}에서 뉴스 스크래핑 시작...")
            
            # 1단계: requests + BeautifulSoup 시도
            news_list = self._scrape_with_requests(source, category)
            if news_list:
                print(f"✅ requests로 {len(news_list)}개 뉴스 수집 성공")
                return news_list
            
            # 2단계: Selenium 시도
            news_list = self._scrape_with_selenium(source, category)
            if news_list:
                print(f"✅ Selenium으로 {len(news_list)}개 뉴스 수집 성공")
                return news_list
            
            print(f"❌ {source['source_name']}에서 뉴스 수집 실패")
            return []
            
        except Exception as e:
            print(f"❌ 소스 스크래핑 실패: {e}")
            return []
    
    def _scrape_with_requests(self, source, category):
        """requests를 사용한 스크래핑"""
        try:
            url = source['url']
            print(f"📡 {url}에 요청 중...")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            print(f"✅ HTTP 응답 성공: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_list = []
            processed_urls = set()
            
            # 더 포괄적인 셀렉터로 뉴스 링크 찾기
            selectors = [
                'a[href*="/News/"]', 'a[href*="/news/"]', 'a[href*="/article/"]',
                'a[href*="/story/"]', 'a[href*="/view/"]', 'a[href*="/read/"]',
                '.news-item a', '.article-item a', 'article a',
                '.list-item a', '.item a', '[class*="news"] a',
                '[class*="article"] a', '[class*="story"] a',
                'h1 a', 'h2 a', 'h3 a', 'h4 a'
            ]
            
            print(f"🔍 {len(selectors)}개 셀렉터로 뉴스 검색 중...")
            
            for i, selector in enumerate(selectors):
                try:
                    links = soup.select(selector)
                    print(f"셀렉터 {i+1}/{len(selectors)}: '{selector}' -> {len(links)}개 링크 발견")
                    
                    if links:
                        for link in links[:20]:  # 최대 20개까지
                            try:
                                href = link.get('href')
                                if not href:
                                    continue
                                
                                # URL 정규화
                                if href.startswith('/'):
                                    href = source['base_url'].rstrip('/') + href
                                elif not href.startswith('http'):
                                    href = source['base_url'] + href
                                
                                if href in processed_urls:
                                    continue
                                processed_urls.add(href)
                                
                                # 제목 추출
                                title = link.get_text(strip=True)
                                if not title:
                                    title_elem = link.find(['h1', 'h2', 'h3', 'h4', 'span', 'div', 'strong'])
                                    if title_elem:
                                        title = title_elem.get_text(strip=True)
                                
                                if title and len(title) > 5:
                                    news_list.append({
                                        'title': title,
                                        'url': href,
                                        'category': category,
                                        'source_name': source['source_name']
                                    })
                                    print(f"📰 뉴스 추가: {title[:50]}...")
                                    
                                    if len(news_list) >= 15:  # 최대 15개
                                        break
                            except Exception as e:
                                continue
                    
                    if news_list:
                        print(f"✅ {len(news_list)}개 뉴스 수집 완료")
                        break
                        
                except Exception as e:
                    print(f"셀렉터 {selector} 처리 중 오류: {e}")
                    continue
            
            return news_list
            
        except Exception as e:
            print(f"❌ requests 스크래핑 실패: {e}")
            return []
    
    def _scrape_with_selenium(self, source, category):
        """Selenium을 사용한 스크래핑 - 참고프로젝트 기반 개선"""
        try:
            url = source['url']
            print(f"🌐 Selenium으로 {url} 접속 중...")
            
            # Chrome 옵션 설정 (참고프로젝트 기반)
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # WebDriver 초기화 (WinError 193 해결)
            driver = None
            
            # 방법 1: 직접 Chrome 실행
            try:
                driver = webdriver.Chrome(options=chrome_options)
                print("✅ Chrome WebDriver 직접 실행 성공")
            except Exception as e:
                print(f"❌ Chrome WebDriver 직접 실행 실패: {e}")
                
                # 방법 2: WebDriverManager 사용
                try:
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                    print("✅ WebDriverManager로 실행 성공")
                except Exception as e2:
                    print(f"❌ WebDriverManager도 실패: {e2}")
                    
                    # 방법 3: 시스템 PATH의 chromedriver 사용
                    try:
                        driver = webdriver.Chrome(service=Service(), options=chrome_options)
                        print("✅ 시스템 PATH의 chromedriver 사용 성공")
                    except Exception as e3:
                        print(f"❌ 모든 WebDriver 초기화 방법 실패: {e3}")
                        return []
            
            try:
                driver.get(url)
                time.sleep(5)  # JS 렌더링 대기
                print(f"✅ 페이지 로드 완료: {url}")
                
                # 스크롤하여 동적 콘텐츠 로드
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                
                news_list = []
                processed_urls = set()
                
                # 참고프로젝트 기반 셀렉터 (사이트별 최적화)
                site_selectors = {
                    '연합뉴스': [
                        '//ul/li//strong/a',  # XPath 방식
                        '//ul/li//a',
                        '.news-con a',
                        'article a'
                    ],
                    'ZDNet': [
                        '.newsPost a',  # 참고프로젝트에서 사용한 셀렉터
                        '.newsPost h3 a',
                        'article a'
                    ],
                    '한국일보': [
                        '.news-item a',
                        'article a',
                        '.list-item a'
                    ],
                    '조선일보': [
                        '.story-item a',
                        'article a',
                        '.list-item a'
                    ],
                    '중앙일보': [
                        '.story-item a',
                        'article a',
                        '.list-item a'
                    ]
                }
                
                # 사이트별 최적화된 셀렉터 사용
                selectors = site_selectors.get(source['source_name'], [
                    'a[href*="/News/"]', 'a[href*="/news/"]', 'a[href*="/article/"]',
                    '.news-item a', '.article-item a', 'article a',
                    '.list-item a', '.item a', '[class*="news"] a'
                ])
                
                print(f"🔍 {len(selectors)}개 셀렉터로 뉴스 검색 중...")
                
                for i, selector in enumerate(selectors):
                    try:
                        if selector.startswith('//'):
                            # XPath 사용
                            elements = driver.find_elements(By.XPATH, selector)
                        else:
                            # CSS 셀렉터 사용
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        print(f"셀렉터 {i+1}/{len(selectors)}: '{selector}' -> {len(elements)}개 요소 발견")
                        
                        for element in elements[:20]:  # 최대 20개
                            try:
                                href = element.get_attribute('href')
                                if not href or href in processed_urls:
                                    continue
                                
                                processed_urls.add(href)
                                
                                # URL 정규화
                                if href.startswith('/'):
                                    href = source['base_url'].rstrip('/') + href
                                elif not href.startswith('http'):
                                    href = source['base_url'] + href
                                
                                # 제목 추출 (참고프로젝트 방식)
                                title = element.text.strip()
                                if not title:
                                    try:
                                        # h3 태그에서 제목 찾기 (ZDNet 방식)
                                        title_elem = element.find_element(By.TAG_NAME, 'h3')
                                        title = title_elem.text.strip()
                                    except:
                                        try:
                                            # strong 태그에서 제목 찾기
                                            title_elem = element.find_element(By.TAG_NAME, 'strong')
                                            title = title_elem.text.strip()
                                        except:
                                            continue
                                
                                if title and len(title) > 5:
                                    news_list.append({
                                        'title': title,
                                        'url': href,
                                        'category': category,
                                        'source_name': source['source_name']
                                    })
                                    print(f"📰 뉴스 추가: {title[:50]}...")
                                    
                                    if len(news_list) >= 15:  # 최대 15개
                                        break
                            except Exception as e:
                                continue
                        
                        if news_list:
                            print(f"✅ {len(news_list)}개 뉴스 수집 완료")
                            break
                            
                    except Exception as e:
                        print(f"셀렉터 {selector} 처리 중 오류: {e}")
                        continue
                        
            finally:
                driver.quit()
                print("🔚 WebDriver 종료")
                
            return news_list
            
        except Exception as e:
            print(f"❌ Selenium 스크래핑 실패: {e}")
            return []
    
    def _get_sample_news(self, category):
        """샘플 뉴스 데이터"""
        sample_news = {
            "정치": [
                {"title": "국회 예산안 심의 진행 상황", "url": f"https://example.com/news/1", "category": "정치", "source_name": "샘플"},
                {"title": "정치개혁 관련 논의 활발", "url": f"https://example.com/news/2", "category": "정치", "source_name": "샘플"},
                {"title": "여야 간 정책 협의 지속", "url": f"https://example.com/news/3", "category": "정치", "source_name": "샘플"},
                {"title": "지방선거 준비 본격화", "url": f"https://example.com/news/4", "category": "정치", "source_name": "샘플"},
                {"title": "국정감사 결과 발표", "url": f"https://example.com/news/5", "category": "정치", "source_name": "샘플"}
            ],
            "경제": [
                {"title": "주식시장 변동성 증가", "url": f"https://example.com/news/1", "category": "경제", "source_name": "샘플"},
                {"title": "부동산 시장 동향 분석", "url": f"https://example.com/news/2", "category": "경제", "source_name": "샘플"},
                {"title": "기업 실적 발표 시즌", "url": f"https://example.com/news/3", "category": "경제", "source_name": "샘플"},
                {"title": "환율 변동 영향 분석", "url": f"https://example.com/news/4", "category": "경제", "source_name": "샘플"},
                {"title": "경제 지표 발표", "url": f"https://example.com/news/5", "category": "경제", "source_name": "샘플"}
            ]
        }
        
        return sample_news.get(category, [
            {"title": f"{category} 관련 뉴스 1", "url": f"https://example.com/news/1", "category": category, "source_name": "샘플"},
            {"title": f"{category} 관련 뉴스 2", "url": f"https://example.com/news/2", "category": category, "source_name": "샘플"},
            {"title": f"{category} 관련 뉴스 3", "url": f"https://example.com/news/3", "category": category, "source_name": "샘플"},
            {"title": f"{category} 관련 뉴스 4", "url": f"https://example.com/news/4", "category": category, "source_name": "샘플"},
            {"title": f"{category} 관련 뉴스 5", "url": f"https://example.com/news/5", "category": category, "source_name": "샘플"}
        ])
