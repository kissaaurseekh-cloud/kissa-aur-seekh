# Kissa Aur Seekh – daily Short pipeline

This repo makes and publishes one vertical (1080×1920) Hindi moral-story YouTube Short a day
for the channel **Kissa Aur Seekh** (@KissaAurSeekh). Owner: Akshita. Publishing is fully automatic,
so quality checks below are mandatory.
Weekly long videos (Saturday pick, Sunday long video) follow `long/LONG.md`.

## Daily run (do these in order)

1. `./setup.sh` (installs packages, downloads the AI4Bharat Hindi voice model ~1.5 GB).
2. Read `log/state.json`.
   - If `queue` is not empty, take the first item. If it has `"youtube_id"`, the video was already uploaded
     as private: skip building and uploading, run steps 6c–6f with that id, then step 7. Otherwise build it with its `cover` lines.
   - If `queue` is empty, write a NEW story (next section) as `stories/NN_slug/`
     (NN = `next_number`).
3. Build: `python3 engine/build.py stories/NN_slug "<cover line 1>" "<cover line 2>" <hook_time>`
   → writes `videos/NN_slug.mp4` and `videos/NN_slug_cover.jpg` (~3 min).
4. Check: Read `stories/NN_slug/sheet.jpg` (still frames) and the cover jpg. Also pull frame 0, frame 8 and the last
   frame from the mp4 (`ffmpeg -vf "select='eq(n\,0)+eq(n\,8)+eq(n\,LAST)'",tile`) and view them: frame 0 must already
   show the big question text + the mystery thing (no black, no blink, nothing cut off), and the last frame must look
   like frame 0 (seamless loop). Check the length (`ffprobe`): 25–40 s. Fix anything broken
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

## Writing a new story (Short v2 format, since 27 Nov 2026)

Why this format (channel data, Nov 2026): 94 % of views come from the Shorts feed, and 54 % of viewers swiped
away in the first 1–2 s. People who stayed left at ~10 s (slow setup) and again when the सीख card and the 11 s
Like/Share/Subscribe outro started; under 2 % reached the end of the 57–65 s videos. Hits ("हाथी और रस्सी" 979,
"Ganesh parikrama" 917, "Neelkanth" 256) all opened with a visual "why/how?" puzzle; the slower, older-style
videos stayed under 50 views. Akshita's Instagram Reels show the same: lesser-known facts framed as a
contradiction, told fast (~45 s), beat well-known stories told slowly.

- Theme: stories from Hindu gods / mythology (see the scheduled task prompt for the weekday deity rule),
  traditional version only, deities respectful and recognisable, kid-safe. Avoid anything already in
  `published`/`queue` or `stories/`. No "why do we do this ritual" explainers (separate channel).
- Pick the ANGLE before the story: the best hooks are a CONTRADICTION or an impossible-looking picture —
  something great + something that seems wrong ("इतना बड़ा हाथी… पतली रस्सी से क्यों बंधा?",
  "शिव जी ने ज़हर क्यों पिया?", "ये हाथी सिर्फ़ एक कमल से कैसे बचा?"). Prefer a lesser-known episode or a
  lesser-known twist of a known one. If you can't write such a hook in ≤ 8 words, pick another story.
- START FROM `templates/short_v2/` (copy the folder to `stories/NN_slug/`): its `render.py` already has the v2
  timing (voice on frame 1, tiny gaps), the hook punch-in, a slow camera push on every scene, hard cuts,
  the one-line सीख scene and the 2–3 s looping outro; its `make_vo.py` speaks at atempo 1.17. Copy scene
  drawing code / characters from the older story folders as needed.
