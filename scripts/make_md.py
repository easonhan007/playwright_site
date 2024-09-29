import sys
import requests
import os
import random
import shutil
from datetime import datetime
import pytz
from download_image_from_a_md import dl_images

header_templ = """
+++
date = {}
title = "{}"
description = "{}"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++
"""

class MdMaker():
    def __init__(self, url) -> None:
        self.origin_url = url
        self.url = f"https://r.jina.ai/{url}"
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            }
        self.set_banner_dir()
        self.get_md_content()

    def set_banner_dir(self):
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        self.banner_dir =  os.path.join(parent_dir, "banners")

    def get_md_content(self):
        try:
            print(f"🚀 GET {self.url}")
            resp = requests.get(self.url, headers=self.headers)
        except:
            print(f"Can not access {self.url}")
            exit(1)

        if resp.status_code >= 400:
            print(f"Inavlid status code, the code is {resp.status_code}")
            exit(1)

        self.content = resp.text
        return self.content

    def guess_dir_name(self):
        if "?" in self.origin_url:
            without_questoin_mark = self.origin_url.split("?")[0]
        else:
            without_questoin_mark = self.origin_url

        parts = without_questoin_mark.split('/')
        if len(parts[-1]) == 0:
            dir_name = parts[-2]
        else:
            dir_name = parts[-1]

        return dir_name

    def mkdir(self):
        dir_name = self.guess_dir_name()
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)

        new_dir_path = os.path.join(parent_dir, "content", "blog", dir_name)

        if not os.path.isdir(new_dir_path):
            os.makedirs(new_dir_path, exist_ok=True)
            print(f"🚌 Create dir {new_dir_path}")
        else:
            print(f"😭 {new_dir_path} exists, nothing to do")

        self.md_dir = new_dir_path
        return new_dir_path

    def get_info(self):
        lines = self.content.split("\n")
        meta_list = lines[:7]
        self.primary_content = "\n".join(lines[7:])
        title = source = published_at = ""
        for line in meta_list:
            if "Title:" in line:
                title = line.replace("Title:", "").strip()
                continue
            if "URL Source:" in line:
                source = line.replace("URL Source:", "").strip()
                continue
            if "Published Time:" in line:
                published_at = line.replace("Published Time:", "").strip()
                continue

        print(title, source, published_at)
        return (title, source, published_at)
                

    def gen_header(self, title, desc, published):
        return header_templ.format(published, title, desc)

    def mkmd(self):
        title, source, published_at = self.get_info()
        if len(title) == 0:
            print("Can not get title")
            exit(1)
        if len(published_at) == 0:
            published = datetime.now().strftime("%Y-%m-%d")
        else:
            published = self.format_date(published_at)
        
        header = self.gen_header(title, source, published)
        
        md_path = os.path.join(self.md_dir, "index.md")
        if os.path.exists(md_path):
            print(f"❌ {md_path} exists, skip")
        else:
            with open(md_path, "w+") as f:
                print(f"✅ create {md_path}")
                f.write(header + self.primary_content)

    def format_date(self, date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        # 设置时区为UTC
        dt = dt.replace(tzinfo=pytz.UTC)
        # 格式化输出
        return dt.strftime("%Y-%m-%d")

    def select_a_banner(self):
        # Get all JPG files from the source directory
        jpg_files = [f for f in os.listdir(self.banner_dir) if f.lower().endswith('.jpg')]

        if not jpg_files:
            print("No JPG files found in the source directory.")
            return

        # Randomly select a JPG file
        selected_file = random.choice(jpg_files)
        
        # Construct full paths
        source_path = os.path.join(self.banner_dir, selected_file)
        destination_path = os.path.join(self.md_dir, 'banner.jpg')

        # Copy the file to the destination directory and rename it
        shutil.copy2(source_path, destination_path)

        print(f"Randomly selected '{selected_file}', copied to '{destination_path}' as 'banner.jpg'")

    def process(self):
        self.mkdir()
        self.mkmd()
        self.select_a_banner()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: make_md URL")
        exit(0)

    maker = MdMaker(sys.argv[-1])
    maker.process()
    dl_images(maker.md_dir)
    