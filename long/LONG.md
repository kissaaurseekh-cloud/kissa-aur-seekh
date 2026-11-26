# Weekly long video – instructions (v2, since 27 Nov 2026)

Every week the most-loved Short (Monday–Saturday) becomes a 16:9 long video on Sunday ~7 PM IST:
**the full traditional katha** behind that Short. Owner: Akshita. Fully automatic.
State lives in `log/weekly.json` (`weeks` list, newest last). "This week" = the coming/current Sunday's date.

Why v2 (channel data, Nov 2026): the first long video (an invented sequel, 3:55) got 25 views with 30 %
average viewed, and its "पूरी कहानी नीचे लिंक पर" teaser Short got 16 views. Long videos are found through
search and suggestions, so they need a searchable title, a thumbnail that reads at phone size, a strong first
15 seconds and steady pacing. The Monday teaser Short is discontinued.

Zapier YouTube app = `YouTubeV4CLIAPI`; always `inspect_zapier_actions` before executing.
English subtitles/localization and the first comment follow CLAUDE.md steps 6g–6i.
Raw file URL base: `https://raw.githubusercontent.com/kissaaurseekh-cloud/kissa-aur-seekh/main/`

## Saturday ~8 PM: pick the winner

1. If `log/weekly.json` already has an entry for this Sunday, stop (it was planned by hand).
2. Candidates: Shorts in `log/state.json` → `published` with a `date` from this Monday to Saturday.
   If fewer than 2 candidates, also include last week's. Skip stories that already have a long video.
3. Stats: YouTube `_zap_raw_request` Make API GET Request
   `https://www.googleapis.com/youtube/v3/videos?part=statistics&id=<comma-separated ids>`.
   Score = views + 25 × likes + 60 × comments. Highest score wins (ties → newer video).
4. Append `{"sunday": "<YYYY-MM-DD>", "pick": "<slug>", "pick_id": "<youtube id>", "status": "picked",
   "ranking": [[slug, views, likes, comments, score], ...]}` to `log/weekly.json`; commit and push.
5. SendUserMessage (Hindi-English mix is fine), e.g.:
   "Is hafte ki sabse pasand ki gayi Short: <title> (<views> views, <likes> likes). Kal Sunday 7 PM ko iski
   poori katha ka long video aayega. Koi aur story chahiye to Claude ko Sunday 12 baje tak bata dijiye." + the top-3 ranking.

## Sunday ~5:40 PM: make and publish the long video

