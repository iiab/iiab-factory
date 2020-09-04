var moment = require('moment');
////    Startup Initialization
var label1 = "Time Min";
var label2 = "Bytes MB"
$( '#hour' ).addClass('chosen');
$( '#usage' ).addClass('chosen');


///////////   Button click action routines //////////////
var xAxisUnit = "day";
var pdEnd = document.getElementById('pdEnd');
var pdStart = document.getElementById('pdStart');
var pdYear = moment().format('YYYY');
pdEnd.value = moment().format('YYYY/MM/DD');
pdStart.value = moment().format('YYYY/MM/DD');
var sql = hourly()  + hourly_selector();
var now = moment();
var startDay;


function xAxis(elem){
  var clickedId = elem.id;
  $( ".chooseAxis" ).removeClass('chosen');
  $( '#'+ clickedId ).addClass('chosen');
  xAxisUnit = clickedId;

  switch( clickedId ){
     case "hour":
       xAxisUnit = "hour";
       sql = hourly()  + hourly_selector();
       pdEnd.value = moment().format('YYYY/MM/DD');
       pdStart.value = moment().format('YYYY/MM/DD');
       showGraph();
       break;
     case "day":
       xAxisUnit = "day";
       pdEnd = now.clone();
       startDay = pdEnd.clone();
       startDay.add(-1, "week");
       pdStart.value = startDay.format("YYYY/MM/DD");
       break;
     case "week":
       xAxisUnit = "week";
       pdEnd = now.clone();
       startDay = pdEnd.clone();
       startDay.add(-1, "month");
       pdStart.value = startDay.format("YYYY/MM/DD");
       break;
     case "month":
       xAxisUnit = "month";
       pdEnd = now.clone();
       startDay = pdEnd.clone();
       startDay.add(-1, "year");
       pdStart.value = startDay.format("YYYY/MM/DD");
       break;
     default:
       break;
  }
}
window.xAxis = xAxis;

function hourly_selector(){
   sql = "datestr >= '" + pdStart.value + "' AND datestr <= '" + pdEnd.value + "'";
   return sql;
}

function hourly(){
   sql = 'SELECT connected_time/60 AS value1, tx_bytes/1000000 AS value2,hour as xaxis,hour FROM connections WHERE '
   return sql;
}
function redraw(){
   sql = hourly()  + hourly_selector();
   showGraph();
}
window.redraw = redraw;

function earlier(){
   switch (xAxisUnit){
   case 'hour':
      var startDay = moment(pdStart.value);
      startDay.add(-1, "day");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   case 'day':
      var startDay = moment(pdStart.value);
      startDay.add(-1, "week");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   case 'week':
      var startDay = moment(pdStart.value).add(-1,"month");
      startDay.add(-1, "month");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   case 'month':
      var startDay = moment(pdStart.value).add(-1,"year");
      startDay.add(-1, "year");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   default:
      alert('No match found for xAxisUnits = ' + xAxisUnit);
      break;
   }
}
window.earlier = earlier;
      
function later(){
   switch (xAxisUnit){
   case 'hour':
      var startDay = moment(pdStart.value);
      startDay = startDay.add(1, "day");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   case 'day':
      var startDay = moment(pdStart.value);
      startDay = startDay.add(1, "week");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   case 'week':
      var startDay = moment(pdStart.value).add(-1,"month");
      startDay = startDay.add(1, "month");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   case 'month':
      var startDay = moment(pdStart.value).add(-1,"year");
      startDay = startDay.add(1, "year");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      //showGraph();
      break;
   default:
      alert('No match found for xAxisUnits = ' + xAxisUnit);
      break;
  }
}
window.later = later;

$(document).ready(function () {
   showGraph();
});


//////////////// Graph.js ///////////////////////////
function showGraph(){
    $.post("select.php?sql=" + sql,function (data){
        if (data.length == 0){
           alert("No data returned from sql: " + sql);
        } else {
           dataDict = JSON.parse(data);
           console.log(dataDict);
           var name = [];
           var bar1 = [];
           var bar2 = [];
           var bar2Max = 0;

           for (var i=0;i<dataDict.length;i++) {
               name.push(dataDict[i].xaxis);
               bar1.push(dataDict[i].value1);
               var bar2Val = dataDict[i].value2
               if ( bar2Val < bar2Max) bar2Max = bar2Val;
               bar2.push(bar2Val);
           }
           var chartdata = {
               labels: name,
               datasets: [
                   {
                       label: label1,
                       backgroundColor: 'Blue',
                       yAxisID: 'A',
                       data: bar1
                   },
                   {
                       label: label2,
                       backgroundColor: 'Green',
                       yAxisID: 'B',
                       data: bar2
                   }
               ]
           };

           var graphTarget = $("#graphCanvas");

           var barGraph = new Chart(graphTarget, {
               type: 'bar',
               data: chartdata,
               options: {
                   scales: {
                     yAxes: [{
                       id: 'A',
                       type: 'linear',
                       position: 'left'
                     }, {
                       id: 'B',
                       type: 'linear',
                       position: 'right'
                     }]
                   }
                 }
           });
         }
  });
}
