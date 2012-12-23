function addShortener(evt) {
  var topost = {
    host: $("#host").val(),
    pattern: $("#pattern").val(),
    canary: $("#canary").val()
  };

  $.ajax(
    "/s", 
    { type: "POST", data: topost }
  ).done(function() {
    window.location.reload();
  });

  $(this).trigger("requested");
  evt.preventDefault();
}

function deleteShortener(evt) {
  var host = this.dataset["host"];
  var canary = $("#canary").val();
  $.ajax(
    "/s/" + host, 
    { type: "DELETE", headers: { "x-hasbug-canary": canary } }
  ).done(function() {
    window.location.reload();
  });

  $(this).trigger("requested");
  evt.preventDefault();
}

function cueRequested() {
  $(this).find(".requested-cue-placeholder").attr("class", "icon-time");
  $(this).find("input,button").attr("disabled", "true");
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
    $(".my-shortener").on("requested", cueRequested);
    $(".my-shortener-new").on("requested", cueRequested);
  }
});
