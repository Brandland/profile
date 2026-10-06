const {chromium}=require('playwright-core');const fs=require('fs'),path=require('path');
const A=p=>path.join(__dirname,'assets',p);const OUT=path.join(__dirname,'out');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const ctx=await b.newContext({viewport:{width:1360,height:1000},deviceScaleFactor:1});
  await ctx.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/pdf\.js\/3\.11\.174\/pdf\.min\.js/,r=>r.fulfill({path:path.join(__dirname,'node_modules/pdfjs-dist/build/pdf.min.js'),contentType:'text/javascript'}));
  await ctx.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/pdf\.js\/3\.11\.174\/pdf\.worker\.min\.js/,r=>r.fulfill({path:path.join(__dirname,'node_modules/pdfjs-dist/build/pdf.worker.min.js'),contentType:'text/javascript'}));
  await ctx.route(/cdnjs\.cloudflare\.com\/ajax\/libs\/jszip/,r=>r.fulfill({path:path.join(__dirname,'node_modules/jszip/dist/jszip.min.js'),contentType:'text/javascript'}));
  await ctx.addInitScript({path:path.join(__dirname,'fake-runtime.js')});
  const page=await ctx.newPage();const errors=[];
  page.on('pageerror',e=>errors.push('pageerror: '+e.message));page.on('console',m=>{if(m.type()==='error') errors.push('console: '+m.text())});
  const shot=async n=>page.screenshot({path:path.join(OUT,n+'.png'),fullPage:true});
  const toast=async()=>page.$eval('#toast',e=>e.hidden?'':e.textContent).catch(()=>'');
  await page.goto('http://localhost:8765/');await sleep(1500);await shot('01-board-empty');
  await page.click('[data-go=newclient]');await sleep(300);
  await page.fill('#c-name','Kuluka Coffee');await page.fill('#c-sector','Specialty coffee');await page.fill('#c-palette','#2B1A12, #F3E6D3, #C8742E, #3E5B3A');await page.fill('#c-tone','Warm, proud of origin');
  await page.click('#client-form button[type=submit]');await sleep(800);
  await page.setInputFiles('input[data-upload=logo]',A('kuluka-logo.png'));await sleep(1500);console.log('after logo:',await toast());
  await shot('02-client');
  await page.click('#nav-new');await sleep(300);
  await page.fill('#j-title','Lançamento Gurué');await page.fill('#j-count','3');await page.fill('#j-end','2026-10-31');
  await page.click('#job-form button[type=submit]');await sleep(800);
  await page.setInputFiles('input[data-upload=briefing]',[A('brief-kuluka.pdf'),A('notas-cliente.docx'),A('campanha.pptx')]);
  for(let i=0;i<60;i++){await sleep(500);const t=await toast();if(/files? added/.test(t)){console.log('brief:',t);break}}
  await page.setInputFiles('input[data-upload=visual]',[A('farm-gurue.jpg'),A('barista-cup.jpg')]);
  for(let i=0;i<30;i++){await sleep(400);const t=await toast();if(/files? added/.test(t)){console.log('visual:',t);break}}
  await page.setInputFiles('input[data-upload=reference]',[A('ref-poster.jpg'),A('ref-arch.png')]);
  for(let i=0;i<30;i++){await sleep(400);const t=await toast();if(/files? added/.test(t)){console.log('refs:',t);break}}
  await sleep(500);await shot('03-job-files');
  const briefLen=await page.$eval('#brief',e=>e.value.length);console.log('brief chars',briefLen);
  await page.click('[data-act=run-all]');
  for(let i=0;i<240;i++){await sleep(500);const live=await page.$eval('#live',e=>e.textContent).catch(()=>'');if(/All agents finished|Stopped|could not|problem/.test(live)){console.log('LIVE:\n'+live);break}}
  await sleep(2500);await shot('04-job-done');
  // full-res renders of each post in both languages
  const renders=await page.evaluate(async()=>{const j=jobById(S.view.id);const out=[];for(const p of S.posts[j.id]){for(const l of ['pt','en']){const r=await renderPost(j,p,l);out.push({n:p.n,l,url:r.canvas.toDataURL('image/png'),warn:r.warn})}}return out});
  for(const r of renders){fs.writeFileSync(path.join(OUT,`post${r.n}-${r.l}.png`),Buffer.from(r.url.split(',')[1],'base64'));if(r.warn.length) console.log('warn',r.n,r.l,r.warn)}
  await page.click('[data-lang=en]');await sleep(1500);await shot('05-job-en');
  // exports
  await page.click('[data-act=export]');for(let i=0;i<40;i++){await sleep(500);if(fs.readdirSync(OUT).some(f=>f.endsWith('.zip'))) break}
  await page.click('.post [data-pact=svg]');await sleep(1500);
  console.log('downloads:',fs.readdirSync(OUT).filter(f=>/\.(zip|svg)$/.test(f)));
  // change request + redesign path, and variant + undo
  await page.click('.post:nth-of-type(2) [data-pact=note]');await sleep(200);
  await page.fill('.post:nth-of-type(2) textarea[id^=note-]','Make the headline shorter');await page.click('.post:nth-of-type(2) [data-pact=note-copy]');
  for(let i=0;i<40;i++){await sleep(300);const live=await page.$eval('#live',e=>e.textContent).catch(()=>'');if(/Done\./.test(live)) break}
  await sleep(800);const h2=await page.evaluate(()=>S.posts[S.view.id][1].en.headline);console.log('revised en headline:',h2);
  await page.click('.post:nth-of-type(1) [data-pact=variant]');for(let i=0;i<40;i++){await sleep(300);const live=await page.$eval('#live',e=>e.textContent).catch(()=>'');if(/Done\./.test(live)) break}
  await sleep(600);console.log('prevDesign present:',await page.evaluate(()=>!!S.posts[S.view.id][0].prevDesign));
  await page.click('.post:nth-of-type(2) [data-pact=apply-fix]').catch(()=>console.log('no apply-fix button'));await sleep(800);
  console.log('after fix pt headline:',await page.evaluate(()=>S.posts[S.view.id][1].pt.headline));
  await page.click('.post:nth-of-type(1) [data-pact=approve]');await sleep(600);
  console.log('summary:',await page.evaluate(()=>JSON.stringify(jobById(S.view.id).summary)));
  console.log('assets:',await page.evaluate(()=>jobById(S.view.id).assets.map(a=>`${a.kind}:${a.name}:${a.w}x${a.h}:${a.meta?.use||''}`).join('\n')));
  await page.click('#home');await sleep(600);await shot('06-board');
  await page.setViewportSize({width:400,height:900});await page.click('.card');await sleep(1500);await shot('07-mobile-job');
  console.log('ERRORS:',errors.length?errors.join('\n'):'none');
  await b.close();
})().catch(e=>{console.error('FAILED',e);process.exit(1)});
