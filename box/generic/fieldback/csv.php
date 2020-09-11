<?php

$db = new SQLite3('/opt/iiab/clientinfo.sqlite');

$res = $db->query('SELECT * FROM connections');

$firstRow = TRUE;
$response = '';
while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
   if ( $firstRow ){
      $fieldNames = array_keys($row);
      foreach($fieldNames as $name) {$response .= $name .  ',';  };
      $response = substr($response,0,-1);
      $response .= '<br>';
      $firstRow = FALSE;
   }
   foreach($fieldNames as $name) {$response .= $row[$name] .  ',';  };
   $response = substr($response,0,-1);
   $response .= '<br>';
  
   
}

echo $response;
?>
