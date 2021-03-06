## Video initiative is evolving
* As of May 2020, I have 10 "HowTo Videos" that only occupy 170MB -- only a few were created by me.
* I've only used a Windows laptop and a RPi4 for origination.
* Additional requirements:
    * USB sound dongle
    * WEBCAM -- I used Logitech c525. 
    * Tripod
    * Lots of patience. The linux tools are not as foolproof as those that run on my MacBook.
    
## A Work Flow And Framework for Videos
1. There is an open source javascript viewer from Brighcove that I've incorporated into a page which plays closed captions (I've chosen English, French, and Spanish). But any additional translations rely on Google Translate, and are easy to add if needed.
2. There was a steep learning curve for me, as I tried to learn to edit video. Many open source editors blew up for me on a PRi4, and destroyed a lot of work in process. The more capable editors, might have more programming horsepower to arrive at a stable platform, but they seemed overly complicated.
3. It may have just been my luck. But I had successful output, and a fairly easy time, with OpenShot. It runs adequately on the RPi.

### Start a Video Project July 26,2019
* My first video effort had a nummber of failings:
   1. It was not scripted, was too long, and planned on the fly.
   2. There was no written correlated material.
   3. No plan or strategy existed for making the material available in other languages.
   4. It relied on specialized hardware (my MacBook), which did not permit others who didn't have a MacBook to gain from my experience.
* Are there folks on the XSCE mailing list who might be enticed do research and create "howto videos" for capabilities that we already have in IIAB?
* Could we develop a curated selection of "howto Videos" to facilitate expanded use of current offerings?
#### New Strategy
1. Find a suite of software and hardware which makes video generation as easy on the RPI as it is on the MAC.
2. Create a video showing how to create videos.
3. Develop a system similar to gettext for internationalization of these "Howto Videos".--May,2020 --(use google translated closed captions instead of gettext)
4. Make a list on needed "Howtos".


#### Videos Needed
1. Set up and debug sound on the rpi.
2. A first recording.
2. Video editing suggested standards.
3. Use wordpress as story board, and input to gettext
4. Set up gettext work flow, and document via video.
5. Find video editor which will let native speakers redub videos created in english.
