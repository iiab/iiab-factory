<?php
   $video_base = '/library/www/html/info/videos';
   $video_url = '/info/videos';

function human_filesize($bytes, $decimals = 1) {
    $size = array('B','kB','MB','GB','TB','PB','EB','ZB','YB');
    $factor = floor((strlen($bytes) - 1) / 3);
    return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)) . @$size[$factor];
}

function getDuration($file){
   include_once("/usr/share/php/getid3/getid3.php");
   $getID3 = new getID3;
   $file = $getID3->analyze($file);
   return $file['playtime_string'];
}

function getOneLine($file){
  $lines = @file($file);
  if ($lines !== FALSE) return $lines[0]; else return '';
}
  
function getLines($file){
  $lines = @file($file);
  if ($lines !== FALSE) return $lines; else return [];
}

function menu_item($path){
     global $video_url, $video_base, $nbfiles, $menuhtml, $bytestotal;
     //$menuhtml .= 'Menu Item:' .$path . '<br>';
     $video_basename = basename($path);
     $video_stem = substr($video_basename,0,-4);
     $after_video = substr($path,strlen($video_base));
     $href = $video_url . "/viewer.php?name=" . $after_video;
     $title = getOneLine(dirname($path) ."/title");
     if ($title === '') $title = dirname($path);
     $video_link = "<a href=$href >$title</a>";
     $oneliner = getOneLine(dirname($path) . "/oneliner");
     $details = getOneLine(dirname($path) . "/details");
     $nbfiles++;
     $stat = stat($path);
     $filesize=$stat['size'];
     $bytestotal+=$filesize;
     if ( $details == '') {
        $pretty = human_filesize($filesize);
        $video_time = getDuration($path);
        $modate = date ("F d, Y", $stat['ctime']);
        $details =  "   $pretty, duration: $video_time m:s, $modate";
        $fd = @fopen(dirname($path) . "/details",'w');
        if ($fd){
          fwrite($fd,"$details\n");
          fclose($fd);
        }
     }
     $menuhtml .= "$video_link -- $oneliner<br>&nbsp&nbsp" . trim($details) ."<br>";
}
?>
<!doctype html>
<html>
  <head>

    <title>internet in a box - videos</title>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="/common/css/fa.all.min.css"/>
    <link rel="stylesheet" href="/common/css/font-faces.css"/>
    <link rel="stylesheet" href="./viewer.css" type="text/css">
    <link rel="stylesheet" href="./viewer.css" type="text/css">
  </head>

  <body>
      <div class = "h1" id="headerdesktop" style="align: center;">Internet in a Box -- Howto Videos</div> 
    <!--<div id="content" class="flex-col"> -->
    <!--<div class="content-item"> -->
<?php

$bytestotal=0;
$nbfiles=0;
$menuhtml =  '<div class="content-item" >';
$group_list = array();
$mp4_type = array('mp4','m4v');

$glob_list = glob($video_base . "/group*",GLOB_ONLYDIR);
// First render videos that have been grouped
if ($glob_list){
   $last_heading = $heading = '';
   foreach ($glob_list as $cur){
       //$menuhtml .= $cur . '<br>';
       //print($cur);
       $regex = "@.*group.*-([A-Za-z0-9-_.]+).*@";
       preg_match($regex,$cur,$matches);
       if ($matches) {
           $heading = $matches[1];
       }
       if ($heading != $last_heading){
         $menuhtml .= "<h3>$heading</h3>";
         $last_heading = $heading;
      }
      $iter=new recursivedirectoryiterator($cur);
      $treeIter = new RecursiveIteratorIterator($iter);
      foreach ($treeIter as $filename=>$fname) {
         //$menuhtml .= $fname.'<br>';
         if (in_array(substr($fname,-3), $mp4_type)){
            menu_item($fname); 
         }
      }
  }
}
// Now render Videos that are not in a group
$glob_list = glob($video_base . "/*",GLOB_ONLYDIR);
if ($glob_list){
   $last_heading = $heading = '';
   foreach ($glob_list as $cur){
      //$menuhtml .= $cur . '<br>';
      $after_video = substr($cur,strlen($video_base));
      //$menuhtml .= $after_video . '<br>';
      if (substr($after_video,0,6) == '/group') continue;
      $heading = 'Other Videos';
      if ($heading != $last_heading){
         $menuhtml .= "<h3>$heading</h3>";
         $last_heading = $heading;
      }
      $iter=new recursivedirectoryiterator($cur);
      $treeIter = new RecursiveIteratorIterator($iter);
      foreach ($treeIter as $filename=>$fname) {
         //$menuhtml .= $fname.'<br>';
         if (in_array(substr($fname,-3), $mp4_type)){
            menu_item($fname); 
         }
      }
   }
}
$bytestotal=human_filesize($bytestotal);
$menuhtml .= "<br>Total: $nbfiles files,  $bytestotal . bytes\n";
$menuhtml .= "</div>";
//die($menuhtml);
echo $menuhtml;
?>
<!--   </div>  End content-->
<!--   </div> flex-col -->
</body>
</html>
