// Chart classes

class BasicChart{

  constructor(XData, YData, XLabel, YLabel)
  {
    this.XData = XData;
    this.YData = YData;
    this.XLabel = XLabel;
    this.YLabel = YLabel;
  }

  createGraph()
  {
    var data =
            {
              labels: this.XData,
              series:[
                      this.YData
              ]
            }
    new Chartist.Line(
      '.ct-chart',
      data, {
        showArea: true,
        axisY: {
          onlyInteger: true
        },
        plugins: [
        Chartist.plugins.ctAxisTitle({
          axisX: {
            axisTitle: this.XLabel,
            axisClass: "ct-axis-title",
            offset: {
              x: 0,
              y: 25
            },
            textAnchor: "bottom"
          },
          axisY: {
            axisTitle: this.YLabel,
            axisClass: "ct-axis-title",
            offset: {
              x: 0,
              y: 25
            },
            flipTitle: true
          }
        })
    ]});
  }
}

class GroupDashChart{

  constructor(XData, YData, XLabel, YLabel)
  {
    this.XData = XData;
    this.YData = YData;
    this.XLabel = XLabel;
    this.YLabel = YLabel;
  }

  createGraph()
  {
    var data =
            {
              labels: this.XData,
              series:this.YData
            }
    new Chartist.Line(
      '.ct-chart',
      data,
       {
        showArea: true,
        axisY: {
          onlyInteger: true
        },
        plugins: [
        Chartist.plugins.ctAxisTitle({
          axisX: {
            axisTitle: this.XLabel,
            axisClass: "ct-axis-title",
            offset: {
              x: 0,
              y: 25
            },
            textAnchor: "bottom"
          },
          axisY: {
            axisTitle: this.YLabel,
            axisClass: "ct-axis-title",
            offset: {
              x: 0,
              y: 25
            },
            flipTitle: true
          }
        }),
        Chartist.plugins.tooltip()
    ]});
  }
}
class IndexChart{

  constructor(XData, YData, XLabel, YLabel)
  {
    this.XData = XData;
    this.YData = YData;
    this.XLabel = XLabel;
    this.YLabel = YLabel;
  }

  createGraph()
  {
    var data =
            {
              labels: this.XData,
              series:this.YData
            }
    new Chartist.Line(
      '.ct-chart',
      data,
       {
        showArea: false,
        axisY: {
          onlyInteger: true
        },
        plugins: [
        Chartist.plugins.ctAxisTitle({
          axisX: {
            axisTitle: this.XLabel,
            axisClass: "ct-axis-title",
            offset: {
              x: 0,
              y: 25
            },
            textAnchor: "bottom"
          },
          axisY: {
            axisTitle: this.YLabel,
            axisClass: "ct-axis-title",
            offset: {
              x: 0,
              y: 25
            },
            flipTitle: true
          }
        })
    ]});
  }
}
