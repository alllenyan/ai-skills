# 小红书笔记免登录读取：原理与排查

## 为什么需要这套方法

- 小红书网页版强制登录：未登录时 WebFetch / 无头浏览器拿到的多是登录页或验证页，正文拿不到
- 多图笔记（攻略类最常见）的内容在图片里，图片 URL 又在登录态后面
- **浏览器自动化（agent-browser/Playwright）不是默认方案**：机器出口 IP 多为机房 IP / Cloudflare WARP，会被小红书风控识别（页面提示 "IP at risk"），登录页直接拦截；即使走本地代理（如 127.0.0.1:10808）出口仍是机房 IP，同样被拦
- 免登录 SSR 提取路线不受登录风控影响，是性价比最高的方案

## 核心原理

小红书网页版是服务端渲染（SSR）：未登录下载的笔记页 HTML 里，`<script>window.__INITIAL_STATE__={...}</script>` 内嵌了完整笔记数据，其中 note 对象的 imageList 数组包含全部图片的完整 URL。

关键坑：JSON 里的 URL 斜杠被转义成 `\u002F`，直接正则匹配 `http://...` 匹配不到。必须先反转义：

```python
text = json_text.encode("utf-8", "ignore").decode("unicode_escape")
```

## 提取正则

```python
import re
IMAGE_RE = re.compile(
    r"https?://[a-z0-9.-]*xhscdn\.com/[A-Za-z0-9_/!.-]+"
    r"!(?:nd_dft_wlteh_jpg_3|nd_dft_wlteh_jpg)"
)
```

- 前缀：`http(s)://sns-webpic-qc.xhscdn.com/`（可能还有其他 xhscdn 子域）
- 路径字符集：字母数字、`/`、`_`、`-`、`!`
- 质量后缀：`!nd_dft_wlteh_jpg_3`（标准图）或 `!nd_dft_wlteh_jpg`

## 下载要点

- 必须带 `Referer: https://www.xiaohongshu.com/`，否则 CDN 拒绝（403）
- 必须带浏览器 User-Agent
- urllib / requests 即可，无需登录 cookie

## 故障排查表

| 现象 | 原因 | 处理 |
|---|---|---|
| HTML 很小、无 `__INITIAL_STATE__` | 被重定向到验证/登录页 | 换完整浏览器 UA 重试；确认 URL 完整带 `xsec_token` |
| 找到图片 URL 但下载 403 | 缺 Referer / 被 CDN 拦 | 加 `Referer: https://www.xiaohongshu.com/` |
| 图片能下载但内容是 HTML | 出口 IP 被风控返回假图 | 走本地代理（`127.0.0.1:10808`）重试 |
| 页面提示 "IP at risk" | 机房 IP 被识别 | 不要硬闯登录；SSR 提取路线通常不受影响 |
| 笔记是纯文字 | 无图片 | 直接读 HTML 里 `desc` 字段；WebFetch 可能已能拿到标题+正文 |
| 视频笔记 | 只有封面 | 只能拿到封面图，正文需其他途径 |

## 已知限制

- 只能读公开笔记（无需登录可见）；「仅关注可见」「仅粉丝可见」的内容读不到
- 视频笔记只拿到封面图
- 小红书若改版不再 SSR 渲染，此方法失效——届时回到浏览器自动化 + 真人扫码登录，且需真人 IP（家庭宽带）环境
- **密集请求会触发临时 IP 风控，SSR 也会被切断**（2026-08-28 实测）：正常时笔记页 SSR 返回 60-80KB+ 且含 `noteDetailMap`；短时间密集请求（连续多次评论 API + 批量抓页）后，同一 URL 开始返回 34KB 登录墙页，`noteDetailMap` 为 null。此时连免登录 SSR 也失效，需等待风控冷却（数小时到一天）或更换出口 IP。**控制抓取节奏**：单次任务抓 5-10 篇以内，每篇间隔 2-5 秒，不要连续触发登录相关接口（评论/搜索 API）。

## 笔记热度数据（interactInfo，免登录可读）

笔记页 SSR 的 `note.interactInfo` 里直接带点赞/收藏/评论/分享数（字符串），**免登录**，可用于「高赞高收藏笔记筛选」：

