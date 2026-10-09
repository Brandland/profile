# Playground Social Studio

A pipeline for social media production: brief in, posts out. Claude agents work in sequence and the account team reviews and approves the results. Every post is produced in Portuguese for Mozambique (PT-MZ) and English for South Africa (EN-ZA).

Live app: https://claude.ai/artifact/RB4BZEYSeiRaZxN3MQCtUx (private until shared from the page's Share menu)

## How a job works

1. **Client profile.** Name, sector, handles, tone of voice, brand colours, always/never rules, visual identity notes, logos and brand fonts. Created once per client.
2. **Job.** Platforms, number of posts, main format, languages (PT-MZ + EN-ZA by default), period and the brief. Files go into three groups:
   - **Briefing and brand documents** (PDF, Word, PowerPoint, TXT). The text goes into the brief. Pages and pictures inside the documents are extracted so the agents can see them and use them.
   - **Photos and graphics to use.** The art director places these in the posts.
   - **Style references.** Posts, campaigns or moodboards the client likes. The art director studies them and designs in that direction.
   Each image has a role chip (use / style / skip) that the image analyst sets and the team can change with one click.
3. **Agents** (one at a time, or all with "Run full pipeline"):
   - **Strategist.** Objective, audiences, messages, pillars, mandatories, risks, the post plan and the questions to send back to the client. It also reads the pages of the briefing documents.
   - **Copywriter.** For each post, in both languages: kicker, headline, subline, body, call to action and footnote for the image, plus caption, hashtags and alt text. Portuguese follows the Mozambican norm with pre-Agreement spelling; English follows South African usage.
   - **Art director.** First an image analyst describes every uploaded image (subject, colours, focal point, calm areas for text, whether it can be used or is only a style reference). Then the art director sets the campaign direction: the big idea, what it takes from each reference, palette, typography, graphic devices and which image goes in which post. Then it designs each post, renders it, looks at its own render in both languages and corrects it.
   - **Brand QA.** Checks both language versions and the rendered designs against the brief, the language rules and risk, scores each post and proposes text fixes.
4. **Review.** Every post shows as a full-size proof, with a PT-MZ / EN-ZA switch. The team can approve, edit the text, ask for another design, go back to the previous design, or send a change request to the copywriter or the art director.
5. **Export.** A zip with PNGs for each language, editable SVGs (open in Illustrator or Figma), `captions.csv` with both languages, the strategy and the art direction.

## The design engine

The art director writes each post as four layers:

1. a background SVG with everything visual: colour fields, the client's photos (placed and cropped by code), masks, shapes, patterns, illustration, grain;
2. text boxes, set by the page with real fonts (17 Google Fonts plus the client's own brand fonts). The page wraps lines and shrinks the size to fit, separately for each language;
3. an optional foreground SVG over the text;
4. the logo, which the page places in a box and can show in white, black or any colour. Logos saved as JPEG on a plain light background are cleaned up automatically.

Because the agent writes real vector artwork, it can create original graphics (illustrations, patterns, compositions) when no photo fits, and it can use every photo it is given. If a design fails to render, the page sends the error back to the agent to repair it.

## Canva (beta, unverified)

When the Canva connector is connected, the art director can ask Canva to generate an image for a post that has no suitable photo, and then use it. This part has not been tested against the real Canva connector. If Canva only returns a link, the post shows "Open generated image" so the image can be downloaded and added to the job by hand.

## Known limits

- Only people inside the organisation with edit access can upload. Clients can't upload directly; the account manager adds their files.
- The agents run on the viewer's own Claude account. Each person who runs them needs Claude access.
- Image understanding needs a view that can send images to Claude (Claude in a desktop browser). The page warns when it can't.
- The "Best" design mode uses the strongest model and a self-review per post, so a 6-post job takes several minutes. "Fast" mode is quicker and lighter.
- Publishing to social networks is not connected. Load the CSV and PNGs into the scheduler (Meta Business Suite, Hootsuite, Buffer, Metricool).

## Files

- `studio.html`: the whole app (published as a Claude Artifact).
- `test/`: local end-to-end tests with a fake Claude runtime. See `test/README.md`.
