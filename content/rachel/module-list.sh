#!/bin/bash

html1='<tr><td><a href="/modules/'
html2='/" target="_blank">'
html3='</a>'
td='</td><td>'
end='</td></tr>'
megdiv=1024

echo '<html><head><style>table tr td { border: 1px solid black; padding: 10px;}</style></head>'
echo '<body><table>'

echo '<h1>All Installed Moduless</h1>'
echo '<tr><td>Module</td><td>SIZE (M)</td>></tr>'

for d in $( ls /library/www/html/modules ); do
    #    filename="${f%%.*}"
    mod_size=`du -s /library/www/html/modules/$d  | awk '{print $1}'`
    #echo $d, $mod_size
    mod_size_m=$((mod_size / megdiv))

    echo $html1$d$html2$d$html3$td$mod_size_m$end
done
echo '</table></body></html>'
