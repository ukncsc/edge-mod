
require(["knockout-3.1.0", "publisher/SelectModel", "domReady!"], function (ko, SelectModel) {
    ko.applyBindings(new SelectModel(), document.getElementById("content"));
});
