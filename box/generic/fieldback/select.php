<?php

$db = new SQLite3('/etc/iiab/clientinfo.sqlite');
$sql = $_REQUEST['sql'];
//$sql = 'select host_num, hour,sum(connected_time),sum(tx_bytes) from connections group by year,doy,hour'; 
$res = $db->query($sql);

while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
    $jsonArray[] = $row;
}
$response = json_encode($jsonArray);
echo $response;
?>
