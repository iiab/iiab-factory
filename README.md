<!-- For http://d.iiab.io/README.html -- usable in version subdirectories too -->
<!-- Copied from https://github.com/iiab/iiab-factory/blob/master/README.html -->

<a href=https://internet-in-a-box.org>Internet-in-a-Box (IIAB)</a> 8.2 pre-releases are thoroughly tested, and can be installed from this page!  Please read our DRAFT <a href="https://github.com/iiab/iiab/wiki/IIAB-8.2-Release-Notes">IIAB 8.2 Release Notes</a>.
<p>
  <i>To install IIAB 8.2 onto <a href="https://www.raspberrypi.com/software/">Raspberry Pi OS</a>, <a href="https://github.com/iiab/iiab/wiki/IIAB-Platforms#ubuntu-2404">Ubuntu 24.04+</a>, <a href="https://linuxmint.com/">Linux Mint 22+</a> or <a href="https://www.debian.org/download">Debian 12+</a>, simply run this 1-line installer:</i>
<p>
  <center><big><b><mark>curl iiab.io/install.txt | bash</mark></b></big></center>
<p>
  <!--OS TIPS & TRICKS: click the above link (that ends in .txt) for important recommendations on how to PREPARE & SECURE YOUR OS. <p>-->
  On a Raspberry Pi, <a href="https://www.raspberrypi.com/software/">WE RECOMMEND YOU INSTALL THE LATEST RASPBERRY PI OS</a> <a href="https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-64-bit">(64-bit is recommended)</a>, using their <a href="https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system">detailed instructions</a> if necessary.  WARNING: THE NOOBS OS IS *NOT* SUPPORTED, as its partitioning is very different.  To attempt an IIAB install onto a <a href=https://github.com/iiab/iiab/wiki/IIAB-Platforms#operating-systems>non-supported Linux distribution</a> (AT YOUR OWN RISK) see also the <a href="https://github.com/iiab/iiab/wiki/IIAB-Installation#do-everything-from-scratch">manual/legacy instructions</a>.
<p>
  <i>An Ethernet cable is highly recommended during installation.  This is more reliable AND allows an internal IIAB hotspot to be set up without confusion.</i>  WARNING: IF YOU CONNECT YOUR IIAB'S INTERNAL WI-FI TO THE INTERNET OVER 5 GHz, YOU'LL PREVENT OLDER LAPTOPS/PHONES/TABLETS (WHICH REQUIRE 2.4 GHz) FROM CONNECTING TO YOUR IIAB'S INTERNAL HOTSPOT.  For AP+STA mode, set "wifi_up_down: True" in <a href="https://wiki.iiab.io/go/FAQ#What_is_local_vars.yml_and_how_do_I_customize_it%3F">/etc/iiab/local_vars.yml</a> (<a href="https://github.com/iiab/iiab/blob/cbae5b71eac0a9d6894f4c741e94b033a2bb6a81/vars/local_vars_medium.yml#L94-L95">example</a>).<!--  If however you must install over Wi-Fi, remember to run "iiab-hotspot-on" after IIAB installation, TO ACTIVATE YOUR RASPBERRY PI's INTERNAL WIFI HOTSPOT (thereby killing Internet connectivity!)-->
<p>
  <center><b>Thanks For Building Your Own Library To Serve One & All</b></center>
<p>
  Please <a href=https://internet-in-a-box.org/contributing.html>contact us</a> if you find issues, Thank You!  Special Thanks to the countries + communities + volunteers working non-stop to bring about <a href="https://github.com/iiab/iiab/wiki/IIAB-8.2-Release-Notes">IIAB 8.2</a> !
<p>
  IIAB Dev Team
  <br>
  <a href="https://wiki.iiab.io/go/FAQ">http://FAQ.IIAB.IO</a>
