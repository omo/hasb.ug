
function isValidURL(mayURL) {
  var a = document.createElement("a"); 
  a.href = mayURL;
  return a.href.toString() == mayURL;
}

function FormValidation(messageHolder) {

  var errors = [];
  var groupElement = messageHolder.closest(".control-group");

  this.error = function(message) {
    errors.push(message);
  };

  this.validate = function() {
    if (0 < errors.length) {
      messageHolder.text(errors[0]);
      groupElement.addClass("error");
      return false;
    } else {
      messageHolder.text("");
      groupElement.removeClass("error");
      return true;
    }
  };

  return this;
}


function MePage() {
  this.hostValidation = null;
  this.patternValidation = null;
};

MePage.prototype.wire = function() {
  $(".my-shortener").on("requested", function(evt) {
    $(evt.delegateTarget).find("a").attr("disabled", "true");
    $(evt.delegateTarget).find(".requested-cue-placeholder").attr("class", "icon-time");
  });
  $(".delete-shortener-button").on("click", this.didClickDelete.bind(this)); // FIXME: convert to global data-* handler + <form>

  $(".my-shortener-new")
    .on("submit", this.didSubmitCreate.bind(this))
    .on("requested", this.didRequestCreate.bind(this))
    .on("responded", this.didCreate.bind(this));
  $(".add-shortener-button").on("click", function(evt) { $(evt.target).closest("form").submit(); });
};

MePage.prototype.prepareValidateCreation = function()
{
  this.hostValidation = new FormValidation($("#host-validation-message"));
  this.patternValidation = new FormValidation($("#pattern-validation-message"));
};

MePage.prototype.validateCreation = function()
{

  var ok = true;
  var host = $("#host").val();
  var pattern = $("#pattern").val();
  
  if (!host.length)
    this.hostValidation.error("Host is required.");
  if (!host.match(/([a-z0-9]\.)+[a-z0-9]/))
    this.hostValidation.error("This doesn't look like a host name.");

  if (!pattern.length)
    this.patternValidation.error("Pattern is required.");
  if (0 != pattern.indexOf("http://") && 0 != pattern.indexOf("https://"))
    this.patternValidation.error("Needs to start with http(s)");
  if (-1 == pattern.indexOf("{id}"))
    this.patternValidation.error("The {id} placeholder is missing.");
  if (!isValidURL(pattern.replace("{id}", "12345")))
    this.patternValidation.error("Invalid as an URL.");

  return this.hostValidation.validate() & this.patternValidation.validate();
}

MePage.prototype.didCreate = function(evt, error) {

  if (error) {
    var toFocus = null;
    switch(error.name) {
    case "host":
      this.hostValidation.error(error.message);
      toFocus = $(evt.delegateTarget).find("#host");
      break;
    case "pattern":
      this.patternValidation.error(error.message);
      toFocus = $(evt.delegateTarget).find("#pattern");
      break;
    default:
      console.log(error);
      break;
    }

    $(evt.delegateTarget).find("input,button").attr("disabled", null);
    this.validateCreation();
    if (toFocus)
      toFocus.focus();
    return;
  }

  window.location.reload();
};

MePage.prototype.didRequestCreate = function(evt) {
  $(evt.delegateTarget).find("input,button").attr("disabled", "true");
};

MePage.prototype.didSubmitCreate = function(evt) {
  var topost = {
    host: $("#host").val(),
    pattern: $("#pattern").val(),
    canary: $("#canary").val()
  };

  this.prepareValidateCreation();
  if (!this.validateCreation()) {
    evt.preventDefault();
    return;
  }

  var target = evt.delegateTarget;

  $.ajax(
    "/s", 
    { type: "POST", data: topost,  headers: { "accept": "application/json" } }
  ).done(function(xhr) {
    $(target).trigger("responded");
  }.bind(this)).fail(function(xhr) {
    if (xhr.status == 403)
      $(target).trigger("responded", JSON.parse(xhr.responseText));
  }.bind(this));

  $(target).trigger("requested");
  evt.preventDefault();
}

MePage.prototype.didClickDelete = function(evt) {
  var host = evt.delegateTarget.dataset["host"];
  var canary = $("#canary").val();

  $.ajax(
    "/s/" + host, 
    { type: "DELETE", headers: { "x-hasbug-canary": canary } }
  ).done(function() {
    window.location.reload();
  });

  $(evt.delegateTarget).trigger("requested");
  evt.preventDefault();
}

function signout() {
  $("#form-signout").submit();
}

$(document).ready(function() {
  // For global navigation
  $("#nav-signout").on("click", signout);
  $(document).on("click", "a[disabled]", function(evt) { evt.preventDefault(); });

  if (0 == window.location.pathname.indexOf("/me")) {
    var f = new MePage();
    f.wire();
  }
});
