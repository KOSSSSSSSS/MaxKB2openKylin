import requests
from requests.exceptions import RequestException
import time


def crawl_website(url, save_path):
    # 请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.openkylin.top/",
        "Connection": "keep-alive"
    }

    try:
        # 发送GET请求，设置超时时间
        response = requests.get(
            url=url,
            headers=headers,
            timeout=15,
            verify=False
        )
        # 检查响应状态码
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"

        # 写入文件
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"网页爬取成功！已保存至：{save_path}")

    except RequestException as e:
        print(f"爬取失败！错误信息：{e}")
    except Exception as e:
        print(f"未知错误：{e}")


if __name__ == "__main__":
    # 目标URL
    target_url = "https://course.openkylin.top/document"
    # 保存路径
    save_file = ("./course.html")

    # 休眠1秒
    time.sleep(1)

    crawl_website(target_url, save_file)