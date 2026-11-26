# Copy a style from a video you like

You've watched a channel and thought: "I want my video to look like that." This page shows how to turn that feeling into inputs the agent can use: a short set of notes, a `brand.json` and a style brief.

The tokens it maps onto live in [`skills/video-basic/references/style.md`](../skills/video-basic/references/style.md) (shared by `video-basic` and `video-pro`). Read that first if you haven't; this page refers to its names.

## 1. Study the reference

Watch two or three videos from the channel, ideally one short and one long. Watch each twice: once for the content, once with the sound off to see only the look. Then fill in this worksheet.

| Area | What to write down | Example note |
|---|---|---|
| **Pacing** | Average beat length in seconds; cuts per minute; how long the first hook lasts | "A new idea every 4–6s; about 12 cuts a minute; hook is 5s" |
| **Layout** | Where the presenter's face sits and how big; where cards sit; how much empty space | "Face bottom-left in a rounded box; cards fill the right two thirds" |
| **Type** | Weight and size of titles; caption style (pill, outline, plain); how many words at once | "Very heavy titles; 2–4 word captions in a yellow pill" |
| **Colour** | Background colours (sampled, not guessed); card colour; one accent | "Purple-to-pink gradient; white cards; yellow accent" |
| **Motion** | How things enter (spring, slide, wipe); how fast; how text appears (typing, pop, wipe) | "Cards spring in with a small overshoot; commands type out" |
| **Sound** | Music energy; whether there are whooshes or clicks on transitions; voice pace | "Quiet music bed; soft click on each card" |

Tips:

- Count, don't feel. For pacing, play 60 seconds and tally the cuts.
- Sample colours with your OS colour picker rather than eyeballing them.
- Note the *job* each element does ("the pill names the pain") rather than just what it looks like. That is what carries over to your own topic.

## 2. Capture stills for your own reference

Pause on three to five beats (a title, a card, a terminal or code beat, a caption, the outro) and take a screenshot of each. Keep them in a private folder outside the repo.

These stills are for **describing the look to the agent and to yourself**. Never ship them: don't put them in your video, your repo or a PR. If you need a picture in your own docs, render one of your own beats (like [the preview in the README](preview.gif)) and use that.

## 3. Turn the notes into inputs

Two files do the work. Both are optional, and both are yours.

### `brand.json`: colours and fonts

Put it in your project root. The fields are listed in [the style guide](../skills/video-basic/references/style.md#brand). From the example notes above:

```json
{
  "name": "Acme CLI",
  "url": "acme.dev",
  "colors": { "accent": "#22c55e", "dark": "#0a1422", "light": "#f8fafc", "pill": "#ffd43b", "pillText": "#141420" },
  "backgrounds": ["#5b5cf0,#c26bd6", "#4f7cf7,#9a6df2"],
  "fonts": { "heading": "Inter Display", "body": "Inter", "mono": "DejaVu Sans Mono" }
}
```

Use your own accent and gradients, inspired by the reference rather than sampled from its logo. The agent reads these values over the defaults.

### A style brief: everything `brand.json` can't say

`brand.json` has no field for pacing or motion, so write a short brief (a few lines in your prompt, or a `STYLE-BRIEF.md` next to your project) that maps each observation to a token in the style guide:

| You observed | Write in the brief | Token it changes |
|---|---|---|
| Beats of 4–6s | "Keep scenes 4–6s; overlap neighbours by 0.4s" | Scene windows in `render(t)` |
| Cards bounce in | "Cards spring in, about 0.8s, small overshoot" | `spr()` helper and spring timing |
| Soft rounded cards | "Cards: white, radius 24px" | Card radius and shadow |
| Highlighted captions | "Captions: yellow pill, 60px, slight tilt, 2–4 words" | Caption pill size, colour, `rotate()` |
| Commands typed live | "Terminals type at 24 characters a second" | Typing effect rate |
| Fast pop-ins | "Stagger list items by 0.12s" | Stagger per item |
| Big faded word behind | "Add a big background word, 330px, 15% white" | Big background word |

Anything you can't map to a token, describe in plain words ("titles feel heavy and tight") and let the agent pick the closest values.

## 4. Prompt the agent

Give the agent your topic, the brand, and the brief together. A worked example:

> Make a 45-second video-basic video for my project, `acme-cli`. Use `brand.json` in the project root. Style brief: scenes of 4–6 seconds, overlapping by 0.4s; white cards with 24px radius that spring in over about 0.8s; 2–4 word captions in a yellow tilted pill; terminals that type real commands from the README. Presenter box on the left for the intro and outro. Write the spoken line for each beat so I can record it.

The agent will research the project, write beats, build `index.html` and render it. Look at the **first render as stills** (`python3 render.py stills index.html 4.0 12.5 20.0`) before you ask for a full video.

### Iterating

Change one thing at a time and name the beat, as in [Editing a video-basic video](EDITING-BASIC.md):

- "Captions pop faster: 0.3s wipe instead of 0.4s."
- "In the intro, cards slide in from the left instead of springing."
- "Make titles heavier and tighten the letter-spacing."
- "Cut each scene by about a second; the pace feels slow."

If a change keeps missing, add a number ("stagger 0.12s", "radius 32px") rather than an adjective.

## 5. What you can and can't copy

This is practical guidance, not legal advice.

**Fine to borrow:** pacing and rhythm; layout ideas (face in a corner, cards beside it); general aesthetics (bright gradients, rounded cards, bold captions); how a kind of beat is structured (problem, then steps, then payoff).

**Don't copy:** a channel's logo or mascot; its intro or outro sting; its music or sound effects; its footage, thumbnails or screenshots; its exact signature graphics, a distinctive animation or character that people recognise as *that channel*; its name or a lookalike of it.

A quick test: would a regular viewer of that channel think yours is theirs? If yes, change it. Make it your own: your brand colours, your own mascot or none, fictional names in sample UI, and your own music.

## Out of scope

The skills don't download videos, and there is no code here that fetches from YouTube. Watch the reference in your browser and take your own notes.
