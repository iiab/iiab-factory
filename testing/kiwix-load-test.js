// setup as non-root
// mkdir iiab-tester
// cd iiab-tester/
// npm init -y
// npm install puppeteer

const puppeteer = require('puppeteer');

//host = 'http://192.168.3.96';
host = 'http://192.168.3.96:3000';

randomUrl = host + '/kiwix/random?content=wikipedia_es_medicine_maxi_2019-11';
testUrls = [
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=mexico+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=futbol+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=amlo+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=gobierno+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=pais+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=nuevo+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=juego+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=oaxaca+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=gastronomia+',
  '/kiwix/search?content=wikipedia_es_all_maxi_2019-09&pattern=pueblo+'


]
process.setMaxListeners(Infinity); // avoid max listeners warning

function main() {
  loadSet();
  loadSet();
  loadSet();
  loadSet();
  loadSet();
  loadSet();
  //loadSet();
  //loadSet();
}

function loadSet() {
  for (var i = 0; i < testUrls.length; i++) {
    console.log(i);
    loadPage(host + testUrls[i]);
    loadPage(randomUrl);
  }
}

async function loadPage(url) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  try {
    await page.goto(url, {waitUntil: 'load', timeout: 0});
    const title = await page.title();
    const html = await page.content();
    const pageBody = await page.evaluate(() => document.body.innerHTML);
    //const h1 = await page.evaluate(() => document.body.h1.innerHTML);

    console.log(title);
    console.log(pageBody);
    //console.log(page.headers.status);
    //console.log(pageBody.substring(1, 300));
    //const elm = await page.$("h1");
    //const text = await page.evaluate(elm => elm.textContent, elm[0]);
    //console.log(text);
    //console.log(h1);
  }
  catch (err) {
    console.log(err);
  }
  finally {
    await browser.close();
  }
}

main();
