"""
update.py - 매일 아침 9시(KST) GitHub Actions 자동 실행
template.html + config.json -> index.html 생성
"""

import json
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

# 영어 문장 목록 (config.json에 quote_override_en 이 있으면 그걸 우선 사용)
QUOTES = [
    {"en": "Even though the future seems far away, it is actually beginning right now.",
     "ko": "비록 미래가 멀리 있는 것처럼 보일지라도, 사실 바로 지금 시작되고 있다. - Mattie Stepanek"},
    {"en": "Success is the sum of small efforts repeated day in and day out.",
     "ko": "성공은 매일 반복되는 작은 노력들의 합이다. - Robert Collier"},
    {"en": "The secret of getting ahead is getting started.",
     "ko": "앞서 나가는 비결은 시작하는 것이다. - Mark Twain"},
    {"en": "Do something today that your future self will thank you for.",
     "ko": "미래의 내가 감사할 일을 오늘 하라."},
    {"en": "It does not matter how slowly you go as long as you do not stop.",
     "ko": "멈추지 않는 한, 얼마나 천천히 가든 상관없다. - Confucius"},
    {"en": "Believe you can and you are halfway there.",
     "ko": "할 수 있다고 믿으면 이미 절반은 온 것이다. - Theodore Roosevelt"},
    {"en": "Your limitation is only your imagination.",
     "ko": "당신의 한계는 오직 상상력뿐이다."},
]

MARKET_SYMBOLS = [
    {"symbol": "^KS11", "name": "KOSPI"},
    {"symbol": "^KQ11", "name": "KOSDAQ"},
    {"symbol": "^GSPC", "name": "S&P 500"},
    {"symbol": "^IXIC", "name": "NASDAQ"},
    {"symbol": "^DJI",  "name": "DOW"},
]


def get_kst_now():
    return datetime.now(timezone(timedelta(hours=9)))


def pick_of_day(items, now):
    return items[now.timetuple().tm_yday % len(items)]


def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def build_todo_html(items):
    return "\n    ".join("<li>" + item + "</li>" for item in items)


def fetch_stock_chips():
    if not HAS_YF:
        return '<div class="market-chip"><div class="m-name">증시</div><div class="m-value">-</div><div class="m-change flat">yfinance 미설치</div></div>'

    chips = []
    for item in MARKET_SYMBOLS:
        try:
            hist = yf.Ticker(item["symbol"]).history(period="2d")
            if len(hist) < 1:
                raise ValueError("no data")
            close = float(hist["Close"].iloc[-1])
            if len(hist) >= 2:
                prev = float(hist["Close"].iloc[-2])
                diff = close - prev
                pct  = diff / prev * 100.0
            else:
                diff = pct = 0.0

            sign = "+" if diff > 0 else ("-" if diff < 0 else "")
            css  = "up"  if diff > 0 else ("down" if diff < 0 else "flat")
            change_s = sign + "{:.2f}".format(abs(diff)) + " (" + "{:.2f}".format(abs(pct)) + "%)"

            chips.append(
                '<div class="market-chip">'
                + '<div class="m-name">' + item["name"] + '</div>'
                + '<div class="m-value">' + "{:,.2f}".format(close) + '</div>'
                + '<div class="m-change ' + css + '">' + change_s + '</div>'
                + '</div>'
            )
        except Exception as e:
            chips.append(
                '<div class="market-chip">'
                + '<div class="m-name">' + item["name"] + '</div>'
                + '<div class="m-value">-</div>'
                + '<div class="m-change flat">데이터 없음</div>'
                + '</div>'
            )
            print("warning: " + item["name"] + " - " + str(e))
    return "\n    ".join(chips)


def main():
    now    = get_kst_now()
    config = load_config()

    updated_date = now.strftime("%Y년 %m월 %d일 %H:%M KST")

    # 영어 문장: config 우선, 없으면 자동 순환
    if config.get("quote_override_en"):
        quote_en = config["quote_override_en"]
        quote_ko = config.get("quote_override_ko", "")
    else:
        q = pick_of_day(QUOTES, now)
        quote_en = q["en"]
        quote_ko = q["ko"]

    # 운동
    workout_id  = config.get("workout_id",  "kc9QW75eMmg")
    workout_url = config.get("workout_url", "https://youtu.be/" + workout_id)
    embed       = "https://www.youtube-nocookie.com/embed/" + workout_id

    # Todo
    todo_items = config.get("todo", ["할 일을 config.json에서 편집하세요"])
    todo_html  = build_todo_html(todo_items)

    # 증시
    print("증시 데이터 수집 중...")
    stock_chips = fetch_stock_chips()

    # template.html 읽기 -> index.html 쓰기
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{UPDATED_DATE}}",  updated_date)
    html = html.replace("{{QUOTE_EN}}",      quote_en)
    html = html.replace("{{QUOTE_KO}}",      quote_ko)
    html = html.replace("{{YOUTUBE_EMBED}}", embed)
    html = html.replace("{{YOUTUBE_URL}}",   workout_url)
    html = html.replace("{{TODO_ITEMS}}",    todo_html)
    html = html.replace("{{STOCK_CHIPS}}",   stock_chips)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("완료: " + updated_date)
    print("문장: " + quote_en[:50])
    print("운동: " + workout_url)


if __name__ == "__main__":
    main()
