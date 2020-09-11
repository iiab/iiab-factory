<?php

$db = new SQLite3('/opt/iiab/clientinfo.sqlite');

$res = $db->query('SELECT * FROM connections');

while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
    $jsonArray[] = $row;
}
//die($response);
$response = json_encode($jsonArray);
echo $response;
?>
