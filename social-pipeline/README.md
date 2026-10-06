# Playground Social Studio

A pipeline for social media production: brief in, posts out. Four Claude agents work in sequence, and the account team reviews and approves the results.

Live app: https://claude.ai/artifact/RB4BZEYSeiRaZxN3MQCtUx (private until shared from the page's Share menu)

## How it works

1. **Client profile.** Name, sector, language, tone of voice, brand colours, always/never rules, context, logos. Created once per client and used by every job.
2. **Job.** Platforms, number of posts, format, language, period, and the brief. Files are uploaded into four groups:
   - Briefing documents (PDF, Word, TXT). The text is extracted and added to the brief.
   - Visuals for the posts. Client-approved images the agents may place in posts.
   - References. Inspiration only. The art director reads them but never places them in a post.
   - Other client material.
3. **Agents** (run one by one, or all with "Run full pipeline"):
   - **Strategist.** Objective, audiences, key messages, pillars, mandatories, risks, the post plan, and the questions to send back to the client.
   - **Copywriter.** Hook, on-image headline and subline, caption, hashtags, CTA and alt text for each post. European Portuguese with pre-Agreement spelling, English, or both.
   - **Art director.** Looks at the logo, visuals and references, sets the palette and typography, chooses a layout and visual for each post, and writes an image-generation prompt when no suitable photo exists.
   - **Brand QA.** Scores each post from 1 to 5, flags unsupported claims, wrong language variety, clichés and risks, and suggests fixes.
4. **Review.** Every post renders as a proof at its real size (1080×1080, 1080×1350 or 1080×1920). The team can approve, edit, request changes, or send a post back to the copywriter with a note.
5. **Export.** A zip with every post as PNG, `captions.csv` (ready for a scheduler) and `strategy.json`.

## Technical notes

- Single HTML file (`studio.html`) published as a Claude Artifact.
- Storage: the artifact's shared database (`clients`, `jobs` collections) and its asset store for uploads.
- Agents: Claude calls from the page, on the viewer's own Claude account. Images are sent to the art director.
- PDF text is extracted with pdf.js, Word files with mammoth, and the zip is built with JSZip, all loaded from CDNs.

## Known limits

- Only people inside the organisation with edit access can upload. Clients can't upload directly. Collect files from the client (Drive folder, WeTransfer, email), then the account manager uploads them.
- The art director composes posts from the client's own visuals and typography. It does not generate photographs. When an image is missing it writes a prompt for Firefly, Midjourney or Canva, or for a photographer's brief.
- Publishing to social networks is not connected. Export the CSV and PNGs into the scheduler (Meta Business Suite, Hootsuite, Buffer, Metricool).
