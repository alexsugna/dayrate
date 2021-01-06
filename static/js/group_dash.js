function displayAreas() {
  var ct_seriess = document.getElementsByClassName('ct-series');
  var display;
  if(document.getElementById('display-area-check').checked){
    display = "block";
  }
  else{
    display = "none";
  }
  var i;
  for(i = 0; i < ct_seriess.length; i++){
    var area = ct_seriess[i].getElementsByClassName('ct-area')[0];
    area.style.display = display;
  }
}

function changeColors(username){
  
}
