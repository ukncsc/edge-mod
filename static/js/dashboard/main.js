document.getElementsByClassName("logo")[0].src = "/adapter/certuk_mod/static/plogo.png";
document.getElementById("ftr-btm").getElementsByClassName("navbar-right")[0].innerHTML =
    "Copyright &copy; 2016 Purple Secure Systems <a href=\"/crashlog/\" style=\"color:#aaa;text-decoration:none;\">*</a>";
require([
    "knockout",
    "dashboard/ViewModel"
], function (ko, ViewModel) {
    ko.applyBindings(new ViewModel(), document.getElementById("content"));
});
