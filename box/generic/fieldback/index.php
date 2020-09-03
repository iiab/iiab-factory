<!DOCTYPE html>
<html>
<head>
<title>Creating Dynamic Data Graph using PHP and Chart.js</title>
<style type="text/css">
BODY {
    width: 1200PX;
}

#chart-container {
    width: 100%;
    height: auto;
}
</style>
<link rel="stylesheet" href="report.css" /> 
<link rel="stylesheet" href="assets/Chart.css" /> 
<script type="text/javascript" src="/common/js/jquery.min.js"></script>
<script type="text/javascript" src="assets/Chart.bundle.js"></script>
<link href="/common/css/bootstrap.min.css" rel="stylesheet">


</head>
<body>
    
    <div id="chart-container">
        <canvas id="graphCanvas"></canvas>
    </div>

    <div id="buttonBox">
       <div id="x-axis">
            <label class="bttn">  Displaying:</label>
            <button -id="devices">Devices</button>
            <button -id="usage">Usage</button>
            <div>
            <label class="bttn">Time Frame:</label>
            <button id="month" class="chooseAxis" type="radio" name="xAxis" onclick="xAxis(this.id)">Months</button>
            </div>
            <div>
            <button id="week" class="chooseAxis" type="radio" name="xAxis" onclick="xAxis(this.id)">Weeks</button>
            </div>
            <div>
            <button id="day" class="chooseAxis" type="radio" name="xAxis" onclick="xAxis(this.id)">Days</button>
            </div>
            <div>            <button id="hour" class="chooseAxis" type="radio" name="xAxis" onclick="xAxis(this.id)">Hours</button>
            </div>
       </div>
    </div>
       <div id=timebox
          <div id="timescale">
               <label class="bttn"> Limits:</label>
               <input id="pdstart">
               <input id="pdend">
               <button -id="devices"><-- Earlier</button>
               <button -id="usage">Later --></button>
          </div>
       </div>

</body>
<script type="text/javascript" src="report.js"></script>
</html>

