
require(["knockout", "publisher/SelectModel", "domReady!"], function (ko, SelectModel) {
    var model = new SelectModel();
    ko.applyBindings(model, document.getElementById("content"));
    model.select({ id: stix_id });
});
