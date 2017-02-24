#!/bin/bash

html1='<tr><td><a href="http://schoolserver.xsce.org:3000/'
html2='/" target="_blank">'
html3='</a>'
td='</td><td>'
end='</td></tr>'
megdiv=1024

echo '<html><head><style>table tr td { border: 1px solid black; padding: 10px;}</style></head>'
echo '<body><table>'

echo '<h1>All Installed Zim Files</h1>'
echo '<tr><td>ZIM</td><td>ZIM_SIZE</td><td>IDX_SIZE</td><td>TOTAL_SIZE</td></tr>'

for f in $( ls /library/zims/index ); do
    filename="${f%%.*}"
    zim_size=`du -c /library/zims/content/$filename* | grep total | awk '{print $1}'`
    idx_size=`du -s /library/zims/index/$f  | awk '{print $1}'`
    tot_size=$((zim_size + idx_size))
    echo $filename, $zim_size, $idx_size
    zim_size=$((zim_size / megdiv))
    idx_size=$((idx_size / megdiv))
    tot_size=$((tot_size / megdiv))
    echo $html1$filename$html2$filename$html3$td$zim_size$td$idx_size$td$tot_size$end
done
echo '</table></body></html>'