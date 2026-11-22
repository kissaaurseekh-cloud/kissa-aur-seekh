# Kissa Aur Seekh – daily Short pipeline

This repo makes and publishes one vertical (1080×1920) Hindi moral-story YouTube Short a day
for the channel **Kissa Aur Seekh** (@KissaAurSeekh). Owner: Akshita. Publishing is fully automatic,
so quality checks below are mandatory.
Weekly long videos (Saturday pick, Sunday long video, Monday teaser) follow `long/LONG.md`.

## Daily run (do these in order)

1. `./setup.sh` (installs packages, downloads the AI4Bharat Hindi voice model ~1.5 GB).
2. Read `log/state.json`.
   - If `queue` is not empty, take the first item. If it has `"youtube_id"`, the video was already uploaded
     as private: skip building and uploading, run steps 6c–6f with that id, then step 7. Otherwise build it with its `cover` lines.
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
6. Upload with the Zapier MCP (YouTube app, `selected_api` = `YouTubeV4CLIAPI`). Always `inspect_zapier_actions` first.
   a. Fresh video: action `upload_video` with `video` = raw URL above, `title`, `description`, `tags` (list),
      `privacy_status` = `public`, `made_for_kids` = `false`, `category_id` = `27` (Education),
      `default_language` = `hi`, `default_audio_language` = `hi`, `license` = `youtube`. Note the returned `id`.
   b. Already-uploaded private video (queue item has `youtube_id`): skip 6a and use that id.
   c. Status + AI disclosure (both cases): action `_zap_raw_request` (tool `youtube_make_api_mutating_request`),
      `method` = `PUT`, `url` = `https://www.googleapis.com/youtube/v3/videos`, `querystring` = `{"part":"status"}`,
      `headers` = `{"Content-Type":"application/json"}`, `fail_on_errors` = `false`, `body` =
      `{"id":"<id>","status":{"privacyStatus":"public","selfDeclaredMadeForKids":false,"containsSyntheticMedia":true,"license":"youtube","embeddable":true,"publicStatsViewable":true}}`
      (PUT replaces the whole status, so send every field). Check the response says `"privacyStatus":"public"`.
   d. Thumbnail: action `upload_video_thumbnail` with `video_id` and `thumbnail` = raw URL of the cover jpg
      (skip if the queue item has "thumbnail_done": true).
   e. Playlist: action `add_video_to_playlist` (inspect it; resolve the playlist enum) into
      "1 Minute Moral Stories | Hindi Kahaniyan with Seekh" (id `PLD5ufVzMwbPM`).
   f. Hindi subtitles: action `code_action_youtubev4cliapi__upload_caption_from_url` (YouTube app) with
      `video_id`, `srt_url` = raw URL of `videos/NN_slug_hi.srt` (made by build.py; commit it in step 5),
      `language` = `hi`, `name` = `Hindi` (skip if the queue item has "captions_done": true).
      If this custom action is missing, recreate it with `write_code_action` (YouTube captions.insert,
      multipart upload, SRT downloaded from a public URL) and retry once; a failure here never blocks publishing.
   g. English subtitles: write `videos/NN_slug_en.srt` (same numbering and timings as the `_hi.srt`, each line
      translated into simple natural English; commit it in step 5) and upload it with the same caption action,
      `language` = `en`, `name` = `English` (skip if "captions_en_done": true). Never blocks publishing.
   h. English title/description (so the video also shows up for English-language viewers): `_zap_raw_request`
      PUT `https://www.googleapis.com/youtube/v3/videos`, `querystring` = `{"part":"localizations"}`, `body` =
      `{"id":"<id>","localizations":{"en":{"title":"<en_title>","description":"<en_description>"}}}`.
      If that errors, GET `videos?part=snippet` and PUT `part=snippet,localizations` with the full snippet
      (title, categoryId, description, tags, defaultLanguage `hi`) plus the localizations. Never blocks publishing.
   i. First comment: `_zap_raw_request` POST `https://www.googleapis.com/youtube/v3/commentThreads`,
      `querystring` = `{"part":"snippet"}`, body
      `{"snippet":{"videoId":"<id>","topLevelComment":{"snippet":{"textOriginal":"<comment>"}}}}`.
      Never blocks publishing.
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
  **Suspense hook is mandatory** (rule from Akshita, Nov 2026 – "हाथी और रस्सी" got ~500 views in a day
  with this style; the others got under 10). The first scene (2–4 s) must show a strange, visual mystery
  and ask WHY before any setup: e.g. "इतना बड़ा हाथी… पतली रस्सी से क्यों बंधा है?",
  "ये आदमी रोज़ खाली बाल्टी लेकर कुएँ पर क्यों जाता है?". Show the mysterious thing on screen with a big "?"
  and the title; never start with "एक गाँव में…". Reveal the answer only near the end (twist), then the lesson.
  Prefer stories with a visual puzzle, animals or everyday objects, and a mindset/life lesson.
  Cover lines and the video title must repeat the same mystery question.
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

