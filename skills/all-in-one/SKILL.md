---
name: all-in-one
description: Use when working with XHS, Weibo, or DouYin APIs through the local aione CLI, including search, user lookup, content detail, comments, auth cookies, dry-run checks, and agent workflows.
---

# All-IN-ONE Skill

Use one skill for all three platforms. The execution layer is always the local `aione` CLI; do not import upstream repositories directly from a skill.

Before running commands, load the relevant `references/` file:

- `references/auth.md`: shared cookie priority, save/status/clear, expired-cookie handling
- `references/xhs.md`: XHS command families and examples (86 commands)
- `references/weibo.md`: Weibo command families and examples (15 commands)
- `references/douyin.md`: DouYin command families and examples (45 commands)
- `references/workflows.md`: common cross-platform task flows

## Prerequisites

If `aione` command is not found, install it first:

```bash
pip install all-in-one-aione
aione setup
```

`aione setup` clones the three upstream repos and installs their npm dependencies. Requires `git` and `npm` in PATH.

For local development from source:

```bash
pip install -e .
aione setup
```

## Quick Start

Check command mapping without calling the API:

```bash
aione douyin work info --dry-run --url "https://www.douyin.com/video/example"
```

Save cookies for repeated use:

```bash
aione auth xhs set-cookie --cookie "<cookie>"
```

One-off cookie:

```bash
aione xhs note search --query "coffee" --page 1 --cookies "<cookie>" --output json
```

Debug with verbose mode (prints to stderr, never leaks cookies):

```bash
aione xhs user self-info --verbose --output json
```

Return concise results to the user. Keep raw JSON available when requested.
