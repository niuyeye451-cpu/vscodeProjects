# 文件名: task2_discount_dresses.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_discount_dresses_links(pages_to_scrape=2):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    # ASOS 女装折扣裙子分类的基础 URL
    base_url = "https://www.asos.com/women/sale/dresses/cat/?cid=5235"
    all_product_links = set()  # 使用 set 集合避免重复链接

    try:
        # 遍历需要抓取的页数 (默认抓取 1 到 2 页)
        for page in range(1, pages_to_scrape + 1):
            url = f"{base_url}&page={page}"
            print(f"正在访问第 {page} 页: {url}")
            driver.get(url)
            
            # 显式等待：等待商品卡片中的链接出现 (ASOS 商品链接固定包含 /prd/)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/prd/')]"))
            )
            
            # 模拟用户向下滚动，确保懒加载的商品块充分渲染
            for i in range(1, 4):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/4});")
                time.sleep(1)

            # 获取页面上所有包含 /prd/ (Product ID) 的 a 标签
            elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/prd/')]")
            page_links = set()
            
            for elem in elements:
                href = elem.get_attribute("href")
                if href and "/prd/" in href:
                    # 剥离 URL 中不必要的追踪参数(以?开头)，保留纯净商品链接
                    clean_href = href.split('?')[0]
                    page_links.add(clean_href)
                    all_product_links.add(clean_href)
            
            print(f"第 {page} 页成功提取到 {len(page_links)} 个商品链接。")
            
            # 礼貌性延迟，防止被封 IP
            time.sleep(3)

    except Exception as e:
        print(f"抓取过程中发生错误: {e}")
        driver.save_screenshot("error_task2.png")
        print("错误截图已保存为 error_task2.png")
    finally:
        driver.quit()

    # 将获取到的所有链接写入文件，供任务 1.3 使用
    print(f"\n抓取结束！总共获取到 {len(all_product_links)} 个打折裙装链接。")
    file_name = "dress_links.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        for link in all_product_links:
            f.write(link + "\n")
    print(f"所有商品链接已批量保存到当前目录下的 {file_name} 文件中。")

if __name__ == "__main__":
    # 在这里可以修改你想爬取的页数，当前设为 2 页
    get_discount_dresses_links(pages_to_scrape=2)