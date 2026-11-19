# Kissa Aur Seekh – daily Short pipeline

This repo makes and publishes one vertical (1080×1920) Hindi moral-story YouTube Short a day
for the channel **Kissa Aur Seekh** (@KissaAurSeekh). Owner: Akshita. Publishing is fully automatic,
so quality checks below are mandatory.

## Daily run (do these in order)

1. `./setup.sh` (installs packages, downloads the AI4Bharat Hindi voice model ~1.5 GB).
2. Read `log/state.json`.
   - If `queue` is not empty, take the first item. If it has `"youtube_id"`, the video was already uploaded
     as private: just publish it (step 6b) and skip to step 7. Otherwise build it with its `cover` lines.
   - If `queue` is empty, write a NEW story (next section) as `stories/NN_slug/`
     (NN = `next_number`).
3. Build: `python3 engine/build.py stories/NN_slug "<cover line 1>" "<cover line 2>" <hook_time>`
   → writes `videos/NN_slug.mp4` and `videos/NN_slug_cover.jpg` (~3 min).
4. Check: Read `stories/NN_slug/sheet.jpg` (20 still frames) and the cover jpg. Fix anything broken
   (overlapping text, characters off-screen, black areas, unreadable captions, a scene that doesn't match
   its line) and rebuild. Do not publish a video with visible problems.
5. Commit and push: `git add -A && git commit -m "Story NN: <title>" && git -c push.negotiate=true push`.
   Video URL = `https://raw.githubusercontent.com/kissaaurseekh-cloud/kissa-aur-seekh/main/videos/NN_slug.mp4`
   (check it returns 200 with `curl -sI`).
6. Upload with the Zapier MCP: YouTube (`YouTubeV4CLIAPI`) action `upload_video`:
   - `video` = raw URL above, `thumbnail` = raw URL of the cover jpg
   - `title`, `description`, `tags` (list) – see "Metadata" below
   - `privacy_status` = `public`, `made_for_kids` = `false`, `category_id` = `27` (Education),
     `default_language` = `hi`, `default_audio_language` = `hi`, `notify_subscribers` = `true`
   - 6b. Publishing an already-uploaded private video: YouTube `_zap_raw_request` (Make API Mutating Request)
     `PUT https://www.googleapis.com/youtube/v3/videos?part=status` body
     `{"id":"<id>","status":{"privacyStatus":"public","selfDeclaredMadeForKids":false,"containsSyntheticMedia":true}}`
   - After a fresh upload, set the AI disclosure the same way:
     `{"id":"<id>","status":{"privacyStatus":"public","selfDeclaredMadeForKids":false,"containsSyntheticMedia":true}}`
   - Add it to the playlist "1 Minute Moral Stories | Hindi Kahaniyan" (action `add_video_to_playlist`) if found.
7. Update `log/state.json`: move the item to `published` (slug, title, youtube_id, date), increase
   `next_number` if a new story was made, and delete `videos/*.mp4` older than the 3 newest to keep the repo
   small (`git rm`). Commit and push.
8. Final message: the title and YouTube link.

## Writing a new story

- Original, simple Indian setting, one clear twist, one lesson. Avoid anything already in `published`/`queue`
  or `stories/`. Good sources of ideas: classic Indian folk/Panchatantra/Akbar-Birbal style tales retold in
  your own words, everyday-life parables. Kid-safe for all ages (no gore, no scary death scenes).
- Copy the story folder closest in look as a template: village/houses (01), fair + elephant (02),
  village path + pots (03), garden + boy/grandfather + butterfly (04), night kitchen + frogs (05).
- `script.py`: same format. Speakers: `F` = female narrator (also voices non-human characters),
  `M` = male voice for men. 8–10 scenes, total speech **50–58 s**. Short spoken sentences, commas for pauses.
  Hook first scene: a question/shock that makes viewers stay ("…आखिर क्यों?").
  Keep the `lesson` scene (first line exactly "सीख।") and the `outro` scene **unchanged** (English
  LIKE / SHARE / SUBSCRIBE buttons are drawn by `s_outro`).
- `render.py`: change the `s_<scene>` functions and the `FN = dict(...)` map. Reuse characters from
  `engine/` (`ramu`, `seth`, `house` in gart.py; `man`, `elephant`, `rope`, `mela_bg` in hart.py;
  `raghu`, `pot`, `village`, `flower` in part.py; `boy`, `dadaji`, `butterfly`, `cocoon`, `garden` in tart.py;
  `frog`, `room`, `big_pot`, `milk` in mart.py). New simple shapes are fine (skia drawing).
  Captions sit at y≈1440; keep characters above y≈1350 and nothing important below y≈1650.
- `mix.py`: give each scene a mood (pad/marimba/pluck/heartbeat/riser/stinger helpers) plus 2–4 fitting
  sound effects. Keep voice clearly louder than music (ducking is already in the file).
- Cover lines: 2 short Hindi lines (≤ 22 characters each) that tease the twist, e.g. "सबसे खराब घर…" / "किसका था?".

## Metadata (every video)

- Title (≤ 100 chars): Hinglish hook + emoji + `| Hindi Moral Story #shorts`
  e.g. `Usne Sabse Kharab Ghar Banaya… Phir Pata Chala Woh Kiska Hai 😳 | Hindi Moral Story #shorts`
- Description: line 1 the Hindi hook; blank line; 3–5 Hinglish sentences telling the story without the
  ending; `Seekh: …`; `Kissa Aur Seekh par roz milegi ek nayi 1-minute Hindi moral story. Kahani achhi lagi to
  Like, Share aur Subscribe zaroor karein!`; then
  `#shorts #hindistory #moralstory #hindikahani #motivation #kissaaurseekh` (+1–2 topic tags).
- Tags (≤ 500 chars total): hindi moral story, moral stories in hindi, hindi kahani, hindi kahaniyan,
  motivational story in hindi, prerak kahani, hindi short story, 1 minute story, kissa aur seekh,
  + 6–8 story-specific ones (English and Hinglish names of the story).
