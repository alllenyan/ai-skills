#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书笔记免登录图片抓取工具。

原理：小红书网页版是 SSR 渲染，未登录下载的 HTML 里也内嵌
window.__INITIAL_STATE__，其中 note.imageList 含全部图片 URL。
URL 里的斜杠被转义为 \\u002F，需先反转义再提取，然后带 Referer
从 xhscdn CDN 批量下载。

用法:
    python xhs_fetch.py <url1> [url2] ... [--out DIR]
    python xhs_fetch.py urls.txt            # 文件内每行一个 URL

输出:
    DIR/note1.html, note2.html ...   (下载的页面源码，可溯源)
    DIR/xhs_imgs/note1_01.jpg ...    (全部图片)

抓完后用 Read 工具逐张读取 xhs_imgs/ 下的图片识别内容。
"""

import os
import re
import sys
import argparse
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Referer": "https://www.xiaohongshu.com/"}

# 匹配 xhscdn CDN 图片 URL，结尾带质量后缀
IMAGE_RE = re.compile(
    r"https?://[a-z0-9.-]*xhscdn\.com/[A-Za-z0-9_/!.-]+"
    r"!(?:nd_dft_wlteh_jpg_3|nd_dft_wlteh_jpg)"
)


def fetch_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def extract_image_urls(html):
    """从 SSR 初始状态 JSON 中提取全部图片 URL。"""
    m = re.search(r"window\.__INITIAL_STATE__=(.*?)</script>", html, re.S)
    if m:
        # 反转义 \u002F 等 unicode 转义（图片 URL 里的斜杠是转义形式）
        text = m.group(1).encode("utf-8", "ignore").decode("unicode_escape")
    else:
        # 兜底：直接在整页源码里找
        text = html
    urls = []
    for u in IMAGE_RE.findall(text):
        if u not in urls:
            urls.append(u)
    return urls


def download(url, path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    ap = argparse.ArgumentParser(description="免登录抓取小红书笔记全部图片")
    ap.add_argument("urls", nargs="+", help="笔记 URL，或一个每行一个 URL 的 txt 文件")
    ap.add_argument("--out", default=".", help="输出目录（默认当前目录）")
    args = ap.parse_args()

    url_list = []
    for item in args.urls:
        if item.endswith(".txt") and os.path.isfile(item):
            with open(item, encoding="utf-8") as f:
                url_list += [l.strip() for l in f if l.strip()]
        else:
            url_list.append(item)

    if not url_list:
        print("没有可用的 URL")
        sys.exit(1)

    os.makedirs(os.path.join(args.out, "xhs_imgs"), exist_ok=True)
    for idx, url in enumerate(url_list, 1):
        name = f"note{idx}"
        print(f"\n[{idx}/{len(url_list)}] {url[:70]}")
        try:
            html = fetch_html(url)
            with open(os.path.join(args.out, f"{name}.html"), "w", encoding="utf-8") as f:
                f.write(html)
            urls = extract_image_urls(html)
            print(f"  找到 {len(urls)} 张图片")
            if not urls:
                print("  未找到图片：可能被拦到验证页、纯文字笔记或视频笔记")
                continue
            for i, u in enumerate(urls, 1):
                fn = os.path.join(args.out, "xhs_imgs", f"{name}_{i:02d}.jpg")
                try:
                    size = download(u, fn)
                    print(f"    {name}_{i:02d}.jpg  {size} bytes")
                except Exception as e:
                    print(f"    FAIL {name}_{i:02d}: {e}")
        except Exception as e:
            print(f"  抓取失败: {e}")

    print("\n完成。用 Read 工具逐张读取 xhs_imgs/ 下的图片。")
    print("若未抓到图片，参考 references/xhs-note-extraction.md 排查。")


if __name__ == "__main__":
    main()
