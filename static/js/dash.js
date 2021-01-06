// Javascript functions for dash.html

function Color(color, set){
  console.log("Color: " +color);
  var ct_series = document.getElementsByClassName('ct-series-a')[0];
  var line = ct_series.getElementsByClassName('ct-line')[0];
  var points = ct_series.getElementsByClassName('ct-point');
  var i;
  for(i = 0; i < points.length; i++){
    points[i].style.stroke = color;
  }
  var area = ct_series.getElementsByClassName('ct-area')[0];

  line.style.stroke = color;
  area.style.fill = color;
  console.log("colors should be changed!")
  if(set){
    var cookie_response = $.get('set_cookie?name=color&value=' + color);
  }
}

function changeColors() {
  var color = $('#colors option:selected').val();
  Color(color, true);
}

function setColor(){
  var data = $.get('get_cookie_color');
  var color;
  var extract = data.done(function (response) {
    color = response.color;
    console.log("setColor color: " + color);
  })
  Color(color, false);
}

function displayArea() {
  var ct_series = document.getElementsByClassName('ct-series-a')[0];
  var area = ct_series.getElementsByClassName('ct-area')[0];
  if(document.getElementById('display-area-check').checked){
    area.style.display = "block";
  }
  else{
    area.style.display = "none";
  }
}
