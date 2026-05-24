# Weibo Reference

Scope: `upstreams/WeiboApis/apis`.

Important upstream files:

- `weibo_apis.py`: self, user, post, comments, search (7 commands)
- `weibo_creator_apis.py`: video upload and publish (6 commands)
- `weibo_mobile_apis.py`: mobile work info and search (2 commands)

Auth profiles: `web`, `creator`, `mobile`

## Browsing (auth profile: web)

```bash
aione weibo info self --output json
aione weibo user info --user-id "<user_id>" --output json
aione weibo user posted --user-id "<id>" --page 1 --output json
aione weibo user all-posted --user-url "<user_url>" --output json
aione weibo post search --query "AI" --page 1 --output json
aione weibo work info --url "<post_url>" --output json
aione weibo word comments --user-id "<id>" --mid "<mid>" --output json
```

## Creator (auth profile: creator)

```bash
aione weibo weibo post --note-info "<json>" --output json
aione weibo image upload-file --uid "<uid>" --nick "<nick>" --file "<path>" --output json
aione weibo init video --file "<path>" --output json
aione weibo video upload-file --upload-id "<id>" --media-id "<id>" --file "<path>" --auth "<auth>" --output json
aione weibo check video --upload-id "<id>" --media-id "<id>" --file-size "<size>" --auth "<auth>" --output json
aione weibo output video --media-id "<id>" --output json
```

## Mobile (auth profile: mobile)

```bash
aione weibo mobile search --query "AI" --page 1 --output json
aione weibo mobile work-info --work-id "<id>" --output json
```

Profile-specific auth setup:

```bash
aione auth weibo set-cookie --profile web --cookie "<cookie>"
aione auth weibo set-cookie --profile creator --cookie "<cookie>"
aione auth weibo set-cookie --profile mobile --cookie "<cookie>"
```
