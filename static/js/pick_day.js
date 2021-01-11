$(function(ready){
  $("#today").change(function() {
    var today;
    if (this.checked) {
        var yesterday = document.getElementById("yesterday");
        if (yesterday.checked){
          yesterday.checked = false;
        }
        var now = new Date();
        today = now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + now.getDate();
    } else {
        dateStr = "";
    }
    $("#day").val(today);
  });

  $("#yesterday").change(function() {
    var yesterday;
    if (this.checked) {
        var today = document.getElementById("today");
        if (today.checked){
          today.checked = false;
        }
        var now = new Date();
        yesterday = now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + (now.getDate() - 1);
    } else {
        dateStr = "";
    }
    $("#day").val(yesterday);
  });
});
