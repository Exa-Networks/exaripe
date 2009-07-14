function showPrefix(t,id) {
  elt = document.getElementById(id);
  var loc = document.getElementById("loc");
  loc.innerHTML = elt.innerHTML;
  loc.style.display = "block";
}

function hidePrefix() {
  document.getElementById("loc").innerHTML = "";
  var loc = document.getElementById("loc");
  loc.style.display = "none";
}

function showPrefixAlert(t,id) {

  elt = document.getElementById(id);

  if (elt == undefined)
    return;

  var txt = "";

  kids = elt.childNodes;

  for (var i = 0; i < kids.length; i++) {
    if (kids[i].innerHTML != "") {
      txt += kids[i].innerHTML;
      txt += "\n";
    }
  }

  alert(txt);

}
