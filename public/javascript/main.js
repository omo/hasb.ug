function addShortener() {
  var topost = {
    host: $("#host").val(),
    pattern: $("#pattern").val(),
    canary: $("#canary").val()
  };

  $.ajax("/s", { type: "POST", data: topost });
  // FIXME: update view
}

function deleteShortener() {
  var host = this.dataset["host"];
  var canary = $("#canary").val();
  $.ajax("/s/" + host, { type: "DELETE", headers: { "x-hasbug-canary": canary } });
  // FIXME: update view
}

function signout() {
  $("#form-signout").submit();
}

$(document).ready(function() {
  // For global navigation
  $("#nav-signout").on("click", signout);
  if (0 == window.location.pathname.indexOf("/me")) {
    $(".add-shortener-button").on("click", addShortener);
    $(".delete-shortener-button").on("click", deleteShortener);
  }
});
