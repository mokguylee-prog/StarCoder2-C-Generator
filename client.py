"""StarCoder2 CLI 클라이언트"""
import sys
import json

try:
    import requests
except ImportError:
    print("설치 필요: pip install requests")
    sys.exit(1)

SERVER = "http://localhost:8888"

HELP = """
StarCoder2 클라이언트
=====================
사용법:
  python client.py generate   # 대화형 코드 완성
  python client.py fim        # 코드 중간 채우기
  python client.py health     # 서버 상태 확인
  python client.py demo       # 동작 확인 데모 실행
"""


def check_health():
    try:
        r = requests.get(f"{SERVER}/health", timeout=5)
        r.raise_for_status()
        data = r.json()
        print(f"서버 정상 — 모델: {data['model']}")
        return True
    except requests.ConnectionError:
        print(f"서버 연결 실패: {SERVER}")
        print("먼저 실행하세요: python server.py")
        return False
    except Exception as e:
        print(f"오류: {e}")
        return False


def cmd_generate():
    print("=== 코드 완성 모드 ===")
    print("부분 C 코드를 입력하세요. 빈 줄 두 번 입력하면 전송됩니다.")
    print("종료: Ctrl+C\n")

    while True:
        try:
            lines = []
            empty_count = 0
            while True:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                lines.append(line)

            prompt = "\n".join(lines).strip()
            if not prompt:
                continue

            print("\n생성 중...\n")
            r = requests.post(f"{SERVER}/generate", json={"prompt": prompt}, timeout=120)
            r.raise_for_status()
            data = r.json()
            print("─" * 50)
            print(data["generated"])
            print(f"─" * 50)
            print(f"[생성 토큰: {data['tokens_generated']}]\n")

        except KeyboardInterrupt:
            print("\n종료")
            break
        except requests.ConnectionError:
            print("서버 연결 끊김")
            break


def cmd_fim():
    print("=== FIM 모드 (코드 중간 채우기) ===\n")
    try:
        print("앞부분 코드 (빈 줄 두 번으로 완료):")
        prefix_lines = []
        empty = 0
        while True:
            line = input()
            if line == "":
                empty += 1
                if empty >= 2:
                    break
            else:
                empty = 0
            prefix_lines.append(line)

        print("\n뒷부분 코드 (빈 줄 두 번으로 완료):")
        suffix_lines = []
        empty = 0
        while True:
            line = input()
            if line == "":
                empty += 1
                if empty >= 2:
                    break
            else:
                empty = 0
            suffix_lines.append(line)

        prefix = "\n".join(prefix_lines).strip()
        suffix = "\n".join(suffix_lines).strip()

        print("\n생성 중...\n")
        r = requests.post(f"{SERVER}/fim", json={"prefix": prefix, "suffix": suffix}, timeout=120)
        r.raise_for_status()
        data = r.json()
        print("─" * 50)
        print("[채워진 중간 코드]")
        print(data["generated"])
        print("─" * 50)
        print(f"[생성 토큰: {data['tokens_generated']}]")

    except KeyboardInterrupt:
        print("\n취소")


def cmd_demo():
    """동작 확인용 데모 — 서버가 실행 중인지, 코드가 잘 생성되는지 확인"""
    print("=== 동작 확인 데모 ===\n")

    if not check_health():
        return

    tests = [
        {
            "name": "/generate — 팩토리얼",
            "endpoint": "/generate",
            "payload": {
                "prompt": "// Recursive factorial\nint factorial(int n) {\n    if (n <= 1)\n        return 1;\n",
                "max_tokens": 80,
            },
        },
        {
            "name": "/generate — 버블 정렬",
            "endpoint": "/generate",
            "payload": {
                "prompt": "void bubble_sort(int arr[], int n) {\n    for (int i = 0; i < n - 1; i++) {\n",
                "max_tokens": 120,
            },
        },
        {
            "name": "/fim — 배열 정렬 중간 채우기",
            "endpoint": "/fim",
            "payload": {
                "prefix": "int main() {\n    int arr[] = {5, 3, 1, 4, 2};\n    int n = 5;\n    // sort arr\n",
                "suffix": "    printf(\"%d\\n\", arr[0]);\n    return 0;\n}",
                "max_tokens": 80,
            },
        },
    ]

    passed = 0
    for t in tests:
        print(f"[테스트] {t['name']}")
        try:
            r = requests.post(f"{SERVER}{t['endpoint']}", json=t["payload"], timeout=120)
            r.raise_for_status()
            data = r.json()
            print(f"  생성 토큰: {data['tokens_generated']}")
            preview = data["generated"].replace("\n", " ")[:80]
            print(f"  결과 미리보기: {preview}...")
            print(f"  결과: PASS\n")
            passed += 1
        except Exception as e:
            print(f"  결과: FAIL — {e}\n")

    print(f"{'=' * 40}")
    print(f"결과: {passed}/{len(tests)} 통과")
    if passed == len(tests):
        print("서버 + 클라이언트 정상 동작 확인!")
    else:
        print("일부 테스트 실패. 서버 로그를 확인하세요.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "generate":
        if check_health():
            cmd_generate()
    elif cmd == "fim":
        if check_health():
            cmd_fim()
    elif cmd == "health":
        check_health()
    elif cmd == "demo":
        cmd_demo()
    else:
        print(HELP)
