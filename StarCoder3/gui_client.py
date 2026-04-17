import tkinter as tk
from tkinter import scrolledtext
import requests
import threading
import re

API_URL = "http://localhost:8888"

DARK_BG   = "#0d1117"
PANEL_BG  = "#161b22"
BORDER    = "#30363d"
TEXT      = "#c9d1d9"
BLUE      = "#58a6ff"
GREEN     = "#3fb950"
MUTED     = "#6e7681"
INPUT_BG  = "#21262d"
RED       = "#f85149"
CODE_FG   = "#79c0ff"


class StarCoderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("월평동이상목 StarCoder3")
        self.root.geometry("1280x840")
        self.root.configure(bg=DARK_BG)
        self.root.minsize(900, 640)

        self.history   = []
        self.temperature = tk.DoubleVar(value=0.2)
        self.max_tokens  = tk.IntVar(value=1024)
        self._sending    = False

        self._build_toolbar()
        self._build_main()
        self._check_server()

    # ──────────────────────────────────────────
    # Toolbar
    # ──────────────────────────────────────────
    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=PANEL_BG, pady=7, padx=14,
                       relief=tk.FLAT, bd=0)
        bar.pack(fill=tk.X)

        # 왼쪽: 상태
        self.dot = tk.Label(bar, text="●", fg=GREEN, bg=PANEL_BG,
                            font=("Segoe UI", 13))
        self.dot.pack(side=tk.LEFT, padx=(0, 5))

        self.status_lbl = tk.Label(bar, text="서버 확인 중...",
                                   fg=MUTED, bg=PANEL_BG,
                                   font=("Segoe UI", 9))
        self.status_lbl.pack(side=tk.LEFT, padx=(0, 24))

        # 오른쪽: 파라미터 + 초기화
        tk.Button(bar, text="대화 초기화", command=self._clear_history,
                  bg=INPUT_BG, fg=MUTED, relief=tk.FLAT,
                  font=("Segoe UI", 9), padx=10, pady=3,
                  cursor="hand2").pack(side=tk.RIGHT, padx=4)

        tk.Label(bar, text="최대 토큰:", fg=MUTED, bg=PANEL_BG,
                 font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=(16, 0))
        tk.Spinbox(bar, from_=64, to=4096, increment=64,
                   textvariable=self.max_tokens, width=6,
                   bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
                   relief=tk.FLAT, font=("Segoe UI", 9),
                   buttonbackground=BORDER).pack(side=tk.RIGHT, padx=(4, 0))

        tk.Label(bar, text="온도:", fg=MUTED, bg=PANEL_BG,
                 font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=(16, 0))
        tk.Spinbox(bar, from_=0.0, to=2.0, increment=0.1,
                   textvariable=self.temperature, width=5,
                   bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
                   relief=tk.FLAT, font=("Segoe UI", 9), format="%.1f",
                   buttonbackground=BORDER).pack(side=tk.RIGHT, padx=(4, 0))

    # ──────────────────────────────────────────
    # Main 3-panel layout
    # ──────────────────────────────────────────
    def _build_main(self):
        outer = tk.PanedWindow(self.root, orient=tk.VERTICAL,
                               bg=BORDER, sashwidth=5,
                               sashrelief=tk.FLAT, bd=0)
        outer.pack(fill=tk.BOTH, expand=True)

        # ── 상단: 입력 + 복사 (좌우 분할) ──
        top_pane = tk.PanedWindow(outer, orient=tk.HORIZONTAL,
                                  bg=BORDER, sashwidth=5,
                                  sashrelief=tk.FLAT, bd=0)
        outer.add(top_pane, minsize=220)

        self._build_input_panel(top_pane)
        self._build_copy_panel(top_pane)

        # ── 하단: 실행 결과 ──
        self._build_result_panel(outer)

    # ── Panel 1: 명령 입력 ──────────────────
    def _build_input_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG)
        parent.add(frame, minsize=340)

        self._section_label(frame, "① 명령 입력")

        self.input_box = tk.Text(
            frame, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
            relief=tk.FLAT, font=("Consolas", 11), wrap=tk.WORD,
            padx=10, pady=10, undo=True,
        )
        self.input_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))
        self.input_box.bind("<Control-Return>", lambda e: self._send())

        # 버튼 행
        btn_row = tk.Frame(frame, bg=PANEL_BG, pady=6, padx=8)
        btn_row.pack(fill=tk.X)

        self.send_btn = tk.Button(
            btn_row, text="전송  (Ctrl+Enter)", command=self._send,
            bg=BLUE, fg=DARK_BG, relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"), padx=14, pady=6,
            cursor="hand2",
        )
        self.send_btn.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row, text="입력 지우기",
            command=lambda: self.input_box.delete("1.0", tk.END),
            bg=INPUT_BG, fg=MUTED, relief=tk.FLAT,
            font=("Segoe UI", 9), padx=10, pady=6, cursor="hand2",
        ).pack(side=tk.LEFT)

        self.turn_lbl = tk.Label(btn_row, text="대화: 0턴",
                                 fg=MUTED, bg=PANEL_BG,
                                 font=("Segoe UI", 9))
        self.turn_lbl.pack(side=tk.RIGHT)

    # ── Panel 2: 결과 복사 ─────────────────
    def _build_copy_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG)
        parent.add(frame, minsize=280)

        hdr = tk.Frame(frame, bg=PANEL_BG)
        hdr.pack(fill=tk.X, padx=8)

        self._section_label(hdr, "② 결과 복사", side=tk.LEFT)

        self.copy_btn = tk.Button(
            hdr, text="클립보드 복사", command=self._copy_code,
            bg=INPUT_BG, fg=GREEN, relief=tk.FLAT,
            font=("Segoe UI", 9), padx=10, pady=3, cursor="hand2",
        )
        self.copy_btn.pack(side=tk.RIGHT, pady=6)

        self.copy_hint = tk.Label(
            frame,
            text="코드 블록(``` ```)이 자동 추출됩니다.\n없으면 전체 응답이 표시됩니다.",
            fg=MUTED, bg=PANEL_BG, font=("Segoe UI", 8),
            justify=tk.LEFT,
        )
        self.copy_hint.pack(anchor=tk.W, padx=10, pady=(0, 4))

        self.copy_box = tk.Text(
            frame, bg=DARK_BG, fg=CODE_FG, insertbackground=CODE_FG,
            relief=tk.FLAT, font=("Consolas", 11), wrap=tk.WORD,
            padx=10, pady=10, state=tk.DISABLED,
        )
        self.copy_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # ── Panel 3: 실행 결과 ────────────────
    def _build_result_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG)
        parent.add(frame, minsize=180)

        hdr = tk.Frame(frame, bg=PANEL_BG)
        hdr.pack(fill=tk.X, padx=8)

        self._section_label(hdr, "③ 실행 결과 (전체 AI 응답)", side=tk.LEFT)

        self.elapsed_lbl = tk.Label(hdr, text="", fg=MUTED, bg=PANEL_BG,
                                    font=("Segoe UI", 9))
        self.elapsed_lbl.pack(side=tk.RIGHT, pady=6)

        self.result_box = scrolledtext.ScrolledText(
            frame, bg=DARK_BG, fg=TEXT, insertbackground=TEXT,
            relief=tk.FLAT, font=("Consolas", 11), wrap=tk.WORD,
            padx=10, pady=10, state=tk.DISABLED,
        )
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # ──────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────
    def _section_label(self, parent, text, side=None):
        lbl = tk.Label(parent, text=text, fg=BLUE, bg=PANEL_BG,
                       font=("Segoe UI", 10, "bold"), pady=8)
        if side:
            lbl.pack(side=side)
        else:
            lbl.pack(anchor=tk.W, padx=8)
        return lbl

    def _set_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _extract_code(self, text):
        blocks = re.findall(r"```(?:\w*)\n?(.*?)```", text, re.DOTALL)
        if blocks:
            return "\n\n".join(b.strip() for b in blocks)
        return text.strip()

    # ──────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────
    def _send(self):
        if self._sending:
            return
        prompt = self.input_box.get("1.0", tk.END).strip()
        if not prompt:
            return

        self._sending = True
        self.send_btn.config(state=tk.DISABLED, text="생성 중...")
        self._set_text(self.result_box, "⏳ 생성 중입니다...")
        self._set_text(self.copy_box, "")
        self.elapsed_lbl.config(text="")

        def run():
            try:
                payload = {
                    "messages": self.history + [{"role": "user", "content": prompt}],
                    "temperature": self.temperature.get(),
                    "max_tokens": self.max_tokens.get(),
                }
                r = requests.post(f"{API_URL}/chat", json=payload, timeout=180)
                r.raise_for_status()
                data = r.json()
                response = data.get("response", "")
                elapsed  = data.get("elapsed_ms", 0)

                self.history.append({"role": "user",      "content": prompt})
                self.history.append({"role": "assistant", "content": response})

                code = self._extract_code(response)
                self.root.after(0, lambda: self._on_response(response, code, elapsed))
            except Exception as e:
                self.root.after(0, lambda: self._on_error(str(e)))
            finally:
                self.root.after(0, self._done_sending)

        threading.Thread(target=run, daemon=True).start()

    def _on_response(self, response, code, elapsed_ms):
        self._set_text(self.result_box, response)
        self._set_text(self.copy_box, code)
        self.elapsed_lbl.config(text=f"{elapsed_ms / 1000:.1f}초")
        turns = len(self.history) // 2
        self.turn_lbl.config(text=f"대화: {turns}턴")

    def _on_error(self, msg):
        self._set_text(self.result_box, f"오류: {msg}")
        self._set_text(self.copy_box, "")

    def _done_sending(self):
        self._sending = False
        self.send_btn.config(state=tk.NORMAL, text="전송  (Ctrl+Enter)")

    def _copy_code(self):
        text = self.copy_box.get("1.0", tk.END).strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.copy_btn.config(text="복사됨 ✓")
        self.root.after(2000, lambda: self.copy_btn.config(text="클립보드 복사"))

    def _clear_history(self):
        self.history = []
        self._set_text(self.result_box, "")
        self._set_text(self.copy_box, "")
        self.elapsed_lbl.config(text="")
        self.turn_lbl.config(text="대화: 0턴")

    # ──────────────────────────────────────────
    # Server health check (5초마다)
    # ──────────────────────────────────────────
    def _check_server(self):
        def check():
            try:
                r = requests.get(f"{API_URL}/health", timeout=3)
                data = r.json()
                model = data.get("model", "unknown")
                self.root.after(0, lambda: self._set_online(True, model))
            except Exception:
                self.root.after(0, lambda: self._set_online(False, ""))
            self.root.after(5000, self._check_server)

        threading.Thread(target=check, daemon=True).start()

    def _set_online(self, online, model):
        if online:
            self.dot.config(fg=GREEN)
            self.status_lbl.config(fg=MUTED,
                                   text=f"온라인  │  {model}")
        else:
            self.dot.config(fg=RED)
            self.status_lbl.config(fg=RED,
                                   text="서버 오프라인 — localhost:8888")


if __name__ == "__main__":
    root = tk.Tk()
    StarCoderGUI(root)
    root.mainloop()
