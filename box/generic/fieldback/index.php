<!DOCTYPE html>
<html>
<head>
<title>Creating Dynamic Data Graph using PHP and Chart.js</title>
<style type="text/css">
BODY {
    width: 550PX;
}

#chart-container {
    width: 100%;
    height: auto;
}
</style>
<script type="text/javascript" src="/common/js/jquery.min.js"></script>
<script type="text/javascript" src="./Chart.bundle.js"></script>


</head>
<body>
    <div id="chart-container">
        <canvas id="graphCanvas"></canvas>
    </div>

    <script>
        $(document).ready(function () {
            showGraph();
        });


        function showGraph()
        {
            {
                $.post("fetch.php",
                function (data)
                {
                dataDict = JSON.parse(data);
                    console.log(dataDict);
                     var name = [];
                    var marks = [];

                    for (var i=0;i<dataDict.length;i++) {
                        name.push(dataDict[i].datestr);
                        marks.push(dataDict[i].connected_time);
                    }

                    var chartdata = {
                        labels: name,
                        datasets: [
                            {
                                label: 'Connection Time',
                                backgroundColor: '#49e2ff',
                                borderColor: '#46d5f1',
                                hoverBackgroundColor: '#CCCCCC',
                                hoverBorderColor: '#666666',
                                data: marks
                            }
                        ]
                    };

                    var graphTarget = $("#graphCanvas");

                    var barGraph = new Chart(graphTarget, {
                        type: 'bar',
                        data: chartdata
                    });
                });
            }
        }
        </script>

</body>
</html>

