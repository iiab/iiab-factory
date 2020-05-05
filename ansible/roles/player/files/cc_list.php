<?php
   $video_base = '/library/www/html/info/videos';
   if ( ! isset($_REQUEST['name'])){
      echo('Please enter the video name as a "name=blah" parameter');
      exit(1);
   } else {
      if ( isset($_REQUEST['suffix']))
         $suffix = $_REQUEST['suffix'];else $suffix = 'mp4';
      if (substr($suffix,0,1) == '.') $suffix = substr($suffix,1);
      //name may include a category in path preceeding video directory specifier
      $video_name = $_REQUEST['name'];
      $video_basename = basename($video_name);
      $video_dirname = dirname($video_name);
      if ($video_dirname != '.') $video_dirname = $video_dirname . '/';else $video_dirname = "";
      $video_stem = pathinfo($video_name, PATHINFO_FILENAME);
   }
   $two_ch_lang = 0;
   if ( isset($_REQUEST['lang'])) $two_ch_lang = 1;
   chdir("$video_base/$video_dirname$video_basename");
   $vtt_files = glob("*.vtt");
   $outstr = '[';
   if ($two_ch_lang != 0){
      foreach ($vtt_files as $f) {
         $outstr .= substr($f,-6,2) . ',';
      }
   } else {
      foreach ($vtt_files as $f){
         $outstr .= $f . ',';
      }
   }
   $outstr = rtrim($outstr,',') . ']';
   echo($outstr);
?>
