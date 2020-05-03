// viewer.js for videos 

/////////////  GLOBALS /////////////////////////////
//window.$ = window.jQuery = require('jquery');
var videosDir = '/info/videos/';;

/////////////  FUNCTIONS  /////////////////////////////
function display_it(btn){
  // turn off all translations
  $( ".translated" ).each(function (index,data) {
    if (data) data.style.display = "none";
  })
  var trans_id = document.getElementById('trans-' + btn.name);
  trans_id.style.display = "block";
}

function UrlExists(url)
{
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    return http.status!=404;
}

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

var videoDir = getUrlParameter('name');
if ( videoDir == '') {
   alert('Please specify "name=" in URL');
   exit();
}

var html, editor1 = '';
function readText(videoDir, fname){
	//console.log ("in readText");
  var resp = $.ajax({
    type: 'GET',
    url: videosDir + 'readtext.php?name=' + fname
  })
  .done(function( data ) {
  	 html = data;
  })
  .fail(function (){
      console.log('readText failed. URL=' + videosDir + 'readtext.php?name=' + fname);
      html = '';
  })
  return resp;
}

var info_md;
function get_info_md(){
  info_md = $( "#info_textarea" ).html();
  return info_md;
}
$(document).ready(function(){
  $( "#preview" ).click(function(){
  var current = get_info_md();
  console.log(current);
  $.ajax({
    method: "GET",
    url: videosDir + "metadata.php?name=" + name + "&markdown=" + current,
    data: "*italics*",
    success: function(data) {
      console.log(data);
      alert(data);
    }
  })
})

})

function get_translations(video_path,lang=''){
  var resp = $.ajax({
    type: 'GET',
    dataType: 'json',
    url: videosDir + 'readtext.php?name=' + fname + lang
  })
  .done(function( data ) {
  	 html = data;
  })
  .fail(function (){
      console.log('get_translations failed. URL=' + videosDir + 'readtext.php?name=' + fname);
      html = '';
  })
  return resp;
}
//$.when(get_translations(videoDir,meta)).then(function(data,textStatus,jqXHR){
//     createEditor(data);
//});

