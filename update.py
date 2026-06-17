"""
update.py - 매일 아침 9시(KST) GitHub Actions 자동 실행
"""

import random
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

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

WORKOUTS = [
    {"id": "kc9QW75eMmg", "url": "https://youtu.be/kc9QW75eMmg"},
]

TODO_ITEMS = [
    "Manus 사용 확인",
    "앱스크립트 완성 연결 공유",
    "가치놀이터 사이트 구성 체크",
    "강의안 확인",
]

MARKET_SYMBOLS = [
    {"symbol": "^KS11", "name": "KOSPI"},
    {"symbol": "^KQ11", "name": "KOSDAQ"},
    {"symbol": "^GSPC", "name": "S&P 500"},
    {"symbol": "^IXIC", "name": "NASDAQ"},
    {"symbol": "^DJI",  "name": "DOW"},
]


def get_kst_now():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst)


def pick_of_day(items, now):
    idx = now.timetuple().tm_yday % len(items)
    return items[idx]


def build_todo_html(items):
    parts = []
    for item in items:
        parts.append("<li>" + item + "</li>")
    return "\n    ".join(parts)


def fetch_stock_chips():
    if not HAS_YF:
        return '<div class="market-chip"><div class="m-name">증시</div><div class="m-value">-</div><div class="m-change flat">yfinance 미설치</div></div>'

    chips = []
    for item in MARKET_SYMBOLS:
        try:
            ticker = yf.Ticker(item["symbol"])
            hist = ticker.history(period="2d")
            if len(hist) < 1:
                raise ValueError("no data")
            close = float(hist["Close"].iloc[-1])
            if len(hist) >= 2:
                prev = float(hist["Close"].iloc[-2])
                diff = close - prev
                pct  = diff / prev * 100.0
            else:
                diff = 0.0
                pct  = 0.0

            if diff > 0:
                sign = "+"
                css  = "up"
            elif diff < 0:
                sign = "-"
                css  = "down"
            else:
                sign = ""
                css  = "flat"

            val_s    = "{:,.2f}".format(close)
            diff_s   = "{:.2f}".format(abs(diff))
            pct_s    = "{:.2f}".format(abs(pct))
            change_s = sign + diff_s + " (" + pct_s + "%)"

            chip = (
                '<div class="market-chip">'
                + '<div class="m-name">' + item["name"] + '</div>'
                + '<div class="m-value">' + val_s + '</div>'
                + '<div class="m-change ' + css + '">' + change_s + '</div>'
                + '</div>'
            )
            chips.append(chip)

        except Exception as e:
            chip = (
                '<div class="market-chip">'
                + '<div class="m-name">' + item["name"] + '</div>'
                + '<div class="m-value">-</div>'
                + '<div class="m-change flat">데이터 없음</div>'
                + '</div>'
            )
            chips.append(chip)
            print("warning: " + item["name"] + " - " + str(e))

    return "\n    ".join(chips)


def main():
    now = get_kst_now()
    updated_date = now.strftime("%Y년 %m월 %d일 %H:%M KST")

    quote   = pick_of_day(QUOTES, now)
    workout = pick_of_day(WORKOUTS, now)
    embed   = "https://www.youtube-nocookie.com/embed/" + workout["id"]
    url     = workout["url"]
    todo    = build_todo_html(TODO_ITEMS)

    print("증시 데이터 수집 중...")
    stock_chips = fetch_stock_chips()

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{UPDATED_DATE}}",  updated_date)
    html = html.replace("{{QUOTE_EN}}",      quote["en"])
    html = html.replace("{{QUOTE_KO}}",      quote["ko"])
    html = html.replace("{{YOUTUBE_EMBED}}", embed)
    html = html.replace("{{YOUTUBE_URL}}",   url)
    html = html.replace("{{TODO_ITEMS}}",    todo)
    html = html.replace("{{STOCK_CHIPS}}",   stock_chips)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("완료: " + updated_date)
    print("문장: " + quote["en"][:50])
    print("운동: " + url)


if __name__ == "__main__":
    main()
