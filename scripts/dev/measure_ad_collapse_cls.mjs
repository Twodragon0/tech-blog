#!/usr/bin/env node
/**
 * Ad reserve-then-collapse CLS harness.
 *
 * The shift this measures is NOT ad *fill* — it is the opposite. AdSense marks
 * an unfilled unit with data-ad-status="unfilled", the :has() rules in
 * _includes/head.html then delete the .ad-container, and whatever height was
 * reserved vanishes from under the reader.
 *
 * Measuring that against production is useless: fill is stochastic, and a fast
 * scroll reaches the ad region only after the collapse already happened, which
 * is why lab runs kept reporting CLS 0.0000 while a real reader saw 0.20. This
 * harness drives the transition directly on a local build with all third-party
 * requests aborted, so the number is reproducible.
 *
 * Usage:
 *   JEKYLL_ENV=production ./build.sh   (or: bundle exec jekyll build -d _site)
 *   node scripts/dev/measure_ad_collapse_cls.mjs /posts/YYYY/MM/DD/slug/
 *
 * Baseline recorded 2026-08-14 (3 slots, first container centred):
 *   reservation kept   250 -> 0   CLS 0.0575
 *   reservation removed  0 -> 0   CLS 0.0039
 */

import { chromium } from 'playwright';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
import { fileURLToPath } from 'node:url';
const SITE=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..','..','_site');
const server=http.createServer((req,res)=>{const u=decodeURIComponent((req.url||'/').split('?')[0]);
 const cs=u.endsWith('/')?[path.join(SITE,u,'index.html')]:[path.join(SITE,u),path.join(SITE,u,'index.html')];
 for(const c of cs){const r=path.resolve(c); if(!r.startsWith(SITE))continue;
  if(fs.existsSync(r)&&fs.statSync(r).isFile()){const e=path.extname(r);
   res.writeHead(200,{'Content-Type':{'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml'}[e]||'application/octet-stream'});
   return fs.createReadStream(r).pipe(res);}}
 res.writeHead(404).end('nf');});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const base=`http://127.0.0.1:${server.address().port}`;
const b=await chromium.launch();

async function run(label, killReservation) {
  const c=await b.newContext({viewport:{width:1512,height:827}});
  await c.route('**/*', r=> r.request().url().startsWith(base)? r.continue(): r.abort());
  const p=await c.newPage();
  await p.addInitScript(()=>{ window.__m=0; new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput)window.__m+=e.value;}}).observe({type:'layout-shift',buffered:true}); });
  await p.goto(base+process.argv[2],{waitUntil:'load',timeout:60000});
  await p.waitForTimeout(7000);
  if (killReservation) {
    await p.evaluate(()=>{ document.querySelectorAll('.ad-container').forEach(el=>{el.style.minHeight='0px';});
                           document.querySelectorAll('ins.adsbygoogle').forEach(el=>{el.style.minHeight='0px';}); });
    await p.waitForTimeout(900);
  }
  const pre = await p.evaluate(()=>[...document.querySelectorAll('.ad-container')].map(e=>Math.round(e.getBoundingClientRect().height)));
  await p.evaluate(()=>{ const el=document.querySelector('.ad-container'); if(el) el.scrollIntoView({block:'center'}); });
  await p.waitForTimeout(1200);
  const before = await p.evaluate(()=>window.__m);
  // AdSense 가 실제로 하는 일: unfilled 표시 -> head.html:545/552 의 :has() 가 컨테이너를 지움
  await p.evaluate(()=>{ document.querySelectorAll('ins.adsbygoogle').forEach(el=>el.setAttribute('data-ad-status','unfilled')); });
  await p.waitForTimeout(1500);
  const after = await p.evaluate(()=>window.__m);
  const post = await p.evaluate(()=>[...document.querySelectorAll('.ad-container')].map(e=>Math.round(e.getBoundingClientRect().height)));
  await c.close();
  console.log(`${label}: 컨테이너 높이 ${JSON.stringify(pre)} -> ${JSON.stringify(post)}   붕괴 CLS=${(after-before).toFixed(4)}`);
  return after-before;
}
const a = await run('예약 유지(현행)  ', false);
const bb = await run('예약 제거(수정안)', true);
console.log(`\n차이: ${(a-bb).toFixed(4)}  (현행 ${a.toFixed(4)} -> 수정안 ${bb.toFixed(4)})`);
await b.close(); server.close();
