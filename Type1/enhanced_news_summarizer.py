"""
향상된 뉴스 요약기 - 더 자세한 요약과 본문 표시
"""
import openai
import os
from datetime import datetime
from news_content_scraper import NewsContentScraper

class EnhancedNewsSummarizer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.use_openai = False
        self.client = None
        
        if api_key and api_key.strip():
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key.strip())
                self.use_openai = True
                print("✅ Enhanced News Summarizer 초기화 완료")
            except Exception as e:
                print(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
                self.use_openai = False
        elif os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.use_openai = True
                print("✅ 환경변수에서 OpenAI API 키를 찾았습니다.")
            except Exception as e:
                print(f"❌ 환경변수 OpenAI API 키 초기화 실패: {e}")
                self.use_openai = False
        else:
            print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
            self.use_openai = False

    def summarize_news_detailed(self, url: str, title: str):
        """뉴스 URL의 전체 내용을 스크래핑하고 상세하게 요약"""
        if not self.use_openai:
            return "❌ OpenAI API 키가 필요합니다. 왼쪽 사이드바에서 API 키를 입력해주세요."
        
        try:
            # 뉴스 내용 스크래핑
            scraper = NewsContentScraper()
            content_data = scraper.scrape_news_content(url)
            
            if not content_data or not content_data.get('content'):
                return "❌ 뉴스 내용을 가져올 수 없습니다. URL을 확인해주세요."
            
            # 상세한 요약 프롬프트
            prompt = f"""
다음 뉴스 기사를 한국어로 상세하게 요약해주세요:

제목: {title}
URL: {url}

본문 내용:
{content_data['content']}

요약 시 다음 사항을 포함해주세요:
1. 핵심 내용 (3-4문장)
2. 주요 사실과 데이터
3. 배경 정보
4. 영향과 의미
5. 관련 맥락

요약은 500-800자 정도로 작성해주세요.
"""
            
            response = self.client.chat.completions.create(
                model="GPT-4 mini",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 뉴스 분석가입니다. 뉴스를 정확하고 상세하게 요약하는 것이 전문입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                'summary': summary,
                'full_content': content_data['content'],
                'title': content_data.get('title', title),
                'url': url,
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return f"❌ 뉴스 요약 중 오류가 발생했습니다: {str(e)}"



