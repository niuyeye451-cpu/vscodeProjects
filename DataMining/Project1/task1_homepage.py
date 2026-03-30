import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--start-maximized") # 窗口最大化，确保显示桌面版导航栏
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def get_category_links():
    driver = init_driver()
    url = "https://www.asos.com/"
    
    try:
        print(f"正在访问 ASOS 首页: {url}")
        driver.get(url)
        
        # 等待页面 body 渲染完成
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2) 
        
        # 寻找所有的 a 标签，使用特征匹配，极其稳定
        links = driver.find_elements(By.TAG_NAME, "a")
        women_link, men_link = None, None
        
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            if href.endswith("/women/") or href == "https://www.asos.com/women":
                women_link = href
            elif href.endswith("/men/") or href == "https://www.asos.com/men":
                men_link = href
            if women_link and men_link:
                break

        print("=========================================")
        print(f"✅ 女装频道: {women_link}")
        print(f"✅ 男装频道: {men_link}")
        print("=========================================")

        with open("categories.txt", "w", encoding="utf-8") as f:
            if women_link: f.write(f"Women,{women_link}\n")
            if men_link: f.write(f"Men,{men_link}\n")

    except Exception as e:
        print(f"获取失败: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_category_links()