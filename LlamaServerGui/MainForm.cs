using System.Diagnostics;
using System.Net.Http;
using Microsoft.Web.WebView2.WinForms;

namespace LlamaServerGui;

public sealed class MainForm : Form
{
    // 기본값 — UI에서 수정 가능
    private const string DefaultExePath = @"D:\llama.cpp\llama-server.exe";
    private const string DefaultModelPath = @"D:\StarCoder3\models\gguf\qwen2.5-coder-7b-instruct-q4_k_m.gguf";
    private const int DefaultPort = 8888;

    private readonly TabControl _tabControl;

    private readonly TextBox _exeBox;
    private readonly TextBox _modelBox;
    private readonly NumericUpDown _portBox;
    private readonly Button _startBtn;
    private readonly Button _stopBtn;
    private readonly Button _browserBtn;
    private readonly Label _statusLabel;
    private readonly TextBox _logBox;
    private readonly WebView2 _webView;

    private Process? _serverProcess;
    private bool _webViewReady;

    public MainForm()
    {
        Text = "llama.cpp 서버 런처";
        Width = 1100;
        Height = 800;
        StartPosition = FormStartPosition.CenterScreen;
        MinimumSize = new Size(820, 560);

        // ── 탭 컨트롤 ─────────────────────────────────────
        _tabControl = new TabControl
        {
            Dock = DockStyle.Fill,
            ItemSize = new Size(80, 30),
            Font = new Font("Segoe UI", 10f),
        };

        // 탭 1: 제어
        var controlTab = new TabPage { Text = "제어", Padding = new Padding(10) };
        var controlPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Top,
            ColumnCount = 4,
            RowCount = 4,
            Padding = new Padding(0),
            AutoSize = true,
            AutoSizeMode = AutoSizeMode.GrowAndShrink,
        };
        controlPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 95));
        controlPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        controlPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 70));
        controlPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 0));

        _exeBox = new TextBox { Text = DefaultExePath, Dock = DockStyle.Fill, Anchor = AnchorStyles.Left | AnchorStyles.Right };
        _modelBox = new TextBox { Text = DefaultModelPath, Dock = DockStyle.Fill, Anchor = AnchorStyles.Left | AnchorStyles.Right };
        _portBox = new NumericUpDown { Minimum = 1, Maximum = 65535, Value = DefaultPort, Dock = DockStyle.Fill };

        var exeBrowse = new Button { Text = "...", Dock = DockStyle.Fill };
        exeBrowse.Click += (_, _) => PickFile(_exeBox, "실행 파일 (*.exe)|*.exe|모든 파일 (*.*)|*.*");
        var modelBrowse = new Button { Text = "...", Dock = DockStyle.Fill };
        modelBrowse.Click += (_, _) => PickFile(_modelBox, "GGUF 모델 (*.gguf)|*.gguf|모든 파일 (*.*)|*.*");

        controlPanel.Controls.Add(new Label { Text = "서버 EXE", TextAlign = ContentAlignment.MiddleLeft, Dock = DockStyle.Fill }, 0, 0);
        controlPanel.Controls.Add(_exeBox, 1, 0);
        controlPanel.Controls.Add(exeBrowse, 2, 0);

        controlPanel.Controls.Add(new Label { Text = "모델", TextAlign = ContentAlignment.MiddleLeft, Dock = DockStyle.Fill }, 0, 1);
        controlPanel.Controls.Add(_modelBox, 1, 1);
        controlPanel.Controls.Add(modelBrowse, 2, 1);

        controlPanel.Controls.Add(new Label { Text = "포트", TextAlign = ContentAlignment.MiddleLeft, Dock = DockStyle.Fill }, 0, 2);
        controlPanel.Controls.Add(_portBox, 1, 2);

        // 버튼 줄
        var btnPanel = new FlowLayoutPanel { Dock = DockStyle.Fill, AutoSize = true, FlowDirection = FlowDirection.LeftToRight };
        _startBtn = new Button { Text = "서버 시작", Width = 110, Height = 30 };
        _stopBtn = new Button { Text = "서버 정지", Width = 110, Height = 30, Enabled = false };
        _browserBtn = new Button { Text = "브라우저로 열기", Width = 130, Height = 30, Enabled = false };
        _statusLabel = new Label { Text = "대기 중", AutoSize = true, TextAlign = ContentAlignment.MiddleLeft, Margin = new Padding(12, 8, 0, 0), ForeColor = Color.DimGray };
        _startBtn.Click += async (_, _) => await StartServerAsync();
        _stopBtn.Click += (_, _) => StopServer();
        _browserBtn.Click += (_, _) => OpenInBrowser();
        btnPanel.Controls.Add(_startBtn);
        btnPanel.Controls.Add(_stopBtn);
        btnPanel.Controls.Add(_browserBtn);
        btnPanel.Controls.Add(_statusLabel);
        controlPanel.Controls.Add(btnPanel, 0, 3);
        controlPanel.SetColumnSpan(btnPanel, 4);

        controlTab.Controls.Add(controlPanel);

        // 탭 2: 로그
        var logTab = new TabPage { Text = "로그", Padding = new Padding(10) };
        _logBox = new TextBox
        {
            Dock = DockStyle.Fill,
            Multiline = true,
            ReadOnly = true,
            ScrollBars = ScrollBars.Vertical,
            BackColor = Color.FromArgb(30, 30, 30),
            ForeColor = Color.Gainsboro,
            Font = new Font("Consolas", 9f),
        };
        logTab.Controls.Add(_logBox);

        // 탭 3: 브라우저
        var browserTab = new TabPage { Text = "브라우저", Padding = new Padding(0) };
        _webView = new WebView2 { Dock = DockStyle.Fill };
        browserTab.Controls.Add(_webView);

        // 탭 추가
        _tabControl.TabPages.Add(controlTab);
        _tabControl.TabPages.Add(logTab);
        _tabControl.TabPages.Add(browserTab);

        Controls.Add(_tabControl);

        Load += async (_, _) => await InitWebViewAsync();
        FormClosing += (_, _) => StopServer();
    }

    private async Task InitWebViewAsync()
    {
        try
        {
            await _webView.EnsureCoreWebView2Async();
            _webViewReady = true;
        }
        catch (Exception ex)
        {
            Log($"[WebView2 초기화 실패] {ex.Message}");
            Log("→ Edge WebView2 런타임이 필요할 수 있습니다. '브라우저로 열기'는 계속 사용 가능합니다.");
        }
    }

    private void PickFile(TextBox target, string filter)
    {
        using var dlg = new OpenFileDialog { Filter = filter };
        if (File.Exists(target.Text))
        {
            dlg.InitialDirectory = Path.GetDirectoryName(target.Text);
            dlg.FileName = Path.GetFileName(target.Text);
        }
        if (dlg.ShowDialog(this) == DialogResult.OK)
            target.Text = dlg.FileName;
    }

    private string ServerUrl => $"http://127.0.0.1:{(int)_portBox.Value}";

    private async Task StartServerAsync()
    {
        if (_serverProcess is { HasExited: false })
        {
            Log("이미 서버가 실행 중입니다.");
            return;
        }

        var exe = _exeBox.Text.Trim();
        var model = _modelBox.Text.Trim();
        var port = (int)_portBox.Value;

        if (!File.Exists(exe)) { Warn($"서버 EXE를 찾을 수 없습니다:\n{exe}"); return; }
        if (!File.Exists(model)) { Warn($"모델 파일을 찾을 수 없습니다:\n{model}"); return; }

        var args = $"--model \"{model}\" --ctx-size 8192 --threads 8 --n-gpu-layers 0 --host 127.0.0.1 --port {port}";

        var psi = new ProcessStartInfo
        {
            FileName = exe,
            Arguments = args,
            WorkingDirectory = Path.GetDirectoryName(exe) ?? Environment.CurrentDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
            StandardErrorEncoding = System.Text.Encoding.UTF8,
        };

        try
        {
            _serverProcess = new Process { StartInfo = psi, EnableRaisingEvents = true };
            _serverProcess.OutputDataReceived += (_, e) => { if (e.Data != null) Log(e.Data); };
            _serverProcess.ErrorDataReceived += (_, e) => { if (e.Data != null) Log(e.Data); };
            _serverProcess.Exited += (_, _) => BeginInvoke(OnServerExited);
            _serverProcess.Start();
            _serverProcess.BeginOutputReadLine();
            _serverProcess.BeginErrorReadLine();
        }
        catch (Exception ex)
        {
            Warn($"서버 실행 실패: {ex.Message}");
            _serverProcess = null;
            return;
        }

        _startBtn.Enabled = false;
        _stopBtn.Enabled = true;
        SetStatus("모델 로딩 중...", Color.DarkOrange);
        Log($"$ \"{exe}\" {args}");

        var healthy = await WaitForHealthAsync(port, TimeSpan.FromMinutes(3));
        if (!healthy)
        {
            SetStatus("기동 실패 (타임아웃)", Color.Firebrick);
            return;
        }

        SetStatus($"실행 중 — {ServerUrl}", Color.ForestGreen);
        _browserBtn.Enabled = true;

        if (_webViewReady)
        {
            try { _webView.CoreWebView2.Navigate(ServerUrl); }
            catch (Exception ex) { Log($"[웹뷰 이동 실패] {ex.Message}"); }
        }
    }

    private async Task<bool> WaitForHealthAsync(int port, TimeSpan timeout)
    {
        using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
        var url = $"http://127.0.0.1:{port}/health";
        var deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            if (_serverProcess is null || _serverProcess.HasExited) return false;
            try
            {
                using var resp = await http.GetAsync(url);
                if (resp.IsSuccessStatusCode) return true;
            }
            catch { /* 아직 준비 안 됨 */ }
            await Task.Delay(1000);
        }
        return false;
    }

    private void OpenInBrowser()
    {
        try
        {
            Process.Start(new ProcessStartInfo { FileName = ServerUrl, UseShellExecute = true });
        }
        catch (Exception ex)
        {
            Warn($"브라우저 열기 실패: {ex.Message}");
        }
    }

    private void StopServer()
    {
        var proc = _serverProcess;
        if (proc is null) return;
        try
        {
            if (!proc.HasExited)
            {
                proc.Kill(entireProcessTree: true);
                proc.WaitForExit(5000);
            }
        }
        catch { /* 이미 종료됨 */ }
        finally
        {
            _serverProcess = null;
        }
    }

    private void OnServerExited()
    {
        _serverProcess = null;
        _startBtn.Enabled = true;
        _stopBtn.Enabled = false;
        _browserBtn.Enabled = false;
        SetStatus("정지됨", Color.DimGray);
        Log("[서버 프로세스 종료됨]");
    }

    private void SetStatus(string text, Color color)
    {
        if (InvokeRequired) { BeginInvoke(() => SetStatus(text, color)); return; }
        _statusLabel.Text = text;
        _statusLabel.ForeColor = color;
    }

    private void Log(string line)
    {
        if (_logBox.IsDisposed) return;
        if (_logBox.InvokeRequired) { _logBox.BeginInvoke(() => Log(line)); return; }
        _logBox.AppendText(line + Environment.NewLine);
    }

    private void Warn(string msg)
    {
        Log(msg);
        MessageBox.Show(this, msg, "알림", MessageBoxButtons.OK, MessageBoxIcon.Warning);
    }
}
