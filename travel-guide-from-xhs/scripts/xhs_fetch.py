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
    抓取同时打印每篇笔记的收藏/点赞数（interactInfo，免登录），
    便于按热度排序、优先读取高收藏笔记。

抓完后用 Read 工具逐张读取 xhs_imgs/ 下的图片识别内容。
"""

import os
import re
import sys
import json
import time
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


def extract_interact_info(html):
    """从 SSR 状态中提取 interactInfo（收藏/点赞/评论/分享数，字符串）。

    路径：__INITIAL_STATE__ -> note.noteDetailMap[<id>].note.interactInfo
    返回 dict 或 None。数字字段是字符串，调用方自行 int()。
    """
    try:
        m = re.search(r"window\.__INITIAL_STATE__=(\{.*?\})\s*</script>", html, re.S)
        if not m:
            return None
        # SSR JSON 里可能有 undefined 字面量，先替换再解析
        raw = re.sub(r"(?<=[:,[])\s*undefined\s*(?=[,}\]])", "null", m.group(1))
        obj = json.loads(raw)
        detail_map = (obj.get("note") or {}).get("noteDetailMap") or {}
        for note_id, detail in detail_map.items():
            note = detail.get("note") or {}
            inter = note.get("interactInfo")
            if inter:
                return {
                    "note_id": note_id,
                    "title": note.get("title", ""),
                    "collected_count": int(inter.get("collectedCount") or 0),
                    "liked_count": int(inter.get("likedCount") or 0),
                    "comment_count": int(inter.get("commentCount") or 0),
                    "share_count": int(inter.get("shareCount") or 0),
                }
    except Exception:
        pass
    return None


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
    hot = []
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
            for i, u in enumerate(urls, 1):
                fn = os.path.join(args.out, "xhs_imgs", f"{name}_{i:02d}.jpg")
                try:
                    size = download(u, fn)
                    print(f"    {name}_{i:02d}.jpg  {size} bytes")
                except Exception as e:
                    print(f"    FAIL {name}_{i:02d}: {e}")
            # 热度数据（免登录 SSR 自带）
            info = extract_interact_info(html)
            if info:
                info["name"] = name
                hot.append(info)
                print(f"  热度: 收藏 {info['collected_count']} | 点赞 {info['liked_count']} | "
                      f"评论 {info['comment_count']} | {info['title'][:40]}")
            else:
                print("  热度: 无法解析（页面可能是登录墙/SSR 未渲染）")
            # 控制节奏，避免触发临时 IP 风控
            if idx < len(url_list):
                time.sleep(3)
        except Exception as e:
            print(f"  抓取失败: {e}")

    if hot:
        print("\n=== 按收藏数排序（攻略价值最高）===")
        for h in sorted(hot, key=lambda x: x["collected_count"], reverse=True):
            print(f"  收藏 {h['collected_count']:>6} | 赞 {h['liked_count']:>6} | {h['name']} | {h['title'][:40]}")
        print("\n优先用 Read 逐张读取排序靠前笔记的图片。")

    print("\n完成。用 Read 工具逐张读取 xhs_imgs/ 下的图片。")
    print("若未抓到图片，参考 references/xhs-note-extraction.md 排查。")


if __name__ == "__main__":
    main()
