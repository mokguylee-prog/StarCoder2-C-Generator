"""StarCoder2 대화형 클라이언트 — python client.py 로 바로 시작"""
import sys

try:
    import requests
except ImportError:
    print("설치 필요: pip install requests")
    sys.exit(1)

SERVER = "http://localhost:8888"

BANNER = """
╔══════════════════════════════════════════╗
║        StarCoder2  C 코드 생성기          ║
║  서버: http://localhost:8888              ║
╠══════════════════════════════════════════╣
║  부분 C 코드 입력 → 빈 줄로 전송          ║
║  :fim   FIM 모드 (중간 채우기)            ║
║  :gen   일반 생성 모드 (기본)             ║
║  :help  도움말                           ║
║  :quit  종료  (또는 Ctrl+C)              ║
╚══════════════════════════════════════════╝
"""

HELP = """명령어:
  :gen   일반 코드 완성 모드 (기본)
  :fim   FIM 모드 — 앞/뒤 코드를 주면 중간을 채워줌
  :help  이 도움말
  :quit  종료

입력 방법:
  - C 코드를 여러 줄 입력한 뒤 빈 줄(Enter)로 전송
  - :fim 모드에서는 prefix → 빈 줄 → suffix → 빈 줄 순으로 입력
"""


def call_generate(prompt: str) -> None:
    r = requests.post(f"{SERVER}/generate", json={"prompt": prompt}, timeout=120)
    r.raise_for_status()
    data = r.json()
    print("\n" + "─" * 52)
    print(data["generated"])
    print("─" * 52)
    print(f"[생성 토큰: {data['tokens_generated']}]\n")


def call_fim(prefix: str, suffix: str) -> None:
    r = requests.post(f"{SERVER}/fim", json={"prefix": prefix, "suffix": suffix}, timeout=120)
    r.raise_for_status()
    data = r.json()
    print("\n" + "─" * 52)
    print("[채워진 중간 코드]")
    print(data["generated"])
    print("─" * 52)
    print(f"[생성 토큰: {data['tokens_generated']}]\n")


def read_block(prompt_label: str) -> str:
    """빈 줄이 나올 때까지 여러 줄 입력을 받아 하나의 문자열로 반환."""
    print(prompt_label)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def check_server() -> bool:
    try:
        r = requests.get(f"{SERVER}/health", timeout=5)
        r.raise_for_status()
        model = r.json().get("model", "")
        print(f"서버 연결 확인 — 모델: {model}\n")
        return True
    except requests.ConnectionError:
        print(f"[오류] 서버에 연결할 수 없습니다: {SERVER}")
        print("먼저 실행하세요: .\\start_server.ps1\n")
        return False


def main():
    print(BANNER)

    if not check_server():
        sys.exit(1)

    mode = "gen"  # 현재 모드: "gen" 또는 "fim"

    while True:
        try:
            mode_tag = "[GEN]" if mode == "gen" else "[FIM]"
            line = input(f"{mode_tag} >>> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n종료합니다.")
            break

        if not line:
            continue

        # ── 명령어 처리 ──────────────────────────────
        if line == ":quit":
            print("종료합니다.")
            break
        elif line == ":help":
            print(HELP)
            continue
        elif line == ":gen":
            mode = "gen"
            print("모드 변경: 일반 코드 완성\n")
            continue
        elif line == ":fim":
            mode = "fim"
            print("모드 변경: FIM (코드 중간 채우기)\n")
            continue

        # ── 코드 입력 처리 ────────────────────────────
        try:
            if mode == "gen":
                # 첫 줄은 이미 입력받았으므로 이어서 나머지 줄 수집
                print("(계속 입력 → 빈 줄로 전송)")
                rest_lines = []
                while True:
                    try:
                        l = input()
                    except EOFError:
                        break
                    if l == "":
                        break
                    rest_lines.append(l)
                prompt = line + ("\n" + "\n".join(rest_lines) if rest_lines else "")
                print("생성 중...")
                call_generate(prompt)

            else:  # fim
                # 첫 줄 입력이 prefix 시작
                print("(prefix 계속 입력 → 빈 줄로 완료)")
                prefix_lines = [line]
                while True:
                    try:
                        l = input()
                    except EOFError:
                        break
                    if l == "":
                        break
                    prefix_lines.append(l)

                suffix = read_block("suffix 입력 (뒷부분 코드, 빈 줄로 완료):")
                print("생성 중...")
                call_fim("\n".join(prefix_lines), suffix)

        except requests.ConnectionError:
            print("[오류] 서버 연결이 끊겼습니다. 서버 상태를 확인하세요.\n")
        except requests.HTTPError as e:
            print(f"[오류] 서버 응답 오류: {e}\n")
        except Exception as e:
            print(f"[오류] {e}\n")


if __name__ == "__main__":
    main()
