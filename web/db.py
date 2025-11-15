import mysql.connector
import os
import time
from mysql.connector import Error


# MySQL 연결 (재시도 포함)
def get_connection_with_retry(retry=10, delay=2):
    for i in range(retry):
        try:
            conn = mysql.connector.connect(
                host="db",
                user="root",
                password=os.getenv("MYSQL_PASSWORD"),
                database="baseball_db"
            )
            return conn
        except Error as e:
            print(f"MySQL 연결 실패, 재시도 {i+1}/{retry}: {e}")
            time.sleep(delay)
    raise Exception("MySQL 접속 실패 반복. 서버 시작 불가.")


# 모든 기록 가져오기
def get_all_records():
    conn = get_connection_with_retry()
    cursor = conn.cursor(dictionary=True)

    sql = "SELECT id, target_number, attempts, created_at FROM game_records ORDER BY id DESC"
    cursor.execute(sql)
    records = cursor.fetchall()

    cursor.close()
    conn.close()
    return records


# 데이터 저장 (retry 적용)
def save_record(target_number, attempts):
    conn = get_connection_with_retry()
    cursor = conn.cursor()

    sql = """
        INSERT INTO game_records (target_number, attempts)
        VALUES (%s, %s)
    """
    cursor.execute(sql, (target_number, attempts))
    conn.commit()

    cursor.close()
    conn.close()


# 테이블 생성 (retry 적용)
def create_table_if_not_exists():
    try:
        conn = get_connection_with_retry()
        cursor = conn.cursor()

        sql = """
        CREATE TABLE IF NOT EXISTS game_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            target_number VARCHAR(4) NOT NULL,
            attempts INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(sql)

        cursor.execute("ALTER TABLE game_records AUTO_INCREMENT = 1;")
        conn.commit()
        cursor.close()
        conn.close()

        print("game_records 테이블 확인 완료 (없으면 자동 생성됨).")

    except Error as e:
        print("테이블 생성 중 오류:", e)


# 데이터 삭제 (retry 적용)
def delete_record(record_id):
    conn = get_connection_with_retry()
    cursor = conn.cursor()

    sql = "DELETE FROM game_records WHERE id = %s"
    cursor.execute(sql, (record_id,))
    conn.commit()

    cursor.close()
    conn.close()

# 자동으로 테이블 생성 (gunicorn 안전하게 동작)
try:
    create_table_if_not_exists()
except Exception as e:
    print("DB init error:", e)
