<div align="center">

# All-IN-ONE

**小红书 / 微博 / 抖音 — 统一 CLI & Agent Skill**

[![PyPI](https://img.shields.io/pypi/v/all-in-one-aione)](https://pypi.org/project/all-in-one-aione/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/nodejs-16%2B-green)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

</div>

> **CLI** 是执行层，统一操作三个平台。**Skill** 是 Agent 的说明书，Agent 读完就知道怎么装 CLI、怎么调命令、怎么传参数。
>
> 挂载 Skill → Agent 学会用 CLI → 你说自然语言 → Agent 干活。

---

## 为什么需要这个项目？

AI Agent 很强，但它没有操作社交平台的能力。小红书、微博、抖音没有开放 API，想让 Agent 操作它们需要逆向签名、处理认证、三个平台三套代码。

All-IN-ONE 解决这个问题：

```
三个上游仓库（签名/请求/认证已处理）
  Spider_XHS  ─┐
  WeiboApis   ─┤──► aione CLI（146 条命令，JSON 输出）──► Agent 通过 Skill 调用
  DouYin_Spider─┘
```

上游仓库：[Spider_XHS](https://github.com/cv-cat/Spider_XHS) / [WeiboApis](https://github.com/cv-cat/WeiboApis) / [DouYin_Spider](https://github.com/cv-cat/DouYin_Spider)

---

## 🛠️ 安装

```bash
pip install all-in-one-aione
aione setup
```

`aione setup` 自动 clone 三个上游仓库并安装签名所需的 npm 依赖。需要 Python 3.9+、Node.js 16+、Git。

从源码安装：

```bash
git clone https://github.com/cv-cat/All-IN-ONE.git && cd All-IN-ONE
pip install -e . && aione setup
```

---

## 🧩 Agent Skill

**Skill 是 Agent 的入口。** Agent 读取 Skill 后自动知道：CLI 怎么装、有哪些命令、参数怎么传、cookie 怎么配。

### 接入

把 `skills/all-in-one/` 挂载到你的 Agent：

- **Claude Code** — 放到项目的 `skills/` 目录下
- **Codex / 其他 Agent** — 引用 `SKILL.md` 作为工具描述

### 效果

> 你：帮我搜小红书上关于咖啡的笔记

Agent 读取 `references/xhs.md` → 执行 `aione xhs note search --query "咖啡" --page 1 --output json` → 返回结果

> 你：看看这个抖音视频的评论

Agent 读取 `references/douyin.md` → 执行 `aione douyin work all-comment --url "..." --output json` → 返回评论

> 你：在蒲公英上找 KOL 发合作邀请

Agent 读取 `references/xhs.md` → 执行 pugongying 系列命令 → 获取数据 → 发出邀请

### Skill 结构

```
skills/all-in-one/
  SKILL.md                ← Agent 入口：安装方法 + 使用说明
  references/
    auth.md               ← cookie 认证体系（优先级、多 profile、环境变量）
    xhs.md                ← 小红书 86 条命令参考
    weibo.md              ← 微博 15 条命令参考
    douyin.md             ← 抖音 45 条命令参考
    workflows.md          ← 跨平台工作流模板（搜索、详情、发布、直播）
```

---

## 🚀 CLI 使用

Skill 让 Agent 用 CLI，你也可以直接命令行操作：

```bash
# 搜索
aione xhs note search --query "咖啡" --page 1 --output json
aione weibo post search --query "AI" --page 1 --output json
aione douyin work search-some-general --query "美食" --num 20 --output json

# 内容详情
aione xhs note info --url "<笔记链接>" --output json
aione douyin work info --url "https://www.douyin.com/video/..." --output json

# 用户信息
aione xhs user self-info --output json
aione weibo info self --output json

# 评论
aione xhs note all-comment --url "<笔记链接>" --output json
aione douyin work all-comment --url "<视频链接>" --output json

# 创作者发布
aione xhs creator post-note --note-info '{"title":"...","desc":"..."}' --output json
aione weibo weibo post --note-info '{"content":"..."}' --output json

# KOL 数据
aione xhs pugongying user-by-page --page 1 --output json

# Dry-run（不调用 API，验证命令映射）
aione douyin work info --dry-run --url "https://www.douyin.com/video/example"
```

---

## ⭐ 覆盖能力

| 平台 | 模块 | 命令数 | 说明 |
|------|------|--------|------|
| **小红书** | PC 端 | 32 | 首页推荐、搜索笔记/用户、笔记详情、评论、消息、无水印下载 |
| | 创作者平台 | 11 | 上传媒体、发布笔记、查看已发布作品 |
| | PC 登录 | 11 | 二维码登录、手机验证码登录 |
| | 创作者登录 | 12 | 二维码登录、手机验证码登录、会话检查 |
| | 蒲公英 | 11 | KOL 博主列表、粉丝画像、合作邀请 |
| | 千帆 | 9 | 分销商列表、合作品类、店铺/商品数据 |
| **微博** | Web 端 | 7 | 用户信息、微博搜索、评论、用户全部微博 |
| | 创作者 | 6 | 图片/视频上传、发布微博 |
| | Mobile | 2 | 移动端搜索、作品详情 |
| **抖音** | 用户/作品 | 45 | 用户信息、视频详情、搜索、评论、粉丝/关注列表、收藏、私信、直播、推荐流 |
| **合计** | | **146** | |

---

## 🔐 认证

### Cookie 配置

```bash
aione auth xhs set-cookie --cookie "<你的小红书cookie>"
aione auth weibo set-cookie --cookie "<你的微博cookie>"
aione auth douyin set-cookie --cookie "<你的抖音cookie>"
```

Cookie 优先级：`--cookies` 参数 > 环境变量 > 本地存储

### 多 Profile

不同模块使用不同的 cookie，命令执行时自动匹配：

| 平台 | Profile | 对应模块 |
|------|---------|----------|
| XHS | `pc` | PC 端浏览/搜索/评论 |
| XHS | `creator` | 创作者平台发布 |
| XHS | `pugongying` | 蒲公英 KOL 数据 |
| XHS | `qianfan` | 千帆分销商数据 |
| 微博 | `web` | Web 端 |
| 微博 | `creator` | 创作者 |
| 微博 | `mobile` | 移动端 |
| 抖音 | `web` | PC 端 |
| 抖音 | `live` | 直播相关 |

```bash
aione auth xhs set-cookie --profile creator --cookie "<创作者cookie>"
aione auth douyin set-cookie --profile live --cookie "<直播cookie>"
```

---

## 📁 项目结构

```
All-IN-ONE/
├── skills/all-in-one/           # Agent Skill（Agent 的入口）
│   ├── SKILL.md                 #   安装方法 + 使用说明
│   └── references/              #   平台命令参考 + 工作流
├── all_in_one/
│   ├── cli/                     # CLI 实现（认证、路由、输出、错误）
│   └── platforms/               # 上游发现、注册、调用、映射
├── aione/                       # python -m aione 入口
├── tests/                       # 43 个测试（含 cookie 门控集成测试）
├── main.py                      # python main.py 入口
└── pyproject.toml               # 包配置 & 依赖
```

---

## 🧪 测试

```bash
python -m pytest tests/ -v

# 真实接口测试（需要 cookie）
AIONE_XHS_COOKIES="<cookie>" AIONE_WEIBO_COOKIES="<cookie>" AIONE_DOUYIN_COOKIES="<cookie>" \
  python -m pytest tests/ -m integration -v
```

---

## 🗝️ 注意事项

- Cookie 有时效性，失效后需重新获取并执行 `aione auth <平台> set-cookie`
- 建议配合代理使用：`--proxy http://127.0.0.1:7890`
- 创作者/发布类接口请谨慎使用，注意平台规则
- `upstreams/` 目录通过 `aione setup` 管理，不纳入版本控制
- 更新上游仓库：进入对应目录 `git pull`，或删除后重新 `aione setup`

---

## 🧸 额外说明

1. 感谢 Star 和 Follow，项目会持续更新
2. 作者联系方式在主页，有问题随时联系
3. 欢迎 PR 和 Issue，也欢迎关注作者其他项目
4. 如果此项目对您有帮助，欢迎请作者喝一杯奶茶

<div align="center">
  <img src="https://github.com/cv-cat/Spider_XHS/blob/master/author/wx_pay.png" width="380px" alt="微信赞赏码">
  <img src="https://github.com/cv-cat/Spider_XHS/blob/master/author/zfb_pay.jpg" width="380px" alt="支付宝收款码">
</div>

---

## 📈 Star 趋势

<a href="https://www.star-history.com/#cv-cat/All-IN-ONE&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=cv-cat/All-IN-ONE&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=cv-cat/All-IN-ONE&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=cv-cat/All-IN-ONE&type=Date" />
  </picture>
</a>

---

## 🍔 交流群

如果你对爬虫和 AI Agent 感兴趣，请加作者主页 wx 通过邀请加入群聊

ps: 请加群13、14，人满或者过期 issue | wx 提醒

![group13](https://github.com/user-attachments/assets/cc06a36f-7abf-4646-a4a3-c2c841a77a88)

![group14](https://github.com/user-attachments/assets/7c73f29e-0c46-4708-81a5-cc8527023de2)
