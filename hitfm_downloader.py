import os
import re
import time
from datetime import datetime, timedelta

# Selenium 相关
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # 自动管理驱动

# 其他
from bs4 import BeautifulSoup

# ================== 配置 ==================
DEFAULT_CONFIG = {
    "START_DATE": "2025-11-01",
    "END_DATE": "2025-11-30",
    "CHANNEL_NAME": "662",
    "SAVE_BASE_DIR": "./HITFM_202512"
}

CONFIG = DEFAULT_CONFIG.copy()
config_path = os.path.join(os.path.dirname(__file__), 'config.py')
if os.path.exists(config_path):
    try:
        # 动态执行 config.py
        with open(config_path, 'r', encoding='utf-8') as f:
            config_code = compile(f.read(), 'config.py', 'exec')
            exec(config_code, CONFIG)
    except Exception as e:
        print(f"⚠️  加载 config.py 失败: {e}")

# 解包到全局变量（供后续代码使用）
START_DATE = CONFIG.get("START_DATE", DEFAULT_CONFIG["START_DATE"])
END_DATE = CONFIG.get("END_DATE", DEFAULT_CONFIG["END_DATE"])
CHANNEL_NAME = CONFIG.get("CHANNEL_NAME", DEFAULT_CONFIG["CHANNEL_NAME"])
SAVE_BASE_DIR = CONFIG.get("SAVE_BASE_DIR", DEFAULT_CONFIG["SAVE_BASE_DIR"])        
# ==========================================

def get_date_range(start, end):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    while start_dt <= end_dt:
        yield start_dt.strftime("%Y-%m-%d")
        start_dt += timedelta(days=1)

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip() or "Unknown"

def extract_programs_from_rendered_page(soup):
    """
    从渲染后的页面中自动提取节目名称和ID（兼容两种格式）
    返回：[(title, prog_id, id_type), ...]
    id_type: 1=16位数字ID（新版），2=32位字符+数字ID（旧版）
    """
    programs = []
    
    # 查找所有包含 downLiveRecord 的 <a> 标签
    all_links = soup.find_all("a", href="javascript:;")
    
    for link in all_links:
        onclick = link.get("onclick", "")
        
        # 跳过不包含 downLiveRecord 的链接
        if "downLiveRecord" not in onclick:
            continue
        
        # === 提取 ID 和标题 ===
        prog_id = None
        title = None
        id_type = 0  # 0=未识别，1=新版，2=旧版
        
        # 方法：解析 onclick="downLiveRecord('url','title');"
        try:
            # 去掉开头的 downLiveRecord(
            if onclick.startswith("downLiveRecord("):
                args_part = onclick[14:-2]  # 去掉 "downLiveRecord(" 和 ");"
            else:
                start = onclick.find("downLiveRecord(")
                if start == -1:
                    continue
                inner = onclick[start + 14:]
                end = inner.find(");")
                if end == -1:
                    continue
                args_part = inner[:end]
            
            parts = args_part.split("','")
            if len(parts) >= 2:
                url_part = parts[0].lstrip("'")
                title_part = parts[-1].rstrip("'")
                
                # 先匹配新版（16位以上数字ID）
                id_match_v1 = re.search(r'/(\d{16,})\.m4a', url_part)
                if id_match_v1:
                    prog_id = id_match_v1.group(1)
                    id_type = 1
                else:
                    # 匹配旧版（32位字符+数字ID）
                    id_match_v2 = re.search(r'/([a-f0-9]{32}_\d+)\.m4a', url_part)
                    if id_match_v2:
                        prog_id = id_match_v2.group(1)
                        id_type = 2
                
                # 仅保留识别到ID的节目
                if prog_id and title_part.strip() and 'undefined' not in title_part:
                    title = title_part.strip()
                    programs.append((title, prog_id, id_type))
                    print(f"  🔍 发现节目: {title} | ID: {prog_id} | 类型: {'新版' if id_type==1 else '旧版'}")
        except Exception as e:
            print(f"  ⚠️ 解析 onclick 失败: {str(e)}")
            continue
    
    # 去重（按 ID）
    seen = set()
    unique = []
    for title, pid, id_type in programs:
        if pid not in seen:
            unique.append((title, pid, id_type))
            seen.add(pid)
    return unique

def main():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--headless")  # 调试成功后再启用

    print("🔧 启动浏览器（自动识别ID类型）...")
    
    # 指定本地 chromedriver 路径
    driver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
    service = Service(executable_path=driver_path)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        for date_str in get_date_range(START_DATE, END_DATE):
            print(f"\n📅 处理日期: {date_str}")
            formatted_date = date_str.replace("-", "/")
            page_url = (
                f"https://www.radio.cn/pc-portal/sanji/passProgram.html"
                f"?channel_name={CHANNEL_NAME}"
                f"&date_checked={formatted_date}"
                f"&title=cate"
            )

            driver.get(page_url)
            print("  ⏳ 等待页面加载...")
            time.sleep(5)

            # 保存渲染后 HTML 供调试
            debug_file = f"debug_{date_str}.html"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"  💾 已保存调试文件: {debug_file}")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            programs = extract_programs_from_rendered_page(soup)

            if not programs:
                print("  ⚠️ 未找到有效节目")
                # 即使没节目也删调试文件
                if os.path.exists(debug_file):
                    os.remove(debug_file)
                    print(f"  🗑️ 已删除空调试文件: {debug_file}")
                continue

            date_folder = os.path.join(SAVE_BASE_DIR, date_str)
            os.makedirs(date_folder, exist_ok=True)

            for title, prog_id, id_type in programs:
                # 根据自动识别的ID类型匹配下载链接
                if id_type == 1:
                    # 新版ID下载链接
                    audio_url = f"https://ytrecordbroadcast.radio.cn/echo/2/{prog_id}.m4a?e=0&ps=1&r=3"
                elif id_type == 2:
                    # 旧版ID下载链接
                    audio_url = f"https://ytcmsplayer.radio.cn/content/video/vod/{formatted_date}/{prog_id}.m4a"
                else:
                    print(f"  ❌ 无法识别 {title} 的ID类型，跳过下载")
                    continue

                filename = safe_filename(title) + ".m4a"
                filepath = os.path.join(date_folder, filename)

                if os.path.exists(filepath):
                    print(f"  ➡️ 已存在: {title}")
                    continue

                print(f"  📥 下载: {title}")
                try:
                    import requests
                    resp = requests.get(
                        audio_url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            "Referer": "https://www.radio.cn/"
                        },
                        stream=True,
                        timeout=(10, 30)
                    )
                    print(f"  🌐 HTTP 状态码: {resp.status_code}")
                    
                    if resp.status_code == 200:
                        with open(filepath, "wb") as f:
                            for chunk in resp.iter_content(8192):
                                f.write(chunk)
                        print(f"  ✅ 成功: {filename}")
                    else:
                        print(f"  ❌ 服务器返回: {resp.status_code}")
                        
                except Exception as e:
                    print(f"  💥 下载失败: {e}")

                time.sleep(0.5)

            # 下载完成后删除调试文件
            if os.path.exists(debug_file):
                os.remove(debug_file)
                print(f"  🗑️ 已删除调试文件: {debug_file}")

    finally:
        print("\n🚪 关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()
