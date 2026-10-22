const { chromium } = require('/Users/acorrales/.npm/_npx/e41f203b7505f1fb/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  for (const [name, w, theme] of [['cult_wide', 1280, 'dark'], ['cult_narrow', 720, 'dark']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 2, colorScheme: theme });
    const p = await ctx.newPage();
    await p.goto('https://www.cult-ui.com/docs/components/texture-card', { waitUntil: 'networkidle', timeout: 60000 });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `ref/${name}.png`, fullPage: true });
    await ctx.close();
  }
  await b.close();
})();
