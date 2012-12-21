function addShortener() {
  var topost = {
    host: $("#host").val(),
    pattern: $("#pattern").val(),
    canary: $("#canary").val()
  };

  $.ajax("/s", { type: "POST", data: topost });
}

function deleteShortener() {
  var host = this.dataset["host"];
  var canary = $("#canary").val();
  $.ajax("/s/" + host, { type: "DELETE", headers: { "x-hasbug-canary": canary } });
}

$(document).ready(function() {
  if (0 == window.location.pathname.indexOf("/me")) {
    $(".add-shortener-button").on("click", addShortener);
    $(".delete-shortener-button").on("click", deleteShortener);
  }
});
