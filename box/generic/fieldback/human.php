<?php

$db = new SQLite3('/etc/iiab/clientinfo.sqlite');

$res = $db->query('SELECT * FROM connections');

while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
    echo("{$row['host_id']} {$row['connected_time']} {$row['datetime']} <br>");
}

?>}
