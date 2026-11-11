"""draws.json 을 만들고 새 회차만 이어서 추가하는 스크립트.
실행: python update_draws.py  (같은 폴더에 draws.json 이 생깁니다)
형식: [[회차, 번호1~6, 보너스], ...]
"""
import datetime
import json
import os
import time
import urllib.request

API = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}"
FILE = "draws.json"


def latest_round():
    start = datetime.date(2002, 12, 7)  # 1회차 (토)
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    days = (now.date() - start).days
    r = days // 7 + 1
    if days % 7 == 0 and now.hour < 22:  # 추첨일 밤 10시 전
        r -= 1
    return r


def fetch(n):
    req = urllib.request.Request(API.format(n), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as f:
        j = json.loads(f.read().decode("utf-8"))
    if j.get("returnValue") != "success":
        return None
    return [n] + [j["drwtNo%d" % i] for i in range(1, 7)] + [j["bnusNo"]]


def main():
    data = {}
    if os.path.exists(FILE):
        with open(FILE, encoding="utf-8") as f:
            for row in json.load(f):
                data[row[0]] = row

    for n in range(1, latest_round() + 1):
        if n in data:
            continue
        try:
            row = fetch(n)
        except Exception as e:  # 실패한 회차는 다음 실행 때 다시 시도
            print("실패", n, e)
            continue
        if row:
            data[n] = row
            print("추가", n)
        time.sleep(0.3)

    rows = [data[k] for k in sorted(data)]
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, separators=(",", ":"))
    print("총", len(rows), "회차 저장")


if __name__ == "__main__":
    main()
