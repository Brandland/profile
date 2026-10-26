# Playground website: review and improvements

This note covers what I found in the original prototype, what has been changed in this version, and what still needs a decision or input from Playground before launch.

## What was wrong with the original

The design direction is strong. The white space imagery, the orange accent and the editorial typography already feel more premium than most agency sites in the region. The problems were mostly in content, credibility and the technical basics.

**An internal note was visible to visitors.** The Insights page said "The insights section is designed to build authority around the issues Playground advises on, while giving clients a reason to return to the site." That is a brief for the designer, not copy for a client. It has been removed.

**Things looked clickable but were not.** Sector rows had arrows, insight cards had "read" arrows and service cards had "more" links, but none of them went anywhere. This erodes trust quickly, especially with senior visitors who scan. All of them now link to a real destination.

**Proof lived only on cards.** The work section showed titles and one line, with no page behind them. For clients like ExxonMobil, TotalEnergies or UNICEF, the case study is what procurement and communication heads actually read before shortlisting. There are now individual case study pages.

**No Portuguese version.** For a Maputo company, this was the biggest gap. Government, local corporates and many decision makers will search and read in Portuguese. The site is now fully bilingual, in European Portuguese with pre-Agreement spelling (projecto, objectivo, acção).

**The font was never loaded.** The CSS asks for Inter but the file was never included, so most visitors saw Arial or the system font. Inter is now bundled with the site.

**Sharing on LinkedIn would have shown no image.** The preview image used a relative path, which LinkedIn cannot read. There were also no canonical links, no language tags for Google and no structured data. All fixed.

**The contact form did nothing.** It showed "Thank you" without sending anything. There was no consent checkbox and no privacy policy. The WordPress version now sends real emails, with consent, spam protection and a privacy page (the policy text is a placeholder for your lawyer).

**The background images had the logo and tagline baked in.** These have been cleaned so the logo does not appear twice.

## What this version adds

The site now has nine page types in English and Portuguese: Home, Expertise, Sectors, Work, individual case studies, About, Insights, individual articles, Contact and Privacy.

The micro-animations are subtle on purpose. Headlines reveal word by word, the orbit lines in the hero draw themselves on load, numbers count up when they come into view, cards have a soft orange light that follows the cursor, buttons are slightly magnetic, the header hides when scrolling down and returns when scrolling up, and pages fade between each other. Everything switches off for visitors who have reduced motion enabled in their system settings.

The LinkedIn integration is covered in `wordpress/README.md`.

## What I need from Playground before launch

These are the items I could not do without you. Most of them matter more than any design change.

**1. Approved case studies.** The four case studies are illustrative. The structure is right, but the client names, numbers and quotes must come from real projects with client approval. I have marked uncertain values as "TBC" or "to confirm" and the pages show an "illustrative case" badge (in WordPress, only logged-in editors see it). My recommendation is to start with four to six cases, each with at least one hard result. A one-page case brief and a short approval email to each client will make this manageable for the team, without you writing them yourself.

**2. Client logos.** A strip of client logos is the fastest credibility signal on the home page. It needs permission from each client. Even six logos would be enough.

**3. Team.** The About page has a leadership section with your profile and two placeholders. Real names and photos of two or three senior people matter, because clients buy the team. It also shows that Playground is not dependent on one person, which supports your move towards a more strategic role.

**4. Contact details.** The phone number is a placeholder and the LinkedIn company URL needs confirming (`content/site.json`, or the Customizer in WordPress).

## Strategic recommendations

**Make stakeholder intelligence the flagship, not one card among eight.** Today the site still reads as an integrated agency with a long service list. If the direction is a Stakeholder Intelligence & Engagement Group, the site should show it. I would add one dedicated page for that offer, with the method, what a client actually receives (stakeholder maps, monthly intelligence briefs, dashboards) and a redacted example of the output. The idea of improving "the quality and value of stakeholder exchanges" should appear there. I have kept the hero line close to the original ("We help organisations move people") because changing the core positioning is your decision, not a web change. But I think the hero should eventually lead with the advisory position, and let creative and events support it.

**Publish less, but regularly.** One serious article a month is better than four thin ones. The first article, on stakeholder intelligence, is written and can be published as it is or adapted. Publish on the site first, then share the link on LinkedIn, so traffic comes back to Playground's own platform.

**Keep Southwise separate.** I have not added Southwise to this site. If you want a connection, a small footer line later is enough. Mixing the two brands now would weaken both.

## Technical recommendations for production

- Use managed WordPress hosting with daily backups and a staging site.
- Install **Polylang** (free) for the two languages. WPML also works but costs more and is heavier.
- Install **WP Mail SMTP** and connect it to the Playground mailbox. Without it, contact form emails from shared hosting often land in spam.
- Add analytics (GA4 or Plausible) behind the cookie banner that is already in place.
- Replace gradients on case studies with real project photography. This is the biggest visual upgrade still available.
- Run an accessibility check once real content is in. The base structure (skip link, focus states, reduced motion, labelled form fields) is in place.
