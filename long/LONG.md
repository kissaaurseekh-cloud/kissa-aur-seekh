# Weekly long video – instructions

Every week the most-loved Short (Monday–Saturday) becomes a 16:9 long video on Sunday ~7 PM IST,
plus a vertical teaser Short on Monday ~1 PM IST that links to it. Owner: Akshita. Fully automatic.
State lives in `log/weekly.json` (`weeks` list, newest last). "This week" = the coming/current Sunday's date.

Zapier YouTube app = `YouTubeV4CLIAPI`; always `inspect_zapier_actions` before executing.
Raw file URL base: `https://raw.githubusercontent.com/kissaaurseekh-cloud/kissa-aur-seekh/main/`

## Saturday ~8 PM: pick the winner

1. If `log/weekly.json` already has an entry for this Sunday, stop (it was planned by hand).
2. Candidates: Shorts in `log/state.json` → `published` with a `date` from this Monday to Saturday
   (Shorts only; skip teasers). If fewer than 2 candidates, also include last week's.
3. Stats: YouTube `_zap_raw_request` Make API GET Request
   `https://www.googleapis.com/youtube/v3/videos?part=statistics&id=<comma-separated ids>`.
   Score = views + 25 × likes + 60 × comments. Highest score wins (ties → newer video).
4. Append `{"sunday": "<YYYY-MM-DD>", "pick": "<slug>", "pick_id": "<youtube id>", "status": "picked",
   "ranking": [[slug, views, likes, comments, score], ...]}` to `log/weekly.json`; commit and push.
5. SendUserMessage (Hindi-English mix is fine), e.g.:
   "Is hafte ki sabse pasand ki gayi Short: <title> (<views> views, <likes> likes). Kal Sunday 7 PM ko iska
   long video aayega. Koi aur story chahiye to Claude ko Sunday 12 baje tak bata dijiye." + the top-3 ranking.

## Sunday ~5:40 PM: make and publish the long video

1. Read this week's entry in `log/weekly.json`. If missing, do the Saturday step first. If `status` is not
   `picked`, stop. (If Akshita asked for a different story, the entry's `pick` has already been changed.)
2. `./setup.sh`. Read the picked Short's `stories/<slug>/script.py` to know the story.
3. Create `long/NN_<slug>_long/` (NN = next number) by copying `long/01_aakhri_ghar_aage/`
   (lscript.py, lrender.py, lmix.py, make_vo.py, meta.json; not the mp4/jpg/srt files).
4. Write a **sequel or deeper version** of the Short: 10–12 scenes, about 4–6 minutes, one emotional turn,
   the same lesson made stronger. Open with a 10–15 s storm/title hook and a short recap of the Short,
   end with the `lesson` (first line "सीख।") and the unchanged `outro`. Speakers `F` (narrator, women,
   children, animals) and `M` (men). Kid-safe.
5. `lrender.py`: rewrite the `s_<scene>` functions and `FN` with engine characters (lart.py: `kamla`,
   `bucket`, `cart`, `rain`, `tint`, `big_brick`, `lsky`, `lground`, `far_houses`; gart.py: `ramu`, `seth`,
   `house`; hart.py: `man`, `elephant`; tart.py: `boy`, `dadaji`, `butterfly`, `cocoon`; part.py: `pot`,
   `raghu`; mart.py: `frog`, `room`, `big_pot`). Landscape 1920×1080, ground y=900, captions at the bottom.
   Keep the title card text in `s_<first scene>`; update LEAD/TAIL so there are short music-only moments.
   `lmix.py`: one mood per scene + fitting effects (copy the helper style already there).
6. `meta.json`: long {title "<Story> – Aage Kya Hua? … | Hindi Moral Story | Kissa Aur Seekh",
   description with a line `CHAPTERS` where chapters go and "Pehla part (Short): https://youtube.com/shorts/<pick_id>",
   tags}, chapters {scene: name} (first scene first), thumb {scene, t, l1, l2}, teaser {title, description
   containing LONG_URL, tags, scenes [2 consecutive scenes, ~45–50 s, ending before the resolution],
   top [2 lines], end_line, end_text [3 lines]}.
7. Build: `python3 engine/build_long.py long/NN_<slug>_long` (~20 min). Then check: view
   `long/NN_<slug>_long/sheet.jpg` and `thumbnail.jpg`; fix visible problems and rebuild the bad scenes.
8. Commit and push (long.mp4, teaser.mp4, thumbnail.jpg, long_hi.srt, meta.json, code). Check the raw URL of
   long.mp4 returns 200.
9. Upload long.mp4: `upload_video` (public, made_for_kids false, category 27, default_language hi,
   default_audio_language hi, license youtube) → then PUT status with `containsSyntheticMedia: true`
   (same body as CLAUDE.md step 6c) → `upload_video_thumbnail` (thumbnail.jpg) →
   `code_action_youtubev4cliapi__upload_caption_from_url` (long_hi.srt) → `add_video_to_playlist` (PLD5ufVzMwbPM).
10. Add to the picked Short's description (GET then PUT `videos?part=snippet`, keep title/categoryId/tags):
    line 2 = "Aage kya hua? Poori kahani dekhiye: https://youtu.be/<long id>".
11. Update the week entry: `status` = `long_published`, `long_folder`, `long_id`; commit, push.
12. SendUserMessage: long video link + "YouTube Studio (laptop) → Content → Shorts → <Short title> →
    Related video → choose the new long video → Save."

## Monday ~12:50 PM: publish the teaser

1. This week's entry must have `status` = `long_published`; otherwise stop.
2. In its folder's meta.json teaser description replace LONG_URL with `https://youtu.be/<long id>`.
3. `upload_video` teaser.mp4 (public, same settings), PUT status with `containsSyntheticMedia: true`,
   `add_video_to_playlist` (PLD5ufVzMwbPM).
4. Entry: `status` = `teaser_published`, `teaser_id`; commit, push.
5. SendUserMessage: teaser link + "Related video → choose the long video → Save" reminder.
