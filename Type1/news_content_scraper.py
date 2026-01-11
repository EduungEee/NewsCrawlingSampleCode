"""
뉴스 URL의 전체 내용을 스크래핑하는 모듈
"""
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re

class NewsContentScraper:
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
    
    def scrape_news_content(self, url):
        """뉴스 URL의 전체 내용을 스크래핑"""
        try:
            print(f"📰 뉴스 내용 스크래핑 시작: {url}")
            
            # 1단계: requests + BeautifulSoup 시도
            content = self._scrape_with_requests(url)
            if content:
                return content
            
            # 2단계: Selenium 시도
            content = self._scrape_with_selenium(url)
            if content:
                return content
            
            return None
            
        except Exception as e:
            print(f"❌ 뉴스 내용 스크래핑 실패: {e}")
            return None
    
    def _scrape_with_requests(self, url):
        """requests를 사용한 뉴스 내용 스크래핑"""
        try:
            print(f"📡 requests로 {url} 접속 중...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 사이트별 최적화된 셀렉터
            content_selectors = {
                '한국일보': [
                    '.news-content', '.article-content', '.content',
                    'article .text', '.news-text', '.article-text'
                ],
                '연합뉴스': [
                    '.news-con', '.article-content', '.content',
                    'article .text', '.news-text', '.article-text'
                ],
                'ZDNet': [
                    '.newsPost .content', '.article-content', '.content',
                    'article .text', '.news-text', '.article-text'
                ],
                '조선일보': [
                    '.story-content', '.article-content', '.content',
                    'article .text', '.news-text', '.article-text'
                ],
                '중앙일보': [
                    '.story-content', '.article-content', '.content',
                    'article .text', '.news-text', '.article-text'
                ]
            }
            
            # 일반적인 뉴스 내용 셀렉터
            general_selectors = [
                'article', '.article-content', '.news-content', '.content',
                '.story-content', '.post-content', '.entry-content',
                '[class*="article"]', '[class*="content"]', '[class*="story"]',
                'main', '.main-content', '.text-content'
            ]
            
            # 모든 셀렉터 시도
            all_selectors = []
            for site_selectors in content_selectors.values():
                all_selectors.extend(site_selectors)
            all_selectors.extend(general_selectors)
            
            content_text = ""
            
            for selector in all_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        for element in elements:
                            text = element.get_text(strip=True)
                            if len(text) > 100:  # 충분한 길이의 텍스트만
                                content_text = text
                                print(f"✅ 뉴스 내용 발견 (셀렉터: {selector}): {len(text)}자")
                                break
                        if content_text:
                            break
                except Exception as e:
                    continue
            
            if content_text:
                # 텍스트 정리
                content_text = self._clean_text(content_text)
                return {
                    'title': self._extract_title(soup),
                    'content': content_text,
                    'url': url,
                    'method': 'requests'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ requests 스크래핑 실패: {e}")
            return None
    
    def _scrape_with_selenium(self, url):
        """Selenium을 사용한 뉴스 내용 스크래핑"""
        try:
            print(f"🌐 Selenium으로 {url} 접속 중...")
            
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # WebDriver 초기화
            driver = None
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                try:
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                except Exception as e2:
                    print(f"❌ WebDriver 초기화 실패: {e2}")
                    return None
            
            try:
                driver.get(url)
                time.sleep(5)  # JS 렌더링 대기
                print(f"✅ 페이지 로드 완료: {url}")
                
                # 뉴스 내용 셀렉터들
                content_selectors = [
                    'article', '.article-content', '.news-content', '.content',
                    '.story-content', '.post-content', '.entry-content',
                    '[class*="article"]', '[class*="content"]', '[class*="story"]',
                    'main', '.main-content', '.text-content'
                ]
                
                content_text = ""
                title = ""
                
                for selector in content_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for element in elements:
                                text = element.text.strip()
                                if len(text) > 100:  # 충분한 길이의 텍스트만
                                    content_text = text
                                    print(f"✅ 뉴스 내용 발견 (셀렉터: {selector}): {len(text)}자")
                                    break
                            if content_text:
                                break
                    except Exception as e:
                        continue
                
                # 제목 추출
                try:
                    title_element = driver.find_element(By.TAG_NAME, 'h1')
                    title = title_element.text.strip()
                except:
                    try:
                        title_element = driver.find_element(By.CSS_SELECTOR, '.title, .headline, h1, h2')
                        title = title_element.text.strip()
                    except:
                        title = "제목을 찾을 수 없습니다."
                
                if content_text:
                    # 텍스트 정리
                    content_text = self._clean_text(content_text)
                    return {
                        'title': title,
                        'content': content_text,
                        'url': url,
                        'method': 'selenium'
                    }
                
                return None
                
            finally:
                driver.quit()
                print("🔚 WebDriver 종료")
                
        except Exception as e:
            print(f"❌ Selenium 스크래핑 실패: {e}")
            return None
    
    def _extract_title(self, soup):
        """BeautifulSoup에서 제목 추출"""
        try:
            # 다양한 제목 셀렉터 시도
            title_selectors = [
                'h1', '.title', '.headline', '.article-title', '.news-title',
                'title', '.post-title', '.entry-title'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and len(title) > 5:
                        return title
            
            return "제목을 찾을 수 없습니다."
        except:
            return "제목을 찾을 수 없습니다."
    
    def _clean_text(self, text):
        """텍스트 정리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 특수 문자 정리
        text = re.sub(r'[^\w\s가-힣.,!?]', '', text)
        # 연속된 줄바꿈 제거
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