- `script.py` (same format): 7–9 scenes, ONE line per scene (two only for the सीख), each line ≤ ~3.5 s,
  total video **25–40 s** (speech ~22–35 s). Speakers: `F` = narrator (also non-human characters), `M` = men.
  - `hook` (≈2–2.5 s): the question itself, spoken from frame 1, ≤ 8 words, no "एक गाँव में…", no names the
    viewer doesn't know yet.
  - Scene 2 goes straight into the PROBLEM (no "एक दिन…" setup). Fold who/where into that line.
  - Every scene adds something new; re-raise the tension before the twist. Reveal the answer at ~70–80 %.
  - `lesson`: lines exactly `("F","सीख।")` + ONE short sentence for "हम/आप" today.
  - `outro`: exactly `("F","ऐसी कहानियों के लिए, सब्सक्राइब करें!", "ऐसी कहानियों के लिए, Subscribe करें!")`.
- `render.py`:
  - FRAME 1 RULE: `hook_scene()` draws the mystery thing big (filling most of the screen), bright, in
    motion; `hook_title()` draws the 2-line question (≤ 14 characters per line) at full opacity from frame 1,
    with "?" marks. No dark/night opening, no fade-in, no blink on frame 1 (`blink_off`).
  - `s_outro` draws `hook_scene()` + the SUBSCRIBE button and ends with `hook_title()` faded back in, so the
    last frame equals frame 1 (loop). Keep that structure.
  - Every scene: one big 1–3 word label at the top (e.g. "मगरमच्छ!", "हे नारायण!"), shown from the start
    of the scene. Something moves in every scene.
  - Reuse characters from `engine/` (`ramu`, `seth`, `house` in gart.py; `man`, `elephant`, `rope`,
    `mela_bg` in hart.py; `raghu`, `pot`, `village`, `flower` in part.py; `boy`, `dadaji`, `butterfly`,
    `cocoon`, `garden` in tart.py; `frog`, `room`, `big_pot`, `milk` in mart.py; `shiv`, `parvati`,
    `kailash`, `cosmos`, `deva`, `asura` in sart.py; `ganesh`, `kartikeya`, `peacock`, `mushak` in gnart.py;
    `vishnu`, `garuda`, `vishnu_garuda`, `chakra`, `magar`, `lotus`, `trikut`, `water_front` in vart.py).
    New simple shapes are fine (skia drawing). Captions sit at y≈1440; keep characters above y≈1350 and
    nothing important below y≈1650.
- `mix.py`: a sound hit on frame 1 (stinger) and music already playing (no fade-in); one mood per scene
  plus 1–3 effects; voice clearly louder than music (ducking is in the file).
  Scene-change sound = the template's `soft_swish()` only (≈19 dB under the voice). Never add loud or bright
  whooshes at cuts or repeating whooshes/wing-flaps (Akshita: the old cut whoosh was disturbing).
- Cover lines (thumbnail): 2 short Hindi lines (≤ 14 characters each) = the hook question split in two,
  e.g. "हाथी कमल से" / "कैसे बचा?". hook_time ≈ 1.0.

## Metadata (every video) – written for maximum reach

Goal: get found in YouTube search and pushed in the Shorts feed by Hindi AND Hinglish/English searchers.
Put what people actually type first (deity/story names), keep the curiosity hook, and give every
video English subtitles + an English title/description (steps 6g–6h) and a question comment (step 6i).

- Title (≤ 70 chars; the first ~40 chars must work alone because the Shorts feed cuts the rest):
  `<deity name first + the hook question in Hinglish> <1 emoji> <Devanagari story/deity keyword> #shorts`.
  The title must ask the SAME question as the video's hook. Name the deity the way people search
  (Shiv Ji / Mahadev, Hanuman Ji, Krishna, Ganesh Ji, Vishnu Ji…) and add "<story or deity> की कहानी".
  e.g. `Shiv Ji Ne Zehar Kyun Piya? 😳 नीलकंठ की कहानी #shorts`,
  `Vishnu Ji Ne Ek Kamal Ke Liye Haathi Kyun Bachaya? 🪷 गजेंद्र मोक्ष #shorts`.
  No ALL CAPS, no clickbait the video doesn't deliver.
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
- Never make "part 2 / poori kahani neeche link par" teaser Shorts (they got 16 and 25 views).
- Queue items may already carry `title`, `description`, `tags`, `en_title`, `en_description`, `comment`;
  use them as given.
