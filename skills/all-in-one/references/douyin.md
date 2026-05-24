# DouYin Reference

Scope: `upstreams/DouYin_Spider/dy_apis/douyin_api.py` (45 commands).

Excluded: `dy_apis/login_api.py`, `dy_apis/douyin_recv_msg.py`

Auth profiles: `web`, `live`

## User (auth profile: web)

```bash
aione douyin user info --user-url "<user_url>" --output json
aione douyin user work-info --user-url "<user_url>" --output json
aione douyin user all-work-info --user-url "<user_url>" --output json
aione douyin user favorite --sec-id "<sec_id>" --output json
aione douyin user follower-list --user-id "<id>" --sec-id "<sec_id>" --output json
aione douyin user some-follower-list --user-id "<id>" --sec-id "<sec_id>" --num 100 --output json
aione douyin user following-list --user-id "<id>" --sec-id "<sec_id>" --output json
aione douyin user some-following-list --user-id "<id>" --sec-id "<sec_id>" --num 100 --output json
aione douyin user search --query "<keyword>" --output json
aione douyin user search-some --query "<keyword>" --num 50 --output json
aione douyin uid self --output json
aione douyin sec self-uid --output json
```

## Work / Video (auth profile: web)

```bash
aione douyin work info --url "https://www.douyin.com/video/..." --output json
aione douyin work search-some-general --query "coffee" --num 20 --output json
aione douyin work search-general --query "coffee" --offset 0 --output json
aione douyin work search-some-video --query "coffee" --num 16 --output json
aione douyin work search-video --query "coffee" --offset 0 --output json
aione douyin work all-comment --url "<video_url>" --output json
aione douyin work all-out-comment --url "<video_url>" --output json
aione douyin work out-comment --url "<video_url>" --cursor 0 --output json
aione douyin work all-inner-comment --comment "<comment_id>" --output json
aione douyin work inner-comment --comment "<comment_id>" --cursor 0 --output json
```

## Interaction (auth profile: web)

```bash
aione douyin digg digg --aweme-id "<id>" --output json
aione douyin comment publish --aweme-id "<id>" --content "<text>" --output json
aione douyin aweme collect --aweme-id "<id>" --output json
aione douyin collect list --output json
aione douyin collect move-aweme --aweme-id "<id>" --collect-name "<name>" --collect-id "<id>" --output json
aione douyin collect remove-aweme --aweme-id "<id>" --collect-name "<name>" --collect-id "<id>" --output json
```

## Feed / Notice / Message (auth profile: web)

```bash
aione douyin feed get --output json
aione douyin notice list --output json
aione douyin notice some-list --num 20 --output json
aione douyin conversation create --to-user-id "<id>" --output json
aione douyin conversation list --aweme-id "<id>" --output json
aione douyin msg send --conversation-id "<id>" --conversation-short-id "<id>" --ticket "<ticket>" --content "<text>" --output json
aione douyin device id --output json
aione douyin webcast detail --user-id "<id>" --room-id "<id>" --url "<url>" --output json
```

## Live (auth profile: live)

```bash
aione douyin live search --query "music" --num 25 --output json
aione douyin live search-some --query "music" --num 10 --output json
aione douyin live info --live-id "<id>" --output json
aione douyin live production --url "<live_url>" --room-id "<id>" --author-id "<id>" --offset 0 --output json
aione douyin live all-production --url "<live_url>" --output json
aione douyin live production-detail --url "<url>" --ec-promotion-id "<id>" --sec-author-id "<id>" --live-room-id "<id>" --output json
aione douyin live digg-room --room-id "<id>" --output json
aione douyin msg send-in-room --room-id "<id>" --content "<text>" --output json
aione douyin rank list --room-id "<id>" --anchor-id "<id>" --sec-anchor-id "<id>" --output json
```

Profile-specific auth setup:

```bash
aione auth douyin set-cookie --profile web --cookie "<cookie>"
aione auth douyin set-cookie --profile live --cookie "<cookie>"
```
