# 文件名: task3_product_details.py
import time
import re
import os
import datetime
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_product_details(max_items=3):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    txt_file_path = os.path.join(script_dir, "dress_links.txt")
    output_file_path = os.path.join(script_dir, "product.txt")

    try:
        with open(txt_file_path, "r", encoding="utf-8") as f:
            links =[line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"未找到 {txt_file_path}")
        return

    if not links:
        return

    links_to_scrape = links[:max_items]
    print(f"本次测试将抓取前 {len(links_to_scrape)} 个商品，输出 TXT 并下载图片...\n")

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 加入常见的浏览器 User-Agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    with open(output_file_path, "w", encoding="utf-8") as out_f:
        
        for index, url in enumerate(links_to_scrape):
            print(f"[{index+1}/{len(links_to_scrape)}] 正在解析: {url}")
            driver.get(url)
            
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                
                # 1. URL ID (作为商品编码)
                url_id_match = re.search(r'/prd/(\d+)', url)
                url_product_id = url_id_match.group(1) if url_id_match else f"unknown_{index}"
                
                # 2. 面包屑 Breadcrumbs
                try:
                    breadcrumbs = driver.find_elements(By.XPATH, "//nav[@aria-label='breadcrumbs']//ol/li")
                    breadcrumb_text = " > ".join([b.text.strip() for b in breadcrumbs if b.text.strip()])
                except:
                    breadcrumb_text = "Home > Women > Dresses"
                
                # 3. 标志位 1
                flag_1 = "1"
                
                # 4. 提取描述与内部 Product Code
                desc_text = driver.execute_script("""
                    let containers =[
                        document.getElementById('productDescriptionDetails'),
                        document.getElementById('productDetails'),
                        document.querySelector('[data-testid="productDescription"]')
                    ];
                    for(let c of containers) {
                        if(c && c.innerText.trim().length > 10) return c.innerText;
                    }
                    return "";
                """)
                
                internal_code = "N/A"
                if desc_text:
                    code_match = re.search(r'Product Code:\s*(\d+)', desc_text, re.IGNORECASE)
                    if code_match:
                        internal_code = code_match.group(1)
                
                # 5. 主域名 & 标志位 0
                domain = "http://www.asos.com/"
                flag_0 = "0"
                
                # 6. Title 和 Brand
                title = driver.find_element(By.TAG_NAME, "h1").text.strip()
                brand = "N/A"
                if desc_text:
                    brand_match = re.search(r'Brand\s*[:\-]?\s*([A-Za-z0-9\s&]+)', desc_text, re.IGNORECASE)
                    if brand_match and len(brand_match.group(1)) < 30:
                        brand = brand_match.group(1).strip()
                if brand == "N/A" or "Product Code" in brand:
                    words = title.split()
                    brand = f"{words[0]} {words[1]}" if words[0].upper() == "ASOS" else words[0]
                
                # 7. 爬取时间戳
                scrape_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 8. 价格信息
                try:
                    price_wrap = driver.find_element(By.XPATH, "//*[@data-testid='price-wrap']")
                    price_string = price_wrap.text.replace('\n', ' ').strip()
                except:
                    price_string = "Price not found"
                
                # 9. 尺码列表
                try:
                    size_options = driver.find_elements(By.XPATH, "//select[@id='main-size-select']/option | //div[@data-testid='size-select']//option")
                    sizes =[opt.text.split('-')[0].strip() for opt in size_options if 'Select' not in opt.text and opt.text.strip()]
                    sizes_str = ";".join(sizes) + ";" if sizes else "Sizes not found"
                except:
                    sizes_str = "Sizes not found"

                clean_desc = desc_text.replace('Product Code', '\nProduct Code').strip() if desc_text else "No description"
                full_description = f"product description: {clean_desc}\n{sizes_str}"

                # 10. Color
                color = "N/A"
                if desc_text:
                    color_match = re.search(r'Colou?r\s*[:\-]?\s*([A-Za-z\s]+)', desc_text, re.IGNORECASE)
                    if color_match and len(color_match.group(1)) < 20:
                        color = color_match.group(1).strip()
                if color == "N/A":
                    color_from_title = re.search(r'\s+in\s+([a-zA-Z\s]+)$', title, re.IGNORECASE)
                    if color_from_title:
                        color = color_from_title.group(1).strip()
                        
                # ================= 11. 提取并下载图片 (完全采用老师逻辑) =================
                img_url_list =[]
                img_number = 0
                
                try:
                    # 使用老师的 XPath 提取逻辑，稍微加了 contains 防止 class 变动
                    ele_imgs = driver.find_elements(By.XPATH, "//img[@class='gallery-image'] | //img[contains(@class, 'gallery-image')] | //img[@data-testid='gallery-image']")
                    for ele in ele_imgs:
                        src = ele.get_attribute("src")
                        if src:
                            img_url_list.append(src)  # 直接保留真实链接，不去掉参数
                            
                    img_url_list = list(set(img_url_list)) # 去重
                    
                    if img_url_list:
                        # 拼接你的要求目录：product-images/商品编码/.images/
                        img_folder = os.path.join(script_dir, "product-images", str(url_product_id), ".images")
                        os.makedirs(img_folder, exist_ok=True)
                        
                        print(f"  -> 找到 {len(img_url_list)} 张图片，正在下载至 {img_folder} ...")
                        
                        # 下载图片
                        for i, img_url in enumerate(img_url_list):
                            try:
                                # 极其重要：必须伪装 Headers，否则 ASOS 会直接拒绝访问导致报错！
                                req = urllib.request.Request(img_url, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                                    'Referer': 'https://www.asos.com/'
                                })
                                with urllib.request.urlopen(req, timeout=15) as response:
                                    img_path = os.path.join(img_folder, f"{i+1}.jpg")
                                    with open(img_path, 'wb') as img_file:
                                        img_file.write(response.read())
                                        img_number += 1
                            except Exception as dl_e:
                                print(f"    -> 图片 {i+1} 下载失败: {dl_e}")
                except Exception as img_e:
                    print(f"  -> 图片提取解析失败: {img_e}")
                
                # ================= 12. 按格式写入文本 =================
                out_f.write(f"{url_product_id}\n")
                out_f.write(f"{breadcrumb_text}\n")
                out_f.write(f"{url}\n")
                out_f.write(f"{flag_1}\n")
                out_f.write(f"Product Code: {internal_code}\n")
                out_f.write(f"{domain}\n")
                out_f.write(f"{flag_0}\n")
                out_f.write(f"{brand}\n")
                out_f.write(f"{scrape_time}\n")
                out_f.write(f"{title}\n")
                out_f.write(f"{price_string}\n")
                out_f.write(f"{full_description}\n")
                out_f.write(f"{color}\n")
                out_f.write(f"img_number: {img_number}\n\n")  # 使用成功下载的图片数量
                
                print("  -> 文本已写入，图片下载完毕！")

            except TimeoutException:
                print("  -> 页面加载超时，跳过。")
            except Exception as e:
                print(f"  -> 解析时发生未知错误: {e}")
            
            # 礼貌性延时
            time.sleep(2)

    driver.quit()
    print(f"\n=========================================")
    print(f"抓取完成！")
    print(f"文本已保存至: {output_file_path}")
    print(f"图片保存目录: {os.path.join(script_dir, 'product-images')}")
    print(f"=========================================")

if __name__ == "__main__":
    get_product_details(max_items=3)