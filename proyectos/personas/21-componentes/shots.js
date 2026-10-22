const { chromium } = require('/Users/acorrales/.npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const OUT = process.argv[2];
const SITES = [
  ['01_uiarc', 'https://uiarc.dev/'], ['02_buildertools', 'https://www.buildertools.sh/'], ['03_uimaxx', 'https://uimaxx.ing/#library'],
  ['04_libraries', 'https://libraries.dev/'], ['05_sounds', 'https://procedural-sounds.vercel.app/'], ['06_beui', 'https://beui.dev/'],
  ['07_cult', 'https://www.cult-ui.com/docs/components/texture-button'], ['08_aceternity', 'https://ui.aceternity.com/'],
  ['09_beautiful', 'https://www.beautifului.dev/'], ['10_canvasui', 'https://canvasui.dev/docs/components/dithered-object'],
  ['11_reactbits', 'https://reactbits.dev/tools'], ['12_kobra', 'https://kobra.systems/components/form'],
  ['13_mobbin', 'https://mobbin.com/discover/sites/latest?redirect_to=/discover/apps/web/top'], ['14_21st', 'https://21st.dev/community/components'],
];
(async () => {
  const browser = await chromium.launch();
  for (const [name, url] of SITES) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, colorScheme: 'dark' });
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(4500);
      await page.screenshot({ path: `${OUT}/${name}.png` });
      console.log('ok', name, (await page.title()).slice(0, 80));
    } catch (e) { console.log('fail', name, String(e).slice(0, 120)); }
    await ctx.close();
  }
  await browser.close();
})();
