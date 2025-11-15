from flask import Flask
from routes import bp as game_bp
from dotenv import load_dotenv
import os

# 환경변수 .env 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
# create_table_if_not_exists()

# 라우트 등록
app.register_blueprint(game_bp)

if __name__ == "__main__":
    # gunicorn --bind 0.0.0.0:5001 app:app --daemon
    app.run(host='0.0.0.0', port=5001, debug=True)
