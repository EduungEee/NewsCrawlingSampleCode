"""
데이터베이스 초기화 및 기본 뉴스 소스 추가
"""
from database import NewsDatabase

def init_default_sources():
    """기본 뉴스 소스들을 데이터베이스에 추가"""
    db = NewsDatabase()
    
    import json
    import os
    
    # mediacompany.json 파일 경로
    json_path = os.path.join(os.path.dirname(__file__), 'mediacompany.json')
    
    if not os.path.exists(json_path):
        print(f"❌ {json_path} 파일을 찾을 수 없습니다.")
        return 0
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        media_companies = data.get('언론사', [])
        added_count = 0
        
        for company in media_companies:
            name = company['name']
            categories = company['categories']
            
            for category, url in categories.items():
                try:
                    success = db.add_news_source(name, category, url)
                    if success:
                        added_count += 1
                        print(f"✅ {name} - {category} 추가됨")
                    else:
                        print(f"⚠️ {name} - {category} 이미 존재함")
                except Exception as e:
                    print(f"❌ {name} - {category} 추가 실패: {e}")
                    
        print(f"\n🎉 총 {added_count}개의 뉴스 소스가 추가되었습니다!")
        return added_count
        
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {e}")
        return 0

if __name__ == "__main__":
    init_default_sources()
