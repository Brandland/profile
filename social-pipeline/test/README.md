# Tests

End-to-end tests for `studio.html` in headless Chromium, with a fake Claude runtime
(`fake-runtime.js`) that stands in for the artifact's database, file storage, downloads,
Canva connector and Claude calls. `server.js` serves the page and answers the agents with
canned replies; the art director's replies are the hand-made designs in `designs.js`.

```
npm install
python3 make-assets.py      # synthetic photos, references, logo and briefing documents
node server.js &            # http://localhost:8765
node run.js                 # full pipeline, both languages, exports, revisions
node run2.js                # brand font, Canva link-only and failure, legacy job, no-image view
node run3.js                # a broken design is sent back to the art director and repaired
```

Screenshots, rendered posts, the prompts the agents received and the downloads land in `out/`.
These tests check the page's mechanics. They do not judge the quality of real Claude output.