1. Read this week's entry in `log/weekly.json`. If missing, do the Saturday step first. If `status` is not
   `picked`, stop. (If Akshita asked for a different story, the entry's `pick` has already been changed.)
2. `./setup.sh`. Read the picked Short's `stories/<slug>/script.py` and `render.py` to know the story and art.
3. Create `long/NN_<slug>_katha/` (NN = next number) by copying the code files of
   `long/01_aakhri_ghar_aage/` (lscript.py, lrender.py, lmix.py, make_vo.py, meta.json; not mp4/jpg/srt).
4. Story = **the full traditional katha** of the picked Short, told as one story, never invented events:
   the background (who the characters were, the boon/curse that set things up), the main episode in more
   detail, and the outcome as the scripture tells it (e.g. Gajendra Moksh: King Indradyumna and Agastya's
   curse, the gandharva Huhu and Devala's curse, the lake on Trikut, the long struggle, the stuti, Vishnu on
   Garuda, both freed). Check details against at least two reliable sources (the Purana itself, Ramayana /
   Mahabharata, Puranic Encyclopaedia, Wikipedia); word popular beliefs as "माना जाता है…".
   For non-mythology picks: a deeper version of the same story with the same lesson, no sequel cliffhangers.
   - Length 5–8 minutes, 14–20 scenes, 2–4 lines each. Speakers `F` (narrator, women, children, animals,
     deities' words in narration) and `M` (men). Kid-safe.
   - **First 15 seconds (cold open)**: start on the most dramatic moment (picture + one line), ask the big
     question, then promise what they'll get: "आज सुनिए इसकी पूरी कथा… और अंत में वो बात, जो बहुत कम लोग
     जानते हैं।" Voice from the first second. No slow title card, no recap of the Short, no "नमस्कार".
   - Keep a lesser-known detail for the last third (and actually deliver it) so people stay.
   - End: `lesson` (first line "सीख।" + 1–2 lines for "हम/आप" today) and a SHORT outro (≤ 6 s, one line:
     "ऐसी और कथाओं के लिए, चैनल को सब्सक्राइब करें।"). No long Like/Share/Subscribe sequence.
5. `lrender.py`: landscape 1920×1080, ground y=900, captions at the bottom. Rewrite the `s_<scene>` functions
   and `FN` with engine characters (sart.py: `shiv`, `parvati`, `kailash`, `cosmos`, `deva`, `asura`, `light_rays`;
   gnart.py: `ganesh`, `kartikeya`, `peacock`, `mushak`; vart.py: `vishnu`, `garuda`, `vishnu_garuda`, `chakra`,
   `magar`, `lotus`, `trikut`, `water_front`; hart.py: `man`, `elephant`; gart.py: `ramu`, `seth`, `house`;
   lart.py, tart.py, part.py, mart.py as before). Pacing: a new picture or a clear change every 3–5 s
   (camera push/pan, new label, a character entering), short music-only moments only at big turns
   (LEAD/TAIL ≤ 1.2 s, except one 2 s breath before the reveal). `lmix.py`: one mood per scene + fitting effects.
6. `meta.json` (no `teaser` key):
   - long.title (≤ 80 chars, search words first): `<Story name> Ki Poori Katha <emoji> <Deity> Ne … Kyun/Kaise …? | <Devanagari name> कथा`,
     e.g. "Gajendra Moksh Ki Poori Katha 🪷 Vishnu Ji Ne Haathi Ko Kaise Bachaya? | गजेंद्र मोक्ष कथा".
   - long.description: line 1 Hindi hook with the story name, line 2 Hinglish with the story + deity name,
     blank, 4–6 Hinglish sentences (story without the ending, 3–4 search phrases), `Katha: <source>`,
     `Seekh: …`, a line `CHAPTERS`, "1-minute version (Short): https://youtube.com/shorts/<pick_id>",
     the comment question, the channel line from CLAUDE.md, 5–7 hashtags.
   - long.tags: 12–18, story/deity names in English, Hinglish and Devanagari first ("gajendra moksh katha",
     "गजेंद्र मोक्ष", "vishnu bhagwan ki kahani", "bhagwat puran katha"…), then the general ones.
   - chapters {scene: "Hinglish chapter name"} (first scene first, ≥ 3 chapters, each ≥ 10 s).
   - thumb {scene, t, l1, l2}: the deity/hero BIG and bright on the right half, l1 = 2–3 words (the hook,
     e.g. "हाथी कैसे बचा?"), l2 = 1–3 words (e.g. "पूरी कथा"). Never a dark or tiny frame.
7. Build: `python3 engine/build_long.py long/NN_<slug>_katha` (~20 min). Check: view `sheet.jpg`,
   `thumbnail.jpg` AND `thumbnail_small.jpg` (320×180 = phone size: text readable, deity face clear).
   Also view frame 0 and the frame at 10 s of long.mp4. Fix visible problems and rebuild the bad scenes.
8. Commit and push (long.mp4, thumbnail.jpg, long_hi.srt, meta.json, code). Check the raw URL of long.mp4 returns 200.
9. Upload long.mp4: `upload_video` (public, made_for_kids false, category 27, default_language hi,
   default_audio_language hi, license youtube) → PUT status with `containsSyntheticMedia: true`
   (same body as CLAUDE.md step 6c) → `upload_video_thumbnail` (thumbnail.jpg) →
   `code_action_youtubev4cliapi__upload_caption_from_url` (long_hi.srt, hi) → English srt + localization +
   first comment as in CLAUDE.md 6g–6i → `add_video_to_playlist` into a long-video playlist: find
   "Bhagwan Ki Poori Kathayein | Hindi Bhakti Stories" with GET `playlists?part=snippet&mine=true&maxResults=50`;
   if missing, create it once (POST `playlists?part=snippet,status`, public) and save its id in `log/weekly.json`
   as `long_playlist_id`.
10. Add to the picked Short's description (GET then PUT `videos?part=snippet`, keep title/categoryId/tags/
    defaultLanguage): line 2 = "Poori katha (long video): https://youtu.be/<long id>".
11. Update the week entry: `status` = `long_published`, `long_folder`, `long_id`; commit, push.
12. SendUserMessage: long video link + "YouTube Studio (laptop) → Content → Shorts → <Short title> →
    Related video → choose the new long video → Save. Also add an end screen (Editor → End screen →
    'Best for viewer') to the long video." (The API can't set these two.)
