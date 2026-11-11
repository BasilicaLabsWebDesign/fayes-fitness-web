// Renders tools/social/card.html to the share picture in public/assets/img/.
//   node tools/social/build.cjs
// Needs Playwright's Chromium. Image URLs are cached as immutable, so a changed card gets a
// new file name (bump OUT) and the og:image tags in every page are pointed at it.
const { chromium } = require('playwright');
const path = require('path');
const OUT = path.join(__dirname, '../../public/assets/img/social-card-1200x630.jpg');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'card.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForLoadState('networkidle');
  await p.screenshot({ path: OUT, type: 'jpeg', quality: 86 });
  await b.close();
  console.log('wrote', path.relative(process.cwd(), OUT));
})();
