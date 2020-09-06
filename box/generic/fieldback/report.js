var moment = require('moment');
////    Startup Initialization
var label1 = "Time Min";
var label2 = "Bytes MB"
$( '#hour' ).addClass('chosen');
$( '#usage' ).addClass('chosen');


var xAxisUnit = "hour";
var pdEnd = document.getElementById('pdEnd');
var pdStart = document.getElementById('pdStart');
var pdYear = moment().format('YYYY');
pdEnd.value = moment().format('YYYY/MM/DD');
pdStart.value = moment().format('YYYY/MM/DD');
var sql = hourly()  + daily_where();
var now = moment();
var startDay;
var displaying;
var barGraph = null;

///////////   Button click action routines //////////////
function xAxis(elem){
  var clickedId = elem.id;
  $( ".chooseAxis" ).removeClass('chosen');
  $( '#'+ clickedId ).addClass('chosen');
  xAxisUnit = clickedId;

  switch( clickedId ){
     case "hour":
       xAxisUnit = "hour";
       pdEnd.value = moment().format('YYYY/MM/DD');
       pdStart.value = moment().format('YYYY/MM/DD');
       sql = hourly()  + daily_where();
       showGraph();
       break;
     case "day":
       xAxisUnit = "day";
       startDay = moment(pdEnd.value);
       startDay.add(-1, "week");
       pdStart.value = startDay.format("YYYY/MM/DD");
       sql = daily()  + daily_where() + daily_groupby();
       showGraph();
       break;
     case "week":
       xAxisUnit = "week";
       startDay = moment(pdEnd.value);
       startDay.add(-1, "month");
       pdStart.value = startDay.format("YYYY/MM/DD");
       sql = daily()  + daily_where() + daily_groupby();
       alert(sql);
       showGraph();
       break;
     case "month":
       xAxisUnit = "month";
       startDay = moment(pdEnd.value);
       startDay.add(-1, "year");
       pdStart.value = startDay.format("YYYY/MM/DD");
       alert(sql);
       showGraph();
       break;
     default:
       break;
  }
}
window.xAxis = xAxis;

function chooseDisplaying(elem){
  var clickedId = elem.id;
  $( ".displayThis" ).removeClass('chosen');
  $( '#'+ clickedId ).addClass('chosen');
  displaying = clickedId;
  switch (displaying){
      case "device":
         sql = site()  + daily_where() + device_groupby();
         break;
      case "usage":
         sql = daily()  + daily_where() + daily_groupby();
         break;
  }
    alert(sql);
    showGraph();
}
window.chooseDisplaying = chooseDisplaying;

function validate_inputs(){
   if ( moment( pdStart.value ).isValid() && 
        moment( pdEnd.value ).isValid() ){
      return true;
   } else return false;
}

function hourly(){
   sql = 'SELECT connected_time/60 AS value1, tx_bytes/1000000 AS value2,hour as xaxis, hour FROM connections WHERE '
   return sql;
}

function daily(){
   sql = 'SELECT sum(connected_time)/60 AS value1, sum(tx_bytes)/1000000 AS value2,datestr as xaxis, hour FROM connections WHERE '
   return sql;
}

function site(){
   sql = 'SELECT sum(connected_time)/60 AS value1, sum(tx_bytes)/1000000 AS value2,datestr, hour, l.host_num as xaxis FROM connections c,lookup l WHERE c.client_id = l.client_id AND '
   return sql;
}

function daily_where(){
   if ( ! validate_inputs ){
      alert('Bad Date value');
      return;
   }
   sql = "datestr >= '" + pdStart.value + "' AND datestr <= '" + pdEnd.value + "'";
   return sql;
}

function daily_groupby(){
   switch ( xAxisUnit ){
      case "week":
         sql = " GROUP BY year,week";
         break;
      case "month":
         sql = " GROUP BY year,month";
         break;
      default:
         // hour, and day
         sql = " GROUP BY datestr";
         break;
   }
   return sql;
}

function device_groupby(){
   if ( displaying == "device" ) return ' GROUP By site';
   return daily_groupby();
}

function redraw(){
   switch ( xAxisUnit ){
      case "hour":
         sql = hourly()  + daily_where();
         break;
      default:
         sql = daily()  + daily_where();
         break;
   }
   showGraph();
}         


window.redraw = redraw;

function earlier(){
   switch (xAxisUnit){
   case 'hour':
      var startDay = moment(pdStart.value);
      startDay.add(-1, "day");
      pdStart.value = startDay.format('YYYY/MM/DD'); 
      sql = hourly()  + daily_where();
      showGraph();
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
      sql = hourly()  + daily_where();
      showGraph();
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


//////////////// Chart.js ///////////////////////////
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
           if ( barGraph != null ){
                barGraph.clear();
                barGraph.destroy();
           }
           var graphTarget = $("#graphCanvas");

           barGraph = new Chart(graphTarget, {
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
