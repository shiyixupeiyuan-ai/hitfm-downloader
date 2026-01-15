📻 HITFM 节目自动下载器
自动从 中国广播网 下载 HITFM 节目，并直接使用真实节目标题命名文件（如 Music Flow 音乐流.m4a），无需手动重命名！

✨ 功能特点
✅ 自动提取真实节目标题（非 ID）
✅ 按日期批量下载（支持多日范围）
✅ 自动跳过“播放器区域”等干扰项
✅ 文件名安全处理（过滤非法字符）
✅ 临时调试文件自动清理
✅ 跨平台支持（Windows / macOS / Linux）

⚠️ 免责声明
本工具仅用于个人学习与节目存档，不得用于商业用途。
请遵守 中国广播网 的使用条款，尊重音频内容版权。
作者与 HITFM、中国广播网无任何关联。使用风险自负。

🛠️ 安装依赖
前提条件
已安装 Python 3.7+
已安装 Google Chrome 浏览器
安装步骤
克隆本仓库：
git clone https://github.com/yourname/hitfm-downloader.git
cd hitfm-downloader
pip install -r requirements.txt

💡 首次运行时，脚本会自动下载匹配的 chromedriver（需联网）。

⚙️ 使用方法
编辑 hitfm_downloader.py，修改顶部配置：
START_DATE = "2025-12-01"   # 开始日期（格式：YYYY-MM-DD）
END_DATE = "2025-12-01"     # 结束日期
CHANNEL_NAME = "662"        # HITFM 频道ID（勿改）
SAVE_BASE_DIR = "./HITFM_202512"  # 保存目录
运行脚本：
python hitfm_downloader.py
等待完成！节目将保存在：
./HITFM_202512/2025-12-01/Music Flow 音乐流.m4a

📁 项目结构
hitfm-downloader/
├── hitfm_downloader.py      # 主程序
├── requirements.txt         # 依赖列表
├── README.md                # 本说明文件
└── LICENSE                  # MIT 开源协议

📦 依赖说明
selenium	             控制浏览器自动化
webdriver-manager	       自动管理 ChromeDriver（无需手动下载）
beautifulsoup4	       解析 HTML 页面
requests	             下载音频文件
所有依赖均通过 pip install -r requirements.txt 安装。

❓ 常见问题
Q: 报错 chromedriver not found？
A: 确保已安装 Google Chrome。首次运行需联网自动下载驱动。
Q: 能否后台运行（不显示浏览器窗口）？
A: 可以！取消注释代码中的这一行：
# chrome_options.add_argument("--headless")
Q: 为什么有些节目没下载？
A: 可能当天无回放，或页面结构变化。可检查生成的 debug_*.html（临时文件，下载后自动删除）。

📜 许可证
本项目采用 MIT License —— 免费用于个人或商业项目，但请保留原作者信息。