// setup as non-root
// mkdir iiab-tester
// cd iiab-tester/
// npm init -y
// npm install puppeteer

// The loop can be broken by typing any key + enter

const readline = require('readline');
const puppeteer = require('puppeteer');
const sleep = (waitTimeInMs) => new Promise(resolve => setTimeout(resolve, waitTimeInMs));

const maxRequests = 100; // maximum number of simultaneous requests
const rndRatio = 2; // how many random requests for each search
var curRequests = 0;
var runFlag = true;

//host = 'http://192.168.3.96';
const host = 'http://192.168.3.96:3000';
const randomUrl = host + '/kiwix/random?content=wikipedia_es_medicine_maxi_2019-11';
searchUrls = [
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

async function main() {
    getInput().then(result => {
        console.log('getInput result:', result)
    }).catch(e => {
        console.log('failed:', e)
    })
    console.log('getInput has been called')

    var searchPtr = 0;
    var rndCnt = rndRatio;

    while (runFlag) {
        //console.log('Run is ' + runFlag);
        if (curRequests < maxRequests) {
            rndCnt -= 1;
            if (rndCnt != 0) {
                loadPage(randomUrl);
            } else {
                rndCnt = rndRatio;                
                loadPage(host + searchUrls[searchPtr]);
                searchPtr += 1;
                if (searchPtr == searchUrls.length)
                    searchPtr = 0;                
            }
            curRequests += 1;
        }
        await sleep(10);
    }
}

function getInput() {
    return new Promise(function (resolve, reject) {
        let rl = readline.createInterface(process.stdin, process.stdout)

        rl.on('line', function (line) {
            runFlag = false;
            rl.close()
            return // bail here, so rl.prompt() isn't called again                       
        }).on('close', function () {
            console.log('bye')
            resolve('end') // this is the final result of the function
        });
    })
}

async function loadPage(url) {
    //console.log('CurRequests is ' + curRequests);
    console.log(curRequests + ' URL: ' + url)
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    try {
        await page.goto(url, { waitUntil: 'load', timeout: 0 });
        const title = await page.title();
        const html = await page.content();
        const pageBody = await page.evaluate(() => document.body.innerHTML);
        //const h1 = await page.evaluate(() => document.body.h1.innerHTML);

        console.log(curRequests + ' ' + title);
        //console.log(pageBody);
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
        curRequests -= 1;
        //console.log('CurRequests is ' + curRequests);

    }
}

function topWrapper() { // because main is async
    main()
        .then(text => {
            console.log(text);
        })
        .catch(err => {
            // Deal with the fact the chain failed
        });
}

topWrapper()
