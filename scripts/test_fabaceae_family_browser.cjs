"use strict";
const assert=require("node:assert/strict");
const {chromium}=require("playwright");
async function test(){
  const browser=await chromium.launch();
  try{
    for(const width of [390,1280]){
      const page=await browser.newPage({viewport:{width,height:844}});
      await page.goto("http://127.0.0.1:8765/",{waitUntil:"domcontentloaded"});
      await page.locator("#family-lesson-steps .family-step").first().waitFor({timeout:25000});
      assert.equal(await page.locator("#family-lesson-steps .family-step").count(),9);
      assert(await page.locator("#family-diagnostics .family-diagnostic").count()>=4);
      const images=page.locator("#family-lesson-steps .family-step img");
      assert(await images.count()>=7);
      assert(await images.first().evaluate(x=>x.complete&&x.naturalWidth>0));
      assert(await page.locator("#species-count").textContent()==="91");
      const sw=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,viewport:document.documentElement.clientWidth}));
      assert(sw.scroll<=sw.viewport+2,JSON.stringify(sw));
      await page.locator("#family-lesson-toggle").click();
      assert.equal(await page.locator("#family-lesson-content").isVisible(),false);
      await page.locator("#family-lesson-toggle").click();
      assert.equal(await page.locator("#family-lesson-content").isVisible(),true);
      await page.locator("#family-lesson-steps .family-species-link").first().click();
      await page.waitForURL(/species=desmanthus-illinoensis/);
      assert.match(await page.locator("#detail").textContent(),/Illinois bundleflower/i);
      console.log("PASS Fabaceae family lesson, credited images, responsive layout, toggle and species navigation width",width);
      await page.close();
    }
  }finally{await browser.close()}
}
test().catch(e=>{console.error(e);process.exitCode=1});
