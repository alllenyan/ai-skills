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
