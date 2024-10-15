import os
import zipfile
import xml.etree.ElementTree as ET
import shutil
import re
import sys

def modify_epub_cover(epub_path, output_dir, new_cover_filename='cover.jpg'):
    # 创建临时目录
    temp_dir = os.path.join(os.path.dirname(epub_path), 'temp_epub')
    os.makedirs(temp_dir, exist_ok=True)

    # 解压 epub
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 查找并解析 content.opf 文件
    opf_path = None
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith('.opf'):
                opf_path = os.path.join(root, file)
                break
        if opf_path:
            break

    if not opf_path:
        shutil.rmtree(temp_dir)
        return

    # 解析 content.opf 文件
    tree = ET.parse(opf_path)
    root = tree.getroot()

    # 定义命名空间
    ns = {'opf': 'http://www.idpf.org/2007/opf'}

    # 查找 manifest 元素
    manifest = root.find('opf:manifest', ns)

    # 查找封面图片项
    cover_item = manifest.find(".//opf:item[@properties='cover-image']", ns)

    if cover_item is not None:
        # 获取旧文件名
        old_filename = cover_item.get('href').split('/')[-1]
        old_path = os.path.join(os.path.dirname(opf_path), cover_item.get('href'))

        # 更新封面图片项属性
        new_href = cover_item.get('href').replace(old_filename, new_cover_filename)
        cover_item.set('href', new_href)

        # 保存修改后的 content.opf 文件
        tree.write(opf_path, encoding='utf-8', xml_declaration=True)

        # 重命名实际的图片文件
        new_path = os.path.join(os.path.dirname(old_path), new_cover_filename)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)

        # 修改 p-cover.xhtml 文件
        cover_xhtml_path = os.path.join(temp_dir, 'OEBPS', 'Text', 'p-cover.xhtml')
        if os.path.exists(cover_xhtml_path):
            with open(cover_xhtml_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 使用正则表达式替换图片文件名
            new_content = re.sub(r'xlink:href="[^"]*"', f'xlink:href="../Images/{new_cover_filename}"', content)

            with open(cover_xhtml_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

    # 创建新的 epub 文件
    output_epub_path = os.path.join(output_dir, os.path.basename(epub_path))
    with zipfile.ZipFile(output_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

def process_epubs(directory):
    output_dir = os.path.join(directory, 'output')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(directory):
        if filename.endswith('.epub'):
            epub_path = os.path.join(directory, filename)
            modify_epub_cover(epub_path, output_dir)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果有参数，处理指定目录
        target_dir = sys.argv[1]
    else:
        # 否则处理当前目录
        target_dir = os.getcwd()

    process_epubs(target_dir)
