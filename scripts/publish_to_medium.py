import time
import os
import markdown
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # 引入 TimeoutException

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

# 登錄 Medium（使用 Google 登入）
def login_medium(driver, username, password):
    driver.get('https://accounts.google.com/v3/signin/identifier?operation=login&state=google-%7Chttps%3A%2F%2Fmedium.com%2F%3Fsource%3Dlogin-------------------------------------%7Clogin&access_type=online&client_id=216296035834-k1k6qe060s2tp2a2jam4ljdcms00sttg.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fmedium.com%2Fm%2Fcallback%2Fgoogle&response_type=id_token%20token&scope=email%20openid%20profile&nonce=2b974c18ed8dcb1d7be8729ab2b89fee3c951fc87930890d5c769cfec48c9ae7&service=lso&o2v=1&ddm=1&flowName=GeneralOAuthFlow&continue=https%3A%2F%2Faccounts.google.com%2Fsignin%2Foauth%2Fconsent%3Fauthuser%3Dunknown%26part%3DAJi8hAM2EJOM7xYshoZ_OdwMk8YULAFHzS12rBtay4Jx-hLWpgCvesL9psCbganmnxsLDTYZjNO_de2S5KmIl7lgmxZBjuacQp0olI0VwlIZ-34mQA05zDdOOd2IEPo8o8SdJbnzUeLUzkjPpnT460Lk8_dPbLeJm_nXr6AQh1Pc2Oyov1Ia5FDytY1QXFsYPY0lw-ziLfzm_4Ggg-ZW5GIPheE5XSOVyPX5f96Sn1ntm5C2Tr4FP08qC47Bg23A0Y546gLhNs91xrrJf-WeiSMW4tZNJOensAKQb5cMutyGIn_vXQji9ucpjpLN6Xr4drrLyIGZ17AFjZ6gRys6C2AzGmbpdTAK9PnNJpiCchoMBkxpmzk0H-vQcmOC329NTiCZUqi8ktNnIDX7TAS4PG3hdEMzgd85T--XDcP0gPpLs4lsJCcHe-UrZrLSlQgxMaeFCHOF0UaBkkFwqYVfdeJGxHKgEHPwMw%26flowName%3DGeneralOAuthFlow%26as%3DS-986635725%253A1730967845042370%26client_id%3D216296035834-k1k6qe060s2tp2a2jam4ljdcms00sttg.apps.googleusercontent.com%23')

    # 增加超長等待時間，給予更多時間
    try:
        # 等待 Gmail 用戶名輸入框出現，增加等待時間
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, 'identifier')))
        # 輸入 Gmail 用戶名
        driver.find_element(By.NAME, 'identifier').send_keys(username)
        driver.find_element(By.ID, 'identifierNext').click()

        # 等待 Gmail 密碼頁面
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, 'password')))
        # 輸入密碼
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.ID, 'passwordNext').click()

        # 確認是否完成登入，等待跳轉
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"]')))
    except TimeoutException as e:
        print(f"Error: {e}")
        driver.quit()
        raise Exception("Failed to log in due to timeout.")
    time.sleep(5)  # 等待頁面完成載入

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
