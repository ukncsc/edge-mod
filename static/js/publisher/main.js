
require(["knockout", "publisher/SelectModel", "domReady!"], function (ko, SelectModel) {
    ko.applyBindings(
        new SelectModel(root_id, root_type, stix_package),
        document.getElementById("content")
    );
});
