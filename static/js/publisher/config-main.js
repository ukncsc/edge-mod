
require(["knockout", "publisher/ConfigModel", "domReady!"], function (ko, ConfigModel) {
    var model = new ConfigModel();
    ko.applyBindings(model, document.getElementById("content"));
    model.getSites();
});
