import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class NewsDatabase:
    def __init__(self, db_path: str = "news_assistant.db"):
        """데이터베이스 초기화"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 뉴스 업체별 카테고리 링크 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_name, category)
                )
            """)
            
            # 뉴스 요약 정보 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT 0
                )
            """)
            
            # 관심 뉴스 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorite_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_summary_id INTEGER NOT NULL,
                    user_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (news_summary_id) REFERENCES news_summaries (id)
                )
            """)


            
            conn.commit()
    
    def add_news_source(self, source_name: str, category: str, url: str) -> bool:
        """뉴스 소스 추가"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO news_sources (source_name, category, url, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (source_name, category, url))
                conn.commit()
                return True
        except Exception as e:
            print(f"뉴스 소스 추가 실패: {e}")
            return False
    
    def get_news_sources(self, category: str = None) -> List[Dict]:
        """뉴스 소스 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if category:
                    cursor.execute("""
                        SELECT source_name, category, url, created_at, updated_at
                        FROM news_sources WHERE category = ?
                        ORDER BY updated_at DESC
                    """, (category,))
                else:
                    cursor.execute("""
                        SELECT source_name, category, url, created_at, updated_at
                        FROM news_sources
                        ORDER BY category, source_name
                    """)
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"뉴스 소스 조회 실패: {e}")
            return []
    
    def save_news_summary(self, title: str, url: str, category: str, source_name: str, 
                         summary: str, content: str = None) -> int:
        """뉴스 요약 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO news_summaries (title, url, category, source_name, summary, content)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, url, category, source_name, summary, content))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"뉴스 요약 저장 실패: {e}")
            return None
    
    def get_news_summaries(self, category: str = None, is_favorite: bool = None) -> List[Dict]:
        """뉴스 요약 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM news_summaries WHERE 1=1"
                params = []
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if is_favorite is not None:
                    query += " AND is_favorite = ?"
                    params.append(is_favorite)
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"뉴스 요약 조회 실패: {e}")
            return []
    
    def toggle_favorite(self, news_summary_id: int) -> bool:
        """관심 뉴스 토글"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 현재 상태 확인
                cursor.execute("SELECT is_favorite FROM news_summaries WHERE id = ?", (news_summary_id,))
                result = cursor.fetchone()
                if not result:
                    return False
                
                current_status = result[0]
                new_status = 1 if current_status == 0 else 0
                
                # 상태 업데이트
                cursor.execute("""
                    UPDATE news_summaries SET is_favorite = ? WHERE id = ?
                """, (new_status, news_summary_id))
                
                # 관심 뉴스 테이블에도 추가/제거
                if new_status == 1:
                    cursor.execute("""
                        INSERT OR IGNORE INTO favorite_news (news_summary_id)
                        VALUES (?)
                    """, (news_summary_id,))
                else:
                    cursor.execute("""
                        DELETE FROM favorite_news WHERE news_summary_id = ?
                    """, (news_summary_id,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"관심 뉴스 토글 실패: {e}")
            return False
    
    def get_news_by_id(self, news_id: int) -> Optional[Dict]:
        """ID로 뉴스 정보 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM news_summaries 
                    WHERE id = ?
                """, (news_id,))
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"뉴스 정보 조회 실패: {e}")
            return None

    def get_news_by_url(self, url: str) -> Optional[Dict]:
        """URL로 기존 뉴스 요약본 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM news_summaries 
                    WHERE url = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (url,))
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"URL로 뉴스 조회 실패: {e}")
            return None

    def is_news_summarized(self, url: str) -> bool:
        """뉴스가 이미 요약되었는지 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM news_summaries 
                    WHERE url = ?
                """, (url,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"뉴스 요약 상태 확인 실패: {e}")
            return False

    def get_all_news_summaries(self) -> List[Dict]:
        """모든 뉴스 요약본 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM news_summaries 
                    ORDER BY created_at DESC
                """)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"모든 뉴스 요약본 조회 실패: {e}")
            return []

    def get_news_summaries_by_category(self, category: str) -> List[Dict]:
        """카테고리별 뉴스 요약본 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM news_summaries 
                    WHERE category = ?
                    ORDER BY created_at DESC
                """, (category,))
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"카테고리별 뉴스 요약본 조회 실패: {e}")
            return []

    def get_favorite_news(self) -> List[Dict]:
        """관심 뉴스 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ns.*, fn.user_notes, fn.created_at as favorite_date
                    FROM news_summaries ns
                    JOIN favorite_news fn ON ns.id = fn.news_summary_id
                    ORDER BY fn.created_at DESC
                """)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"관심 뉴스 조회 실패: {e}")
            return []


    
    def update_user_notes(self, news_summary_id: int, notes: str) -> bool:
        """사용자 메모 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE favorite_news SET user_notes = ? WHERE news_summary_id = ?
                """, (notes, news_summary_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"사용자 메모 업데이트 실패: {e}")
            return False
    
    def delete_news_source(self, source_name: str, category: str) -> bool:
        """뉴스 소스 삭제"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM news_sources WHERE source_name = ? AND category = ?
                """, (source_name, category))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"뉴스 소스 삭제 실패: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """등록된 카테고리 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM news_sources ORDER BY category")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"카테고리 조회 실패: {e}")
            return []
    
    def get_sources_by_category(self, category: str) -> List[str]:
        """특정 카테고리의 뉴스 소스 목록 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT source_name FROM news_sources WHERE category = ?
                    ORDER BY source_name
                """, (category,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"뉴스 소스 조회 실패: {e}")
            return []

if __name__ == "__main__":
    # 테스트
    db = NewsDatabase()
    
    # 테스트 데이터 추가
    db.add_news_source("한국일보", "정치", "https://www.hankookilbo.com/News/Politics")
    db.add_news_source("조선일보", "정치", "https://www.chosun.com/politics/")
    
    # 데이터 조회
    sources = db.get_news_sources()
    print("뉴스 소스:", sources)
