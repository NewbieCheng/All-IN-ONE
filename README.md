<div align="center">

# All-IN-ONE

**小红书 / 微博 / 抖音 — 统一 CLI & Agent Skill**

[![PyPI](https://img.shields.io/pypi/v/all-in-one-aione)](https://pypi.org/project/all-in-one-aione/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/nodejs-16%2B-green)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

</div>

> 把三个平台的 API 仓库合并成一条命令行和一个 Agent Skill。
> CLI 是稳定执行层，Agent 只需 shell 调用 `aione` 并解析 JSON，无需直接引入上游代码。

---

## 为什么需要这个项目？

```
小红书 API (Spider_XHS)  ─┐
微博 API   (WeiboApis)   ─┤──► aione CLI ──► 你的 AI Agent / 脚本 / 工作流
抖音 API   (DouYin_Spider)─┘      │
                                   ├─ 统一认证 (cookie save/status/clear)
                                   ├─ 统一输出 (json / pretty / file)
                                   ├─ 统一代理 & 超时
                                   └─ 统一错误分类
```

三个仓库各自有不同的调用方式、签名算法、参数风格。All-IN-ONE 做的事情：

- **自动发现** — AST 解析上游源码，零配置注册全部公开接口
- **统一命名** — `aione <平台> <资源> <动作>` 取代零散的函数调用
- **Cookie 管理** — 支持多 profile（PC / 创作者 / 蒲公英 / 千帆 / 直播），优先级：`--cookies` > 环境变量 > 本地存储
- **Agent 就绪** — 所有命令默认输出 JSON，Agent 直接 shell 调用 + 解析

上游仓库：

| 平台 | 仓库 | 说明 |
|------|------|------|
| 小红书 | [Spider_XHS](https://github.com/cv-cat/Spider_XHS) | PC端/创作者/蒲公英/千帆 API |
| 微博 | [WeiboApis](https://github.com/cv-cat/WeiboApis) | Web端/创作者/移动端 API |
| 抖音 | [DouYin_Spider](https://github.com/cv-cat/DouYin_Spider) | 用户/作品/直播/互动 API |

---

## ⭐ 已覆盖功能

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

## 🛠️ 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+（XHS 和抖音的签名算法需要）
- Git

### 安装

**方式一：从 PyPI 安装（推荐）**

```bash
pip install all-in-one-aione
aione setup
```

**方式二：从源码安装**

```bash
git clone https://github.com/cv-cat/All-IN-ONE.git
cd All-IN-ONE
pip install -e .
aione setup
```

`aione setup` 会自动完成：
1. `git clone --depth 1` 三个上游仓库
2. 检测 `package.json` 并执行 `npm install`（XHS 需要 `crypto-js`，抖音需要 `jsrsasign`）

### 配置 Cookie

浏览器登录对应平台后，`F12` → Application → Cookies，复制完整 cookie 字符串：

```bash
aione auth xhs set-cookie --cookie "<你的小红书cookie>"
aione auth weibo set-cookie --cookie "<你的微博cookie>"
aione auth douyin set-cookie --cookie "<你的抖音cookie>"
```

验证：

```bash
aione auth xhs status
aione auth weibo status
aione auth douyin status
```

> Cookie 存储在本地用户目录，文件权限 600，CLI 输出和日志永远不会泄露 cookie 值。

### 运行

```bash
aione --help
aione xhs note search --query "咖啡" --page 1 --output json
aione weibo post search --query "AI" --page 1 --output json
aione douyin work info --url "https://www.douyin.com/video/..." --output json
```

---

## 🚀 CLI 使用示例

### 搜索

```bash
# 小红书搜索笔记
aione xhs note search --query "咖啡" --page 1 --output json

# 小红书批量搜索（自动翻页）
aione xhs note search-some --query "咖啡" --require-num 50 --output json

# 微博搜索
aione weibo post search --query "AI" --page 1 --output json

# 抖音搜索视频
aione douyin work search-some-general --query "美食" --num 20 --output json
```

### 内容详情

```bash
aione xhs note info --url "<笔记链接>" --output json
aione weibo work info --url "<微博链接>" --output json
aione douyin work info --url "https://www.douyin.com/video/..." --output json
```

### 用户信息

```bash
aione xhs user self-info --output json
aione weibo info self --output json
aione douyin uid self --output json
```

### 评论

```bash
aione xhs note all-comment --url "<笔记链接>" --output json
aione douyin work all-comment --url "<视频链接>" --output json
```

### 创作者发布

```bash
# 小红书发布笔记
aione xhs media upload --path-or-file "./image.jpg" --media-type image --output json
aione xhs creator post-note --note-info '{"title":"...","desc":"..."}' --output json

# 微博发布
aione weibo weibo post --note-info '{"content":"..."}' --output json
```

### Dry-run & Verbose

```bash
# 不调用 API，仅验证命令映射
aione douyin work info --dry-run --url "https://www.douyin.com/video/example"

# 调试信息输出到 stderr，不泄露 cookie
aione xhs user self-info --verbose --output json
```

---

## 🤖 接入 AI 智能体

All-IN-ONE 天然适合作为 AI Agent 的数据底座。Agent 只需 shell 调用 `aione` 并解析 JSON：

### 场景一：竞品内容采集 + AI 分析

```bash
# Agent 调用 CLI 搜索竞品笔记
aione xhs note search --query "竞品关键词" --page 1 --output json

# Agent 获取笔记详情
aione xhs note info --url "<笔记链接>" --output json

# Agent 将结果传给大模型分析趋势、生成报告
```

### 场景二：跨平台内容监控

```bash
# 同时监控三个平台的关键词
aione xhs note search --query "品牌名" --page 1 --output json
aione weibo post search --query "品牌名" --page 1 --output json
aione douyin work search-some-general --query "品牌名" --num 20 --output json
```

### 场景三：KOL 筛选 + 自动邀约

```bash
# 获取目标类目的 KOL 数据
aione xhs pugongying user-by-page --page 1 --output json

# AI 评估匹配度后，发起合作邀请
aione xhs pugongying send-invite --user-id "<id>" --product-name "产品" --time "时间" --invite-content "邀请内容" --contact-info "联系方式" --output json
```

### Agent Skill

项目提供标准化的 Skill 文件，直接挂载到 Agent 上即可使用。Agent 根据 Skill 描述自动选择 CLI 命令执行，无需额外编码：

- **Claude Code** — 将 `skills/all-in-one/` 放入项目的 `.claude/skills/` 或直接在项目根目录
- **Codex / 其他 Agent** — 引用 `skills/all-in-one/SKILL.md` 作为工具描述

```
skills/
  all-in-one/
    SKILL.md                # Skill 入口 — Agent 读取后自动获得三平台操作能力
    references/
      auth.md               # 认证：cookie 优先级、多 profile、环境变量
      xhs.md                # 小红书：86 条命令参考
      weibo.md              # 微博：15 条命令参考
      douyin.md             # 抖音：45 条命令参考
      workflows.md          # 跨平台工作流：搜索、详情、发布、直播
```

Agent 挂载后，你只需用自然语言描述任务，Agent 自动调用对应的 `aione` 命令并返回结果。

---

## 🔐 认证体系

### Cookie 优先级

1. `--cookies "<cookie>"` — 命令行直接传入（最高优先级）
2. 环境变量 — `AIONE_XHS_COOKIES`、`AIONE_WEIBO_COOKIES`、`AIONE_DOUYIN_COOKIES`
3. 本地存储 — `aione auth <平台> set-cookie` 保存的 cookie

### 多 Profile 支持

不同模块使用不同的 cookie（自动匹配）：

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
aione auth xhs set-cookie --profile pc --cookie "<PC端cookie>"
aione auth xhs set-cookie --profile creator --cookie "<创作者cookie>"
aione auth douyin set-cookie --profile live --cookie "<直播cookie>"
```

---

## 📁 项目结构

```
All-IN-ONE/
├── all_in_one/
│   ├── cli/
│   │   ├── main.py              # CLI 入口、argparse 路由、setup 命令
│   │   ├── auth.py              # Cookie 存储 / 读取 / 清除 / 优先级解析
│   │   ├── errors.py            # 错误分类（AUTH_MISSING / UPSTREAM_ERROR / ...）
│   │   └── output.py            # 输出格式化（json / pretty / file）
│   └── platforms/
│       ├── discovery.py         # AST 解析上游源码，自动发现全部公开接口
│       ├── registry.py          # 命令注册表，碰撞解决
│       ├── invoke.py            # 动态加载上游模块并调用
│       ├── xhs/mapping.py       # 小红书命令 → 上游函数映射
│       ├── weibo/mapping.py     # 微博命令 → 上游函数映射
│       └── douyin/mapping.py    # 抖音命令 → 上游函数映射
├── aione/
│   ├── __init__.py
│   └── __main__.py              # python -m aione 入口
├── skills/
│   └── all-in-one/              # 统一 Agent Skill
├── tests/                       # 43 个测试（含 cookie 门控集成测试）
├── main.py                      # python main.py 入口
├── pyproject.toml               # 包配置 & 依赖
└── requirements.txt             # 依赖镜像
```

---

## 🧪 测试

```bash
# 运行全部单元测试
python -m pytest tests/ -v

# 仅运行真实接口测试（需要 cookie）
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