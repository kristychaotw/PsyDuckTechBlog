import time
import os
import markdown
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# 從 Markdown 檔案讀取內容
def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# 配置 Chrome 以便運行 Headless 模式
def create_chrome_driver():
    options = Options()
    options.add_argument('--headless')  # 開啟無頭模式
    options.add_argument('--disable-gpu')  # 禁用 GPU，避免影響渲染
    options.add_argument('--no-sandbox')  # 避免在無頭模式下出現問題
    options.add_argument('start-maximized')
    
    service = Service('/usr/bin/chromedriver')  # 如果你使用的是預設的 chromedriver 路徑
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

# 登錄 Medium
def login_medium(driver, username, password):
    driver.get('https://medium.com/m/signin')
    
    # 等待頁面載入
    time.sleep(3)
    
    # 填寫 Medium 用戶名和密碼
    driver.find_element(By.NAME, 'email').send_keys(username)
    driver.find_element(By.NAME, 'password').send_keys(password)
    
    driver.find_element(By.CSS_SELECTOR, 'button[data-action="sign-in"]').click()
    
    # 等待登入完成
    time.sleep(5)

# 發佈文章到 Medium
def publish_article(driver, title, content):
    # 創建新文章
    driver.get('https://medium.com/new-story')
    time.sleep(5)

    # 點擊標題框並輸入標題
    title_input = driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]:nth-of-type(1)')
    title_input.send_keys(title)

    # 切換到正文編輯框
    content_input = driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]:nth-of-type(2)')
    content_input.send_keys(content)
    
    # 發佈文章
    publish_button = driver.find_element(By.XPATH, "//div[text()='Publish']")
    publish_button.click()
    time.sleep(5)

# 獲取指定資料夾中最新的 Markdown 檔案
def get_latest_markdown_file(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.md')]
    if not files:
        raise FileNotFoundError("資料夾中沒有找到 Markdown 檔案")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

# 主函式
def main():
    # 設置用戶名、密碼和 Markdown 文件的資料夾路徑
    username = os.getenv('MEDIUM_USERNAME')  # 透過環境變數取得 Medium 用戶名
    password = os.getenv('MEDIUM_PASSWORD')  # 透過環境變數取得 Medium 密碼
    folder_path = 'src/posts'  # Markdown 檔案資料夾路徑

    # 找到最新的 Markdown 檔案
    md_file_path = get_latest_markdown_file(folder_path)
    
    # 讀取 Markdown 內容
    md_content = read_markdown(md_file_path)
    
    # 使用 markdown2 模組將 Markdown 轉換為 HTML
    html_content = markdown.markdown(md_content)
    
    # 擷取文章的標題（假設標題位於 Markdown 的第一行）
    title = md_content.split('\n')[0].replace('# ', '')

    # 創建 Selenium WebDriver
    driver = create_chrome_driver()

    try:
        # 登入 Medium
        login_medium(driver, username, password)

        # 發佈文章
        publish_article(driver, title, html_content)
    finally:
        # 關閉瀏覽器
        driver.quit()

if __name__ == '__main__':
    main()
