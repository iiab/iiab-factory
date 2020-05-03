<?php
   $video_base = '/library/www/html/info/videos';
   $video_url = '/info/videos';
   // Boilerplate from viewer.php
   if ( ! isset($_REQUEST['name'])){
      echo('Please enter the video name as a "name=blah" parameter');
      exit(1);
   } else {
      $suffix = '.mp4';
      if ( isset($_REQUEST['edit'])){
         $edit_enable = true;
      } else $edit_enable = false;
      if ( isset($_REQUEST['markdown'])){
         $markdown = $_REQUEST['markdown'];
      } else $markdown= '';
      if ( isset($_REQUEST['save'])){
         $save = $_REQUEST['save'];
      } else $save = '';

      //name may include a category in path preceeding video directory specifier
      $video_name = $_REQUEST['name'];
      $video_basename = basename($video_name);

      // look for video extension
      $index = strpos($video_basename,'.');
      if ( $index ) {
         $suffix = substr($video_basename,$index);      
         $video_basename = substr($video_basename,0,$index);
      }

      // look for a category (folder name) preceeding actual filename
      $video_dirname = dirname($video_basename);
      if ($video_dirname != '.') $video_dirname = $video_dirname . '/';else $video_dirname = "";
      $video_stem = pathinfo($video_name, PATHINFO_FILENAME);
      $url_full_path = "./$video_dirname$video_stem/$video_basename$suffix";
      $full_path = "$video_base/$video_dirname$video_stem";

   }
   chdir("$video_base/$video_dirname$video_basename");
   //  End of boilerplate /////////////
   $file_path = "./info";
   if ($markdown !== ''){
      if ($save !== ''){
         //$fp = open($file_path,'w');
         //$fp.write($markdown);
         //$fp.close();
         echo "Data to save: $markdown";
      } else {
         $text_html = shell_exec("echo $markdown |pandoc -f markdown");
         echo $text_html;
      }
   } else echo 'markdown not true';
?>
