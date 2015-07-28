
require(["knockout", "publisher/SelectModel", "domReady!"], function (ko, SelectModel) {
    ko.applyBindings(new SelectModel(), document.getElementById("content"));
});