## Metadata (every video) – written for maximum reach

Goal: get found in YouTube search and pushed in the Shorts feed by Hindi AND Hinglish/English searchers.
Put what people actually type first (deity/story names), keep the curiosity hook, and give every
video English subtitles + an English title/description (steps 6g–6h) and a question comment (step 6i).

- Title (≤ 70 chars; the first ~40 chars must work alone because the Shorts feed cuts the rest):
  `<Hinglish hook with the main keyword> <1 emoji> <short Devanagari keyword phrase> #shorts`.
  - God stories: name the deity in the hook in the way people search (Shiv Ji / Mahadev, Hanuman Ji,
    Krishna, Ganesh Ji…) and add the Devanagari phrase "<deity> की कहानी".
    e.g. `Shiv Ji Ne Zehar Kyun Piya? 😳 नीलकंठ की कहानी #shorts`
  - Other stories: `<hook> <emoji> हिंदी कहानी #shorts`,
    e.g. `Usne Sabse Kharab Ghar Banaya… Kiska Tha? 😳 हिंदी कहानी #shorts`
  - No ALL CAPS, no clickbait the video doesn't deliver.
- Description:
  1. Line 1: the Hindi hook, repeating the main keyword (e.g. "शिव जी ने ज़हर क्यों पिया? 🔱").
  2. Line 2: the same hook in Hinglish (e.g. "Shiv Ji ne zehar kyun piya? Neelkanth ki kahani").
  3. Blank line; 3–5 Hinglish sentences telling the story without the ending, naturally using 2–3 search
     phrases (story name, deity name, e.g. "samudra manthan", "Mahadev ki kahani").
  4. `Seekh: …`; for god stories also `Katha: <source>` (e.g. Shiv Puran / Bhagwat Puran / Ramayan).
  5. A question line that invites comments, e.g. "Aapko is kahani se kya seekh mili? Comment mein batayein 🙏".
  6. `Kissa Aur Seekh par roz milegi ek nayi 1-minute Hindi moral story. Kahani achhi lagi to Like, Share aur
     Subscribe zaroor karein!`
  7. Last line, 5–7 hashtags, most specific first (the first three show above the title):
     god stories e.g. `#mahadev #shivji #shorts #hindistory #bhakti #kissaaurseekh`;
     other stories e.g. `#shorts #hindistory #moralstory #hindikahani #motivation #kissaaurseekh`.
- Tags (≤ 500 chars total): story-specific first — 8–10 variants of the story/deity name in English,
  Hinglish and Devanagari (e.g. "neelkanth story", "shiv ji ki kahani", "शिव जी की कहानी", "samudra manthan",
  "mahadev story", "har har mahadev", "bhakti story") — then the general ones: hindi moral story,
  moral stories in hindi, hindi kahani, prerak kahani, 1 minute story, kissa aur seekh.
- English localization (step 6h): `en_title` = natural English version of the title keeping the keyword
  (e.g. "Why Did Lord Shiva Drink the Poison? 😳 Neelkanth Story #shorts"); `en_description` = 3–4 English
  lines (hook, story without ending, lesson) + the same hashtags.
- First comment (step 6i): one short Hinglish question that is easy to answer, e.g.
  "Agar aap wahan hote to kya karte? 🤔 Comment mein 'Har Har Mahadev' likhiye 🙏".
- Queue items may already carry `title`, `description`, `tags`, `en_title`, `en_description`, `comment`;
  use them as given.
