# XHS Reference

Scope: `upstreams/Spider_XHS/apis`.

Important upstream files:

- `xhs_pc_apis.py`: feed, search, users, notes, comments, messages (32 commands)
- `xhs_pc_login_apis.py`: PC login helpers (11 commands)
- `xhs_creator_apis.py`: creator publishing and media (11 commands)
- `xhs_creator_login_apis.py`: creator login helpers (12 commands)
- `xhs_pugongying_apis.py`: PuGongYing influencer discovery (11 commands)
- `xhs_qianfan_apis.py`: QianFan distributor (9 commands)

Auth profiles: `pc`, `creator`, `pugongying`, `qianfan`

## Browsing (auth profile: pc)

```bash
aione xhs note search --query "coffee" --page 1 --output json
aione xhs note search-some --query "coffee" --require-num 50 --output json
aione xhs note info --url "<note_url>" --output json
aione xhs user info --user-id "<user_id>" --output json
aione xhs user self-info --output json
aione xhs user all-notes --user-url "<user_url>" --output json
aione xhs user search --query "<keyword>" --page 1 --output json
aione xhs note all-comment --url "<note_url>" --output json
aione xhs search keyword --word "<keyword>" --output json
aione xhs homefeed recommend-by-num --category "<category>" --require-num 20 --output json
aione xhs note no-water-img --img-url "<url>" --output json
aione xhs note no-water-video --note-id "<id>" --output json
aione xhs user all-like-note-info --user-url "<user_url>" --output json
aione xhs user all-collect-note-info --user-url "<user_url>" --output json
aione xhs likes all-andcollects --output json
aione xhs metions all --output json
aione xhs unread message --output json
```

## Creator (auth profile: creator)

```bash
aione xhs creator post-note --note-info "<json>" --output json
aione xhs media upload --path-or-file "<path>" --media-type image --output json
aione xhs topic get --keyword "<keyword>" --output json
aione xhs location info --keyword "<keyword>" --output json
aione xhs file ids --media-type image --output json
aione xhs transcode query --video-id "<id>" --output json
aione xhs publish note-info --page 1 --output json
aione xhs publish all-note-info --output json
aione xhs video extract-cover-and-metadata --video "<path>" --output json
```

## Login

```bash
aione xhs pc-login qrcode-login --output json
aione xhs pc-login phone-login --output json
aione xhs creator-login qrcode-login --output json
aione xhs creator-login check-session --output json
```

## PuGongYing (auth profile: pugongying)

```bash
aione xhs pugongying all-categories --output json
aione xhs pugongying user-by-page --page 1 --output json
aione xhs pugongying user-detail --user-id "<id>" --output json
aione xhs pugongying user-fans-detail --user-id "<id>" --output json
aione xhs pugongying send-invite --user-id "<id>" --product-name "<name>" --time "<time>" --invite-content "<content>" --contact-info "<info>" --output json
```

## QianFan (auth profile: qianfan)

```bash
aione xhs qianfan all-categories --output json
aione xhs qianfan user-by-page --choice "<choice>" --distribution-category "<cat>" --page 1 --output json
aione xhs qianfan user-detail --user-id "<id>" --output json
aione xhs qianfan user-cooperation --user-id "<id>" --output json
aione xhs qianfan user-shop --user-id "<id>" --output json
```

Profile-specific auth setup:

```bash
aione auth xhs set-cookie --profile pc --cookie "<cookie>"
aione auth xhs set-cookie --profile creator --cookie "<cookie>"
aione auth xhs set-cookie --profile pugongying --cookie "<cookie>"
aione auth xhs set-cookie --profile qianfan --cookie "<cookie>"
```
