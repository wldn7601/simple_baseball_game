from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from game_service import game_check
import db
import random

bp = Blueprint("game", __name__)

# ------------------------
# 홈 화면
# ------------------------
@bp.route("/")
def home():
    return render_template("home.html")
 
# 히스토리 보기
@bp.route("/history")
def history_page():
    records = db.get_all_records()
    return render_template("history.html", records=records)


# ------------------------
# 게임 시작
# ------------------------
@bp.route("/start", methods=["POST"])
def start_game():
    # 이미 진행 중이라면 그냥 게임 페이지로
    if session.get("target") and not session.get("is_clear", False):
        return redirect(url_for("game.game_page"))

    # 새 게임 생성
    digits = random.sample(range(0, 10), 4)
    session["target"] = "".join(str(d) for d in digits)
    session["history"] = []
    session["attempts"] = 0
    session["is_clear"] = False

    return redirect(url_for("game.game_page"))



# ------------------------
# 게임 화면
# ------------------------
@bp.route("/game")
def game_page():
    return render_template(
        "game.html",
        history=session.get("history", []),
        attempts=session.get("attempts", 0),
        is_clear=session.get("is_clear", False),
        target=session.get("target"),
        last_attempts=session.get("last_attempts")
    )




# ------------------------
# 제출 처리
# ------------------------
@bp.route("/submit", methods=["POST"])
def submit_guess():
    guess = request.form.get("guess")  # "1234"

    # 중복 숫자 체크
    if len(set(guess)) != len(guess):
        flash("중복 숫자는 허용되지 않습니다.", "error")
        return redirect(url_for("game.game_page"))

    # 입력 유효성 검사
    if not guess or len(guess) != 4 or not guess.isdigit():
        flash("4자리 숫자를 입력하세요.")
        return redirect(url_for("game.game_page"))

    session["attempts"] += 1

    target = session.get("target")

    strike, ball = game_check(guess, target)  # 새 함수

    # history 저장
    session["history"].append({
        "number": guess,
        "result": f"{strike}S {ball}B" if strike or ball else "OUT"
    })

    if strike == 4:
        final_attempts = session["attempts"]
        session["last_attempts"] = final_attempts
        session["is_clear"] = True

        db.save_record(target, final_attempts)

        return redirect(url_for("game.game_page"))

    return redirect(url_for("game.game_page"))


# 모든 기록 삭제
@bp.route("/reset_all", methods=["POST"])
def reset_all():
    # 1. DB 기록 삭제
    conn = db.get_connection_with_retry()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE game_records;")  # 전체 삭제
    conn.commit()
    cursor.close()
    conn.close()

    # 2. 세션 초기화
    session.clear()

    return redirect(url_for("game.home"))

# 개별 데이터 삭제
@bp.route("/delete/<int:record_id>", methods=["POST"])
def delete_history(record_id):
    db.delete_record(record_id)
    return redirect(url_for("game.history_page"))
