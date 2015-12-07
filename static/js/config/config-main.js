
require(["knockout", "config/ConfigModel", "domReady!"], function (ko, ConfigModel) {
    var model = new ConfigModel();
    ko.applyBindings(model, document.getElementById("content"));
});
