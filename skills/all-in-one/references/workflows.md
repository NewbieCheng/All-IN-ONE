# Cross-Platform Workflows

## First Step For Any Request

Use `--dry-run` first when checking a command path or when no cookie is available:

```bash
aione xhs note search --query "coffee" --page 1 --dry-run
aione weibo post search --query "AI" --page 1 --dry-run
aione douyin work info --url "https://www.douyin.com/video/example" --dry-run
```

## Search

```bash
aione xhs note search --query "<keyword>" --page 1 --output json
aione xhs note search-some --query "<keyword>" --require-num 50 --output json
aione weibo post search --query "<keyword>" --page 1 --output json
aione douyin work search-some-general --query "<keyword>" --num 20 --output json
```

## Content Detail

```bash
aione xhs note info --url "<note_url>" --output json
aione weibo work info --url "<post_url>" --output json
aione douyin work info --url "<douyin_video_url>" --output json
```

## User Detail

```bash
aione xhs user info --user-id "<user_id>" --output json
aione xhs user self-info --output json
aione weibo user info --user-id "<user_id>" --output json
aione weibo info self --output json
aione douyin user info --user-url "<user_url>" --output json
aione douyin uid self --output json
```

## Comments

```bash
aione xhs note all-comment --url "<note_url>" --output json
aione weibo word comments --user-id "<id>" --mid "<mid>" --output json
aione douyin work all-comment --url "<video_url>" --output json
```

## User Content List

```bash
aione xhs user all-notes --user-url "<user_url>" --output json
aione weibo user all-posted --user-url "<user_url>" --output json
aione douyin user all-work-info --user-url "<user_url>" --output json
```

## Publishing (Creator)

XHS:
```bash
aione xhs media upload --path-or-file "<path>" --media-type image --output json
aione xhs creator post-note --note-info "<json>" --output json
```

Weibo:
```bash
aione weibo image upload-file --uid "<uid>" --nick "<nick>" --file "<path>" --output json
aione weibo weibo post --note-info "<json>" --output json
```

## Live Stream (DouYin)

```bash
aione douyin live search --query "music" --num 25 --output json
aione douyin live info --live-id "<id>" --output json
aione douyin live all-production --url "<live_url>" --output json
aione douyin live digg-room --room-id "<id>" --output json
aione douyin msg send-in-room --room-id "<id>" --content "<text>" --output json
```

## Interaction

```bash
aione douyin digg digg --aweme-id "<id>" --output json
aione douyin comment publish --aweme-id "<id>" --content "<text>" --output json
aione douyin aweme collect --aweme-id "<id>" --output json
```

## Real CLI Test Inputs

To run real platform tests, ask the user for:

- XHS logged-in web cookie
- Weibo logged-in web cookie
- DouYin logged-in `www.douyin.com` cookie
- A DouYin video URL for `work info`

Do not print raw cookies in summaries.
