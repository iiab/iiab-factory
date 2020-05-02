<?php
   $edit_enable = false;
   $video_base = '/library/www/html/info/videos';
   $video_url = '/info/videos';
   if ( ! isset($_REQUEST['name'])){
      echo('Please enter the video name as a "name=blah" parameter');
      exit(1);
   } else {
      $suffix = '.mp4';
      if ( isset($_REQUEST['edit'])){
         $edit_enable = true;
      }

      //name may include a category in path preceeding video directory specifier
      $video_name = $_REQUEST['name'];
      if (substr($video_name,0,1) == '.') $video_name = substr($video_name,1);
      if (substr($video_name,0,1) == '/') $video_name = substr($video_name,1);
      $video_basename = basename($video_name);

      // look for video extension
      $index = strpos($video_basename,'.');
      if ( $index ) {
         $suffix = substr($video_basename,$index);      
         $video_basename = substr($video_basename,0,$index);
      }

      // look for a category (folder name) preceeding actual filename
      $video_dirname = dirname($video_name);
      if ($video_dirname != '.') $video_dirname = $video_dirname . '/' ;else $video_dirname = "";
      $video_stem = pathinfo($video_name, PATHINFO_FILENAME);
      //$url_full_path = "./$video_dirname$video_stem/$video_basename$suffix";
      $url_full_path = "./$video_dirname$video_basename$suffix";
      $full_path = "$video_base/$video_dirname";
      //print($url_full_path);
      //die("$video_url/$video_dirname$video_stem/"); 
   }
   $cwd = getcwd();
   //chdir("$video_base/$video_dirname$video_basename");
   chdir("$full_path");
   $vtt_files = glob("*.vtt");
   $langs = array();
   foreach ($vtt_files as $f){
      $langs[] = substr($f,-6,2);
   }
   $langs_count = count($langs);
   //die(json_encode($vtt_files));
   
   // find any images to use as poster
   $poster = glob("*.{jpg,jpeg,png}",GLOB_BRACE);
   if ( count($poster) > 0 ) $poster = $poster[0]; else $poster = '';
   //die(print_r($langs));
  $path = $full_path;
  $filename = "$path$video_basename" . $suffix; 
  $title = getOneLine("${path}title");
  if ($title === '') $title = $video_basename . $suffix;
  $oneliner = getOneLine("${path}oneliner");
  $details = getOneLine("${path}details");
  $filesize = filesize($filename);
  $pretty = human_filesize($filesize);
  $video_time = getDuration($filename);
  $modate = date ("F d Y", filemtime($filename));
  $info = getLines("$path/info");
  $info_html = implode('<br>',$info);
  $text_md = implode($info);
  if (! $edit_enable){
      $text_html = shell_exec("pandoc -f markdown $path/info");
  } else $text_html = $info_html;

  $info = "$pretty Duration: $video_time Recorded: $modate";
  chdir($cwd);

//  Start of Functions  #################
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
?>
<script type="text/javascript">
var name="<?=$video_basename?>";
</script>
<!DOCTYPE html>
<html>
  <head>

    <title>Internet in a Box - Videos</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="/common/css/fa.all.min.css"/>
    <link rel="stylesheet" href="/common/css/font-faces.css"/>
    <link rel="stylesheet" href="<?=$video_url?>/viewer.css" type="text/css">
    <link href="<?=$video_url?>/video-js.css" rel="stylesheet">
    <link rel="stylesheet" href="/js-menu/menu-files/css/js-menu-item.css" type="text/css">
    <script src="/common/js/jquery.min.js"></script>
    <script src="<?=$video_url?>/viewer.js" type="text/javascript"></script>
    <script src="<?=$video_url?>/video.js"></script>
  </head>

  <body>
    <div class="wrapper">
      <div id="mainOverlay" class="overlay"></div>
      <div class="flex-col">
      <div class = "h1" id="headerDesktop" style="align: center;">Internet in a Box</div> 
        <div id="content" class="flex-col">
           <div id="video_div">
              <video id="example_video_1" class="video-js" controls preload="none" :
               width="720" height="540" poster='<?php echo("$video_url/$video_dirname$poster");?>' data-setup="{}">
               <source src="<?php echo($url_full_path);?>" type="video/mp4">
               <?php
                  for ( $i=0; $i<$langs_count; $i++){ 
                     $src = "$video_url/$video_dirname$vtt_files[$i]"; 
               ?>
               <track kind="captions" src="<?=$src?>" srclang="en" label="<?=$langs[$i]?>">
               <?php } ?>
               <p class="vjs-no-js">To view this video please enable JavaScript, and consider upgrading to a web browser that <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a></p>
              </video>


            </div> <!-- video-div -->
            <fieldset >
              <legend>Spoken Text</legend>

               <div>
               <span id="buttons">
               <?php
                  for ( $i=0; $i<$langs_count; $i++){ 
                     $lang = $langs[$i];
               ?>
               <button id="lang-<?=$langs[$i]?>" class="lang_select" name="<?=$lang?>"
                  type="button" onclick="display_it(this)"><?=$lang?></button>
            <?php } ?>
               <button id="hide" class="lang_select" name="hide"
                  type="button" onclick="display_it(this)">hide</button>
               </span>
               </div>
               <?php
                  for ( $i=0; $i<$langs_count; $i++){ 
                     $outstr = '';
                     $text = getLines("$path/$vtt_files[$i]"); 
                     foreach($text as $line){
                        if (substr($line,0,6) == "WEBVTT") continue;
                        if (substr($line,0,9) == "Language:") continue;
                        if (substr($line,0,5) == "Kind:") continue;
                        if (rtrim($line) == '') continue;
                        if (substr($line,0,1) == '0') continue;
                        $outstr .= $line;
                     }
               ?>
                  <div id="trans-<?=$langs[$i]?>" class="translated" >
                     <textarea cols="120" rows='15'> <?=$outstr?> </textarea>
                  </div>
               <?php } ?>
                  </fieldset>
            <div class="panel">
            <fieldset>
              <legend>MetaData</legend>
            <table style="text-align: left" ><tr><td>
            Title:</td><td>
            <input id="title" size="40" name="title" type="text" 
               value="<?=$title?>"></td></tr>
            <tr><td>
            One line <br>Description:</td><td>
            <input id="oneliner" name="oneliner" type="text" size="80" 
               value="<?=$oneliner?>"></td></tr>
            <tr><td>
            Details:</td><td>
            <input id="details" name="details" type="text" size="80" 
               value="<?=$details?>"></td></tr>
            <tr><td>More <br>Information:</td><td>
            <?php if (! $edit_enable){ ?>
               <div id="info">
               <?php  echo($text_html); ?>
                </div>
             <?php } else { ?>
               <textarea id="info_textarea" rows="7" cols="80">
                  <?php  echo($text_md); ?>
               </textarea>
            <?php } ?>
              </td></tr>
            </table>
            </fieldset>
            </div>
            <?php 
               if ($edit_enable){
            ?>
            <span>
               <button id="edit" value="edit">Edit</button>
               <button id="preview" value="preview">Preview</button>
               <button id="save" value="save">Save</button>
             </span>
               <?php } ?>
        </div> <!-- End content container -->
      </div> <!-- Flex -->
    </div> <!-- Wrapper -->
  </body>
</html>
