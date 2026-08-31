# -*- coding: utf-8 -*-
"""将 CRM 模块手册 .md 转为带侧边目录的专业 HTML（通用参数版）。

用法:
    python3 md2html.py <源.md路径> [--title 标题] [--date YYYY-MM-DD]

未传 --title/--date 时从文件名自动推断（如 opportunity-module → 商机模块）。
"""
import markdown, pathlib, re, sys

def auto_title(name: str) -> str:
    """从文件名推断中文标题。"""
    stem = name.replace("consulting-handbook", "").strip("-").split("-")
    mapping = {
        "lead": "线索模块（Lead）咨询诊断手册",
        "customer": "客户模块（Customer / Account）咨询诊断手册",
        "opportunity": "商机模块（Opportunity）咨询诊断手册",
        "quote": "报价模块（Quote）咨询诊断手册",
        "order": "订单模块（Order）咨询诊断手册",
        "contract": "合同模块（Contract）咨询诊断手册",
        "service": "服务模块（Service）咨询诊断手册",
    }
    for key, val in mapping.items():
        if key in stem:
            return val
    return "CRM 模块咨询诊断手册"

def auto_date(name: str) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return m.group(1) if m else ""

args = sys.argv[1:]
if not args:
    print("usage: python3 md2html.py <src.md> [--title T] [--date D]")
    sys.exit(1)

SRC = pathlib.Path(args[0])
TITLE = "CRM 模块咨询诊断手册"
DATE = auto_date(SRC.stem)
if "--title" in args:
    TITLE = args[args.index("--title") + 1]
else:
    TITLE = auto_title(SRC.name)
if "--date" in args:
    DATE = args[args.index("--date") + 1]
OUT = SRC.with_suffix(".html")
BRAND_SUB = f"{TITLE.split('（')[0]} · {DATE}" if DATE else TITLE.split("（")[0]

text = SRC.read_text(encoding="utf-8")
md = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
    extension_configs={"toc": {"toc_depth": "2"}},
)
body = md.convert(text)
toc = md.toc

CSS = """
:root{
  --navy:#0b1f3a; --navy2:#123b68; --blue:#1f6feb; --ink:#1f2937; --muted:#6b7280;
  --line:#e5e7eb; --bg:#f8fafc; --card:#ffffff; --accent:#c8102e;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",system-ui,sans-serif;
  color:var(--ink);background:var(--bg);line-height:1.75;font-size:15px}
.wrap{display:flex;align-items:flex-start;max-width:1280px;margin:0 auto}
.side{position:sticky;top:0;height:100vh;overflow-y:auto;width:270px;flex:0 0 270px;
  padding:24px 18px 40px;background:var(--navy);color:#cbd5e1}
.side .brand{font-size:13px;font-weight:700;color:#fff;letter-spacing:1px;margin:0 0 4px}
.side .brand-sub{font-size:11px;color:#94a3b8;margin-bottom:18px}
.side .toc{font-size:12.5px}
.side .toc ul{list-style:none;margin:0;padding:0}
.side .toc ul ul{margin:2px 0 6px 12px;border-left:1px solid #334155;padding-left:10px}
.side .toc a{display:block;color:#cbd5e1;text-decoration:none;padding:3px 6px;border-radius:4px}
.side .toc a:hover{background:#1e3a5f;color:#fff}
.side .toc ul ul a{color:#94a3b8}
.side .toc ul ul a:hover{color:#fff}
.main{flex:1;min-width:0;padding:40px 48px 80px;background:var(--card)}
h1{font-size:26px;color:var(--navy);margin:0 0 6px;line-height:1.4}
.doc-meta{font-size:13px;color:var(--muted);border-bottom:3px solid var(--navy);padding-bottom:16px;margin-bottom:28px}
h2{font-size:20px;color:var(--navy);border-left:5px solid var(--navy2);padding-left:12px;
  margin:40px 0 16px;scroll-margin-top:20px}
h3{font-size:16px;color:var(--navy2);margin:28px 0 12px;scroll-margin-top:20px}
h4{font-size:14.5px;color:var(--ink);margin:20px 0 8px}
p{margin:10px 0}
strong{color:var(--navy)}
.table-wrap{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13.5px;background:#fff}
th{background:var(--navy);color:#fff;font-weight:600;padding:9px 12px;text-align:left;white-space:nowrap}
td{padding:8px 12px;border-top:1px solid var(--line);vertical-align:top}
tbody tr:nth-child(even){background:var(--bg)}
pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:8px;overflow-x:auto;font-size:13px}
code{font-family:Consolas,Menlo,monospace}
p code,li code,td code{background:#eef2f7;color:var(--navy2);padding:1px 6px;border-radius:4px;font-size:12.5px}
blockquote{margin:14px 0;padding:10px 16px;border-left:4px solid var(--accent);
  background:#fff5f5;color:#7f1d1d;border-radius:0 8px 8px 0}
blockquote p{margin:4px 0}
blockquote strong{color:var(--accent)}
ul,ol{padding-left:24px}
li{margin:4px 0}
hr{border:none;border-top:1px solid var(--line);margin:32px 0}
.top{position:fixed;right:24px;bottom:24px;background:var(--navy);color:#fff;width:40px;height:40px;
  border-radius:50%;text-align:center;line-height:40px;text-decoration:none;font-size:18px;box-shadow:0 4px 12px rgba(0,0,0,.25)}
.top:hover{background:var(--navy2)}
@media (max-width:900px){
  .wrap{flex-direction:column}
  .side{position:static;width:100%;height:auto;max-height:300px}
  .main{padding:24px 20px 60px}
}
"""

HTML_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <aside class="side">
    <p class="brand">CRM 模块咨询手册</p>
    <p class="brand-sub">{brand_sub}</p>
    <nav class="toc">{toc}</nav>
  </aside>
  <main class="main">
    <h1>{title}</h1>
    <div class="doc-meta">战略咨询顾问 丁笃行（Ding）· 战略咨询合伙人　|　{date}　|　基于线索域手册同源方法论</div>
    {body}
    <hr>
    <p style="color:var(--muted);font-size:12.5px">⚠️ 以上内容由 AI 基于可获得信息整理生成，仅供决策参考，不构成正式投资或法律建议。重大决策请结合专业顾问意见。</p>
  </main>
</div>
<a class="top" href="#top" title="返回顶部">↑</a>
</body>
</html>
"""

html = HTML_TMPL.format(title=TITLE, css=CSS, toc=toc, body=body, brand_sub=BRAND_SUB, date=DATE or "—")
OUT.write_text(html, encoding="utf-8")
print(f"OK -> {OUT}")
print(f"size={OUT.stat().st_size} bytes | title={TITLE} | date={DATE}")
