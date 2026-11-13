"""draws.json 을 만들거나 갱신하는 스크립트 (동행복권 개편 후 새 주소 사용).
실행: python update_draws.py  (같은 폴더에 draws.json 이 생깁니다)
형식: [[회차, 번호1~6, 보너스], ...]
"""
import json
import os
import sys
import time
import urllib.request

URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchLtEpsd=all"
FILE = "draws.json"


def get_raw():
    # 파일 이름을 함께 입력하면 인터넷 대신 그 파일을 읽습니다.
    # 예: python update_draws.py raw.json
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8-sig") as f:
            return f.read()
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.dhlottery.co.kr/lt645/result",
        },
    )
    last = None
    for attempt in range(3):  # 일시적 오류 대비 최대 3번 시도
        try:
            with urllib.request.urlopen(req, timeout=30) as f:
                return f.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            print("재시도", attempt + 1, e)
            time.sleep(5)
    raise last


def fetch_all():
    raw = get_raw()
    try:
        items = json.loads(raw)["data"]["list"]
    except Exception:
        print("JSON이 아닌 응답을 받았어요. 응답 앞부분:")
        print(raw[:300])
        raise
    rows = []
    for it in items:
        nums = [int(it["tm%dWnNo" % i]) for i in range(1, 7)]
        bonus = int(it["bnsWnNo"])
        if len(set(nums)) == 6 and all(1 <= x <= 45 for x in nums + [bonus]):
            rows.append([int(it["ltEpsd"])] + nums + [bonus])
    return rows


def main():
    data = {}
    if os.path.exists(FILE):
        with open(FILE, encoding="utf-8") as f:
            for row in json.load(f):
                data[row[0]] = row

    try:
        new_rows = fetch_all()
    except Exception as e:
        print("실패:", e)
        sys.exit(1)  # 기존 draws.json 은 건드리지 않음

    if not new_rows:
        print("받은 데이터가 비어 있어요. 기존 파일은 그대로 둡니다.")
        sys.exit(1)

    for row in new_rows:
        data[row[0]] = row

    rows = [data[k] for k in sorted(data)]
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, separators=(",", ":"))
    print("총", len(rows), "회차 저장 (최신", rows[-1][0], "회)")


if __name__ == "__main__":
    main()
