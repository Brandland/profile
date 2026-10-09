(() => {
  const store = new Map(); const listeners = new Set();
  const clone = o => JSON.parse(JSON.stringify(o));
  const deepFreeze = o => { if (o && typeof o === 'object' && !Object.isFrozen(o)) { Object.freeze(o); Object.values(o).forEach(deepFreeze); } return o; };
  try { const x = new XMLHttpRequest(); x.open('GET','/_state',false); x.send(); for (const [k,v] of JSON.parse(x.responseText||'[]')) store.set(k,v); } catch(e){}
  const persist = () => fetch('/_state',{method:'POST',body:JSON.stringify([...store.entries()])}).catch(()=>{});
  const snapDoc = path => { const d = store.get(path); return { id: path.split('/').pop(), exists: !!d, data: () => d ? deepFreeze(clone(d)) : undefined, metadata:{fromCache:false,hasPendingWrites:false} }; };
  const colDocs = col => { const depth = col.split('/').length + 1; return [...store.keys()].filter(k => k.startsWith(col + '/') && k.split('/').length === depth).sort().map(snapDoc); };
  const notify = () => { for (const l of [...listeners]) l.fire(); };
  const mkQS = (col, o) => { let docs = colDocs(col); if (o.orderBy) { const [f,dir] = o.orderBy; docs.sort((a,b)=>{const x=a.data()?.[f],y=b.data()?.[f];return (x>y?1:x<y?-1:0)*(dir==='desc'?-1:1)}); } if (o.limit) docs = docs.slice(0,o.limit); return {docs,size:docs.length,empty:!docs.length,docChanges:()=>[],metadata:{fromCache:false,hasPendingWrites:false}}; };
  const query = (col, o={}) => ({ where(){return query(col,o)}, orderBy(f,dir='asc'){return query(col,{...o,orderBy:[f,dir]})}, limit(n){return query(col,{...o,limit:n})}, async get(){return mkQS(col,o)}, onSnapshot(next){const l={fire:()=>setTimeout(()=>next(mkQS(col,o)),0)};listeners.add(l);l.fire();return()=>listeners.delete(l)} });
  const merge = (a,b) => { for (const [k,v] of Object.entries(b)) { if (v && typeof v==='object' && !Array.isArray(v) && a[k] && typeof a[k]==='object' && !Array.isArray(a[k])) merge(a[k],v); else a[k]=clone(v===undefined?null:v); } return a; };
  const docRef = path => { if (path.split('/').length % 2) throw new TypeError('doc path parity ' + path); return { id:path.split('/').pop(), path, async get(){return snapDoc(path)}, async set(d){store.set(path,clone(d));persist();notify()}, async update(d){ if(!store.has(path)) throw {code:'invalid_argument',message:'missing doc'}; store.set(path,merge(clone(store.get(path)),d)); persist(); notify(); }, async delete(){store.delete(path);persist();notify()}, onSnapshot(next){const l={fire:()=>setTimeout(()=>next(snapDoc(path)),0)};listeners.add(l);l.fire();return()=>listeners.delete(l)}, collection(s){return colRef(path+'/'+s)} }; };
  const colRef = path => { if (!(path.split('/').length % 2)) throw new TypeError('collection path parity ' + path); return Object.assign(query(path), { path, doc(id){return docRef(path+'/'+(id||Math.random().toString(36).slice(2,12)))}, async add(d){const r=this.doc();await r.set(d);return r} }); };
  const db = { doc: docRef, collection: colRef };
  const assets = { async upload(blob,opts={}){ const type=opts.type||blob.type; if(!type||/;/.test(type)) throw {code:'invalid_request',message:'type'}; const r=await fetch('/_upload?type='+encodeURIComponent(type),{method:'POST',body:blob}); const {id}=await r.json(); return {id,url:'/_blob/'+id,sizeBytes:blob.size,contentType:type}; }, async delete(){return {deleted:true}}, async list(){return {assets:[],usage:{}}} };
  const downloads = { async save({filename,data}){ const b = data instanceof Blob ? data : new Blob([data]); await fetch('/_download?name='+encodeURIComponent(filename),{method:'POST',body:b}); return {status:'saved'}; } };
  let sampleCalls = 0;
  async function sample(input, opts={}){
    if (opts.images) { const arr = Array.isArray(opts.images) ? opts.images : [opts.images]; let k=0; for (const b of arr) { if (!(b instanceof Blob)) throw {code:'invalid_request',message:'images must be blobs'}; await fetch('/_sampleimg?call='+sampleCalls+'&k='+(k++),{method:'POST',body:b}); } if (arr.length > 5) throw {code:'image_rejected',message:'too many'}; }
    if (opts.signal?.aborted) throw {code:'cancelled'};
    const r = await fetch('/_sample?call='+(sampleCalls++),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({input,nImages:opts.images?(opts.images.length||1):0,tier:opts.modelTier})});
    const t = await r.text(); await new Promise(r=>setTimeout(r,60)); opts.onText && opts.onText({text:t,delta:t}); return {text:t,truncated:false,modelTierApplied:opts.modelTier||'default'};
  }
  sample.json = async (input, opts) => { const {text} = await sample(input, opts); const s = text.trim(); try { return JSON.parse(s.slice(s.search(/[\[{]/))); } catch(e) { throw {code:'invalid_json',message:'bad json',text}; } };
  sample.limits = async () => window.__NOIMG ? {maxPromptBytes:262144} : ({maxPromptBytes:262144,images:{maxCount:5,maxInputBytes:2e7,mediaTypes:['image/png','image/jpeg','image/webp','image/gif']}});
  const mcp = { async listTools(){ return {servers:[{server:'Canva',authStatus:'connected',tools:[]}]}; }, async callTool(server,tool,input){ const r=await fetch('/_mcp',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({tool,input})}); const j=await r.json(); if(j.__error) throw j.__error; return j; } };
  const caps = { db, assets, sample, downloads, mcp };
  window.claude = { use: async n => { await new Promise(r=>setTimeout(r,30)); return caps[n] ?? null; } };
})();
