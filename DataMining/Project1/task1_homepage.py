# 文件名: task1_homepage.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_gender_category_links():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    print("正在启动浏览器...")
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        url = "https://www.asos.com/?msockid=2d90c08b12236dc60338d64a13696caf"
        print(f"正在访问 ASOS 首页: {url}")
        driver.get(url)

        # 只要页面主体 body 加载出来即可
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("页面加载完成，正在提取男女装链接...")
        time.sleep(2) # 稍微等待页面 JS 渲染
        
        # 获取所有链接，通过特征精确匹配，这样不管是分流页还是标准首页都能兼容
        links = driver.find_elements(By.TAG_NAME, "a")
        women_link, men_link = None, None
        
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            
            # 匹配特征："https://www.asos.com/women/"
            if href.endswith("/women/") or href == "https://www.asos.com/women":
                women_link = href
            elif href.endswith("/men/") or href == "https://www.asos.com/men":
                men_link = href
                
            # 两个都找到就可以提前结束循环
            if women_link and men_link:
                break

        print("=========================================")
        if women_link:
            print(f"成功获取 女装(Women) 链接: {women_link}")
        else:
            print("未找到女装链接")
            
        if men_link:
            print(f"成功获取 男装(Men) 链接: {men_link}")
        else:
            print("未找到男装链接")
        print("=========================================")

        return women_link, men_link

    except Exception as e:
        print(f"抓取过程中发生错误: {e}")
        driver.save_screenshot("error_screenshot.png")
    finally:
        time.sleep(2)
        driver.quit()
        print("浏览器已关闭。")

if __name__ == "__main__":
    get_gender_category_links()