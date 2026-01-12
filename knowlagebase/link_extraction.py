import re
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def extract_links_with_labels(html_content, base_url):
    """
    提取HTML中所有有效跳转链接，并关联对应的标签文本
    :param html_content: 原始HTML文本
    :param base_url: 网页基础URL（用于补全相对链接）
    :return: 结构化的{标签: 链接}字典（按站内/外部分类）
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 无效链接过滤规则
    invalid_patterns = [
        r'^$', r'^#', r'^javascript:',
        r'\.(css|js|png|jpg|jpeg|gif|svg|ico|pdf|zip|rar)$',
        r'^mailto:', r'^tel:'
    ]
    invalid_regex = re.compile('|'.join(invalid_patterns), re.IGNORECASE)

    # 存储结果：key=清理后的标签文本，value=绝对链接（去重+分类）
    links_with_labels = {
        'internal': {},  # 站内链接 {标签: 链接}
        'external': {}  # 外部链接 {标签: 链接}
    }
    base_domain = urlparse(base_url).netloc

    # 遍历所有<a>标签
    for a_tag in soup.find_all('a', href=True):
        # 1. 提取原始链接和标签文本
        raw_href = a_tag.get('href', '').strip()
        raw_label = a_tag.get_text(strip=True)

        # 2. 过滤无效链接
        if invalid_regex.match(raw_href):
            continue

        # 3. 清理标签文本
        clean_label = re.sub(r'[\n\t\r↓▲●■]', '', raw_label)
        if not clean_label:
            continue

        # 4. 补全绝对链接
        absolute_href = urljoin(base_url, raw_href)

        # 5. 区分站内/外部链接，并关联标签（去重）
        link_domain = urlparse(absolute_href).netloc
        if link_domain == base_domain or link_domain == '':
            if clean_label not in links_with_labels['internal']:
                links_with_labels['internal'][clean_label] = absolute_href
        else:
            if clean_label not in links_with_labels['external']:
                links_with_labels['external'][clean_label] = absolute_href

    # 按标签文本排序
    links_with_labels['internal'] = dict(sorted(links_with_labels['internal'].items()))
    links_with_labels['external'] = dict(sorted(links_with_labels['external'].items()))

    return links_with_labels


def merge_links_to_json(new_links, json_file_path='links_with_labels.json'):
    """
    将新提取的链接合并到JSON文件中
    :param new_links: 新提取的链接字典（internal/external）
    :param json_file_path: 保存结果的JSON文件路径
    """
    # 1. 读取已有数据（若文件不存在则初始化空字典）
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {'internal': {}, 'external': {}}

    # 2. 合并新数据（新数据覆盖重复标签，保证最新）
    # 合并站内链接
    existing_data['internal'].update(new_links['internal'])
    # 合并外部链接
    existing_data['external'].update(new_links['external'])

    # 3. 重新排序（保持格式统一）
    existing_data['internal'] = dict(sorted(existing_data['internal'].items()))
    existing_data['external'] = dict(sorted(existing_data['external'].items()))

    # 4. 写入文件（覆盖原有文件，但内容是合并后的）
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

    print(f"\n 已将新链接合并到 {json_file_path} 文件")
    print(f" 当前文件内总站内链接：{len(existing_data['internal'])} 条")
    print(f" 当前文件内总外部链接：{len(existing_data['external'])} 条")


if __name__ == '__main__':
    # ===================== 配置项 =====================
    HTML_FILE_PATH = 'course.html'  # 要解析的HTML文件路径
    BASE_URL = 'https://course.openkylin.top/document'  # HTML对应网页的基础URL
    JSON_SAVE_PATH = 'links_with_labels.json'  # 结果保存的JSON文件路径
    # ==================================================

    # 1. 读取本地HTML文件
    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f" 错误：未找到HTML文件 {HTML_FILE_PATH}")
        exit(1)

    # 2. 提取带标签的链接
    new_extracted_links = extract_links_with_labels(html_content, BASE_URL)

    # 3. 输出本次提取的结果
    print("=" * 60)
    print(f" 本次提取到站内链接（{len(new_extracted_links['internal'])} 条）：")
    for label, link in new_extracted_links['internal'].items():
        print(f"  {label} : {link}")

    print("\n" + "=" * 60)
    print(f" 本次提取到外部链接（{len(new_extracted_links['external'])} 条）：")
    for label, link in new_extracted_links['external'].items():
        print(f"  {label} : {link}")

    # 4. 合并并写入JSON文件
    merge_links_to_json(new_extracted_links, JSON_SAVE_PATH)