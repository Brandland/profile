const {chromium}=require('playwright-core');const fs=require('fs'),path=require('path');
const A=p=>path.join(__dirname,'assets',p);const OUT=path.join(__dirname,'out');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function mode(m){await fetch('http://localhost:8765/_mode',{method:'POST',body:JSON.stringify(m)})}
async function setup(ctx,noimg){
  await ctx.route(/pdf\.min\.js/,r=>r.fulfill({path:path.join(__dirname,'node_modules/pdfjs-dist/build/pdf.min.js'),contentType:'text/javascript'}));
  await ctx.route(/pdf\.worker\.min\.js/,r=>r.fulfill({path:path.join(__dirname,'node_modules/pdfjs-dist/build/pdf.worker.min.js'),contentType:'text/javascript'}));
  await ctx.route(/jszip/,r=>r.fulfill({path:path.join(__dirname,'node_modules/jszip/dist/jszip.min.js'),contentType:'text/javascript'}));
  if(noimg) await ctx.addInitScript('window.__NOIMG=true');
  await ctx.addInitScript({path:path.join(__dirname,'fake-runtime.js')});
}
const waitLive=async(page,re,n=200)=>{for(let i=0;i<n;i++){await sleep(300);const live=await page.$eval('#live',e=>e.textContent).catch(()=>'');if(re.test(live)) return live}return 'TIMEOUT'};
const toastWait=async(page,re)=>{for(let i=0;i<80;i++){await sleep(300);const t=await page.$eval('#toast',e=>e.hidden?'':e.textContent).catch(()=>'');if(re.test(t)) return t}return 'TIMEOUT'};
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const ctx=await b.newContext({viewport:{width:1360,height:1000}});await setup(ctx,false);
  const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error') errors.push(m.text())});
  await page.goto('http://localhost:8765/');await sleep(1200);
  await page.click('[data-go=newclient]');await page.fill('#c-name','Kuluka Coffee');await page.fill('#c-palette','#2B1A12, #F3E6D3, #C8742E');await page.click('#client-form button[type=submit]');await sleep(700);
  await page.setInputFiles('input[data-upload=logo]',A('kuluka-logo.png'));console.log('logo',await toastWait(page,/added/));
  await page.setInputFiles('input[data-upload=font]',A('Lobster-Regular.ttf'));console.log('font',await toastWait(page,/added/));await sleep(500);
  console.log('font rec:',await page.evaluate(()=>JSON.stringify(S.clients[0].fonts)));
  await page.screenshot({path:path.join(OUT,'10-client-fonts.png'),fullPage:true});
  await page.click('#nav-new');await page.fill('#j-title','Teste');await page.fill('#j-count','3');await page.fill('#j-brief','Brief de teste. Prova sábado 10h00.');await page.click('#job-form button[type=submit]');await sleep(700);
  await page.setInputFiles('input[data-upload=visual]',[A('farm-gurue.jpg'),A('barista-cup.jpg')]);console.log('vis',await toastWait(page,/added/));
  await page.setInputFiles('input[data-upload=reference]',[A('ref-poster.jpg'),A('ref-arch.png')]);console.log('ref',await toastWait(page,/added/));
  // role toggle on first reference: style -> none
  await page.click('.drop[data-drop=reference] .role');await sleep(500);console.log('role after click:',await page.evaluate(()=>jobById(S.view.id).assets.filter(a=>a.kind==='reference').map(a=>a.meta?.use).join(',')));
  await page.click('.drop[data-drop=reference] .role');await sleep(500);await page.click('.drop[data-drop=reference] .role');await sleep(500);
  console.log('role cycled back:',await page.evaluate(()=>jobById(S.view.id).assets.filter(a=>a.kind==='reference').map(a=>a.meta?.use).join(',')));
  await mode({canva:'links'});
  await page.click('[data-act=run-all]');console.log('pipeline:',(await waitLive(page,/All agents finished|could not|problem|Stopped/)).split('\n').slice(-3).join(' | '));
  await sleep(1500);
  console.log('post3 gen:',await page.evaluate(()=>JSON.stringify(S.posts[S.view.id][2].gen)));
  await page.screenshot({path:path.join(OUT,'11-links.png'),fullPage:true});
  // canva failure path via button
  await mode({canva:'fail'});
  await page.click('.post:nth-of-type(3) summary:has-text("Art direction")');await sleep(200);
  const btn=await page.$('.post:nth-of-type(3) [data-pact=canva]');console.log('canva button present:',!!btn);
  if(btn){await btn.click();console.log('canva fail run:',(await waitLive(page,/Done\.|problem|Canva/)).split('\n').slice(-2).join(' | '));await sleep(800);console.log('post3 gen after fail:',await page.evaluate(()=>JSON.stringify(S.posts[S.view.id][2].gen)))}
  // broken design -> fix path
  await page.click('.post:nth-of-type(1) [data-pact=note]');await page.fill('.post:nth-of-type(1) textarea[id^=note-]','BROKEN-TEST please');await page.click('.post:nth-of-type(1) [data-pact=note-design]');
  console.log('broken run:',(await waitLive(page,/Done\.|could not be rendered|problem/)).split('\n').join(' | '));
  // brand font: switch post 1 headline font to Lobster and render
  await page.evaluate(async()=>{const id=S.view.id;await savePost(id,'p01',cur=>{cur.design.texts.find(t=>t.slot==='headline').font='Lobster';cur.design.texts.find(t=>t.slot==='headline').case='none';return cur})});await sleep(1500);
  const r=await page.evaluate(async()=>{const j=jobById(S.view.id);const p=S.posts[j.id][0];const x=await renderPost(j,p,'pt');return x.canvas.toDataURL('image/png')});fs.writeFileSync(path.join(OUT,'12-brandfont.png'),Buffer.from(r.split(',')[1],'base64'));
  console.log('fonts loaded check:',await page.evaluate(()=>document.fonts.check('400 40px "Lobster"')));
  // legacy v1 job injected into state
  await page.evaluate(async()=>{await S.db.doc('jobs/legacy1').set({clientId:S.clients[0].id,title:'Old v1 job',postCount:2,format:'portrait',language:'pt',platforms:['Instagram'],briefText:'old',assets:[{id:null,name:'x.txt',kind:'other',type:'text/plain'}],posts:[{n:1,headline:'Old',caption:'Old caption',status:'draft'}],agents:{copy:{status:'done',at:1}},createdAt:1,updatedAt:Date.now()})});
  await sleep(500);await page.click('#home');await sleep(500);await page.click('.card:has-text("Old v1 job")');await sleep(1200);
  console.log('legacy banner:',await page.$eval('.banner',e=>e.textContent.slice(0,80)).catch(()=>'none'));
  await page.screenshot({path:path.join(OUT,'13-legacy.png'),fullPage:true});
  // no-image view
  const ctx2=await b.newContext({viewport:{width:1200,height:900}});await setup(ctx2,true);const p2=await ctx2.newPage();p2.on('pageerror',e=>errors.push('p2 '+e.message));
  await p2.goto('http://localhost:8765/');await sleep(1200);await p2.click('.card:has-text("Teste")');await sleep(1500);
  console.log('noimg note:',await p2.$eval('.note',e=>e.textContent.slice(0,60)).catch(()=>'none'));
  console.log('ERRORS:',errors.length?errors.join('\n'):'none');
  await b.close();
})().catch(e=>{console.error('FAILED',e);process.exit(1)});
