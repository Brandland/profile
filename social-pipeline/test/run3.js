const {chromium}=require('playwright-core');const fs=require('fs'),path=require('path');const OUT=path.join(__dirname,'out');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});const ctx=await b.newContext({viewport:{width:1360,height:1000}});
  await ctx.route(/jszip/,r=>r.fulfill({path:path.join(__dirname,'node_modules/jszip/dist/jszip.min.js'),contentType:'text/javascript'}));
  await ctx.addInitScript({path:path.join(__dirname,'fake-runtime.js')});
  const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:8765/');await sleep(1200);await page.click('.card:has-text("Teste")');await sleep(1500);
  const before=await page.evaluate(()=>S.posts[S.view.id][0].design.concept.slice(0,50));
  await page.click('.post:nth-of-type(1) [data-pact=note]');await page.fill('.post:nth-of-type(1) textarea[id^=note-]','BROKEN-TEST please');await page.click('.post:nth-of-type(1) [data-pact=note-design]');
  let live='';for(let i=0;i<100;i++){await sleep(300);live=await page.$eval('#live',e=>e.textContent).catch(()=>'');if(/Done\.|could not be rendered|problem/.test(live)) break}
  console.log(live);await sleep(800);
  console.log('before:',before,'\nafter:',await page.evaluate(()=>S.posts[S.view.id][0].design.concept.slice(0,50)),'\nprev kept:',await page.evaluate(()=>!!S.posts[S.view.id][0].prevDesign),'\nstatus:',await page.evaluate(()=>S.posts[S.view.id][0].status));
  const calls=JSON.parse(await (await fetch('http://localhost:8765/_log')).text()).slice(-4);console.log(calls);
  console.log('ERRORS:',errors.join('\n')||'none');await b.close();
})();
