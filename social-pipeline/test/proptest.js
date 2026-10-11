const {chromium}=require('playwright-core');const fs=require('fs'),path=require('path');const OUT=path.join(__dirname,'out');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const b64=f=>fs.readFileSync(path.join(__dirname,'assets',f)).toString('base64');
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});const ctx=await b.newContext({viewport:{width:1360,height:1000}});
  await ctx.route(/jspdf/,r=>r.fulfill({path:path.join(__dirname,'node_modules/jspdf/dist/jspdf.umd.min.js'),contentType:'text/javascript'}));
  await ctx.addInitScript({path:path.join(__dirname,'fake-runtime.js')});const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await fetch('http://localhost:8765/_state',{method:'POST',body:'[]'});
  await page.goto('http://localhost:8765/');await sleep(1200);
  const posts=JSON.parse(fs.readFileSync(path.join(OUT,'sample-posts.json')));
  await page.evaluate(async({posts,logo,pl,pi})=>{
    const up=async(b,t)=>{const bin=atob(b);const u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);return (await S.assets.upload(new Blob([u],{type:t}),{type:t})).id};
    const lid=await up(logo,'image/png');
    await S.db.doc('settings/agency').set({name:'Playground',logoId:await up(pl,'image/png'),iconId:await up(pi,'image/png'),contact:'Maputo · Moçambique'});
    await S.db.doc('clients/c1').set({name:'Kuluka Coffee',palette:['#2B1A12','#F3E6D3','#C8742E'],logos:[{id:lid,name:'l.png',kind:'logo',type:'image/png',alpha:true}],fonts:[]});
    await S.db.doc('jobs/j1').set({v:2,clientId:'c1',title:'Lançamento Gurué',languages:'both',format:'portrait',postCount:3,startDate:'2026-10-12',endDate:'2026-10-25',assets:[],agents:{},summary:{total:3,approved:3},analysis:{objective:'Notoriedade da origem Gurué e visitas ao café em Outubro.',audiences:[{name:'Jovens profissionais em Maputo',insight:'Pagam por bom café mas assumem que o melhor é importado.'}],keyMessages:['Cultivado em Gurué','Torrado em Maputo às terças'],pillars:[{name:'Origem',purpose:'Orgulho'},{name:'Torra',purpose:'Frescura'}]},updatedAt:Date.now(),platforms:['Instagram','Facebook']});
    for(const p of posts) await S.db.doc('jobs/j1/posts/p0'+p.n).set({...p,status:'approved'});
  },{posts,logo:b64('kuluka-logo-v2.png'),pl:b64('playground-logo.png'),pi:b64('playground-icon.png')});
  await sleep(500);await page.click('.card');await sleep(1500);
  await page.click('[data-act=proposal-open]');await sleep(600);
  await page.click('#pr-strategy');
  await page.screenshot({path:path.join(OUT,'p-panel.png')});
  await page.click('[data-act=proposal-pdf]');
  for(let i=0;i<120;i++){await sleep(500);if(fs.readdirSync(OUT).some(f=>f.endsWith('.pdf'))) break}
  console.log(fs.readdirSync(OUT).filter(f=>f.endsWith('.pdf')));
  await sleep(800);await page.click('#nav-archive');await sleep(800);
  console.log('rows',await page.$$eval('table.arch tbody tr',r=>r.length));
  await page.screenshot({path:path.join(OUT,'p-archive.png')});
  await page.fill('#arch-q','zzz');await sleep(600);console.log('filtered rows',await page.$$eval('table.arch tbody tr',r=>r.length));
  await page.fill('#arch-q','');await sleep(600);
  await page.click('[data-arch=dl]');await sleep(800);
  await page.click('[data-arch=job]');await sleep(800);console.log('view',await page.evaluate(()=>S.view.name));
  await page.click('#nav-archive');await sleep(1000);
  // an orphan file
  await page.evaluate(async()=>{await S.assets.upload(new Blob(['x'.repeat(5000)],{type:'text/plain'}),{type:'text/plain'})});
  await page.click('[data-clean=refresh]');await sleep(800);
  await page.screenshot({path:path.join(OUT,'p-storage.png'),fullPage:true});
  await page.click('[data-clean=orphans]');await sleep(200);await page.click('[data-clean=orphans]');await sleep(1500);
  console.log('after orphans', await page.$eval('.meter + span',e=>e.textContent));
  await page.check('[data-asel]');await sleep(300);await page.click('[data-clean=selected]');await sleep(200);await page.click('[data-clean=selected]');await sleep(1500);
  console.log('archive cell',await page.$eval('table.arch tbody tr',e=>e.textContent.includes('PDF removed')));
  await page.click('#nav-help');await sleep(800);await page.screenshot({path:path.join(OUT,'p-help.png')});
  await page.click('[data-help=off]');await sleep(300);console.log('help hidden',!(await page.$('.help')));
  await page.click('#nav-clients');await sleep(800);await page.screenshot({path:path.join(OUT,'p-clients.png'),fullPage:true});
  console.log('ERRORS',errors.join('\n')||'none');await b.close();
})();
