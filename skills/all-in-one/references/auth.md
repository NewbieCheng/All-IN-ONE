# Auth Reference

Cookie priority is shared across platforms:

1. `--cookies`
2. environment variable
3. saved local cookie

## Auth Profiles

Each platform has multiple auth profiles for different API domains:

- **XHS**: `pc` (default), `creator`, `pugongying`, `qianfan`
- **Weibo**: `web` (default), `creator`, `mobile`
- **DouYin**: `web` (default), `live`

Commands automatically use the correct profile. To save cookies for a specific profile:

```bash
aione auth xhs set-cookie --profile pc --cookie "<cookie>"
aione auth xhs set-cookie --profile creator --cookie "<cookie>"
aione auth weibo set-cookie --profile web --cookie "<cookie>"
aione auth douyin set-cookie --profile web --cookie "<cookie>"
aione auth douyin set-cookie --profile live --cookie "<cookie>"
```

Environment variables (default profile):

```bash
AIONE_XHS_COOKIES="<cookie>"
AIONE_WEIBO_COOKIES="<cookie>"
AIONE_DOUYIN_COOKIES="<cookie>"
```

Profile-specific environment variables:

```bash
AIONE_XHS_CREATOR_COOKIES="<cookie>"
AIONE_WEIBO_MOBILE_COOKIES="<cookie>"
AIONE_DOUYIN_LIVE_COOKIES="<cookie>"
```

## Saved Cookie Commands

```bash
aione auth xhs set-cookie --cookie "<cookie>"
aione auth xhs status
aione auth xhs clear-cookie

aione auth weibo set-cookie --cookie "<cookie>"
aione auth weibo status
aione auth weibo clear-cookie

aione auth douyin set-cookie --cookie "<cookie>"
aione auth douyin status
aione auth douyin clear-cookie
```

One-off cookie examples:

```bash
aione xhs note search --query "coffee" --cookies "<cookie>" --output json
aione weibo post search --query "AI" --page 1 --cookies "<cookie>" --output json
aione douyin work info --url "https://www.douyin.com/video/..." --cookies "<cookie>" --output json
```

If auth is missing, ask for a logged-in web cookie. If auth is expired or invalid, clear saved auth with:

```bash
aione auth <platform> clear-cookie
```