```json
"interactInfo": {
  "commentCount": "8", "shareCount": "151",
  "likedCount": "410", "collectedCount": "412"
}
```

解析路径：`window.__INITIAL_STATE__` → `note.noteDetailMap[noteId].note.interactInfo`。注意数字是字符串，需 `int()` 转换。**筛选优先级**：收藏数 > 点赞数（收藏代表「可执行参考价值」，更符合攻略场景）。

**找笔记的链接来源**（当前 IP 环境无法站内搜索——搜索 API 需登录返回 `-101`，搜索页浏览器打开直接被 300012 IP 风控重定向）：
1. 用户直接提供链接（最可靠）
2. WebSearch 搜转载站（今日头条/腾讯/新浪转载文）——只能拿到内容，通常拿不到原帖链接，但可作为补充证据
3. 换家庭宽带/手机流量环境后，可用浏览器搜索页或登录态搜索 API 直接搜
  
## 评论读取（实测结论 2026-08-28）

**结论：评论接口必须登录 cookie，无法匿名读取。** 笔记正文/图片可以免登录（SSR 路线），评论不行。

- SSR 页面 HTML 里的 `noteDetailMap/<id>/comments` 是空占位（`list: []`，`hasMore: true`），真实评论靠 API 拉取。
- 接口：`GET https://edith.xiaohongshu.com/api/sns/web/v2/comment/page`，参数 `note_id, cursor, top_comment_id, image_formats=jpg,webp,avif, xsec_token`（还可带 `xsec_source`/`source`）。
- 鉴权两件套：
  1. **签名头** x-s / x-t / x-s-common —— 由页面 JS `window._webmsxyw` 生成。纯 Python 重写的旧版签名（md5 `"test"` 方案，`xhs` PyPI 0.2.13 内置）已失效，返回 `code -1`。
  2. **登录 cookie** —— 至少 `a1` + `web_session`。无 cookie 时即使签名正确也返回 `code -101「无登录信息，或登录信息为空」`。
- 可行方案（`scripts/xhs_comments.py`）：Playwright + 系统 Chrome 加载笔记页 → 等 `_webmsxyw` 就绪 → 注入 init script 抓页面启动请求的 `x-s-common` → 页面内 `fetch` 带 `credentials:'include'` + 签名头调评论 API → 按 `cursor` 翻页直到 `has_more=false`。
- 错误码速查：
  | code | 含义 | 处理 |
  |---|---|---|
  | -1 | 签名无效/格式错 | 换真实 `_webmsxyw` 签名（别用旧纯 Python 版） |
  | -101 | 无登录信息 | 检查 cookie 是否被服务端删除；换网络环境或重新获取 cookie |
  | -100 | 登录已过期 | 登录态已被风控吊销或 cookie 过期，需重新获取 |
  | 300011 | 当前账号存在异常 | 当前 IP/设备环境被 XHS 风控标记，停止请求，换网络环境再试 |
  | 200 + code 0 | 成功 | 解析 `data.comments` |
- **环境限制（重要）**：评论接口不仅要求签名 + 登录 cookie，还要求 **IP/设备环境与账号匹配**。
  - 机房/Cloudflare WARP/服务器 IP 环境：笔记页 SSR 能加载、`_webmsxyw` 能跑、签名能生成，但登录 cookie 一注入就可能被 XHS 风控识别为「异常登录」：先返回 `300011 当前账号存在异常`，随后 `web_session` 被服务端吊销（`-100 登录已过期`），甚至页面加载时就被删除（`document.cookie` 里找不到 `web_session`，调用 API 返回 `-101`）。
  - 结论：**不要在机房/数据中心 IP 环境上调用评论脚本**。请在和用户账号相同或相近的家庭宽带/手机流量/办公室网络环境下运行。
- 依赖：`pip install playwright` + 本机 Chrome（`channel="chrome"` 免下载浏览器内核）。
- 时效提示：评论区比正文新，适合「店还在吗」「今天人多吗」「排队多久」类实时信息，但属低置信度信源，需与笔记正文、搜索交叉验证。
