
require(["knockout", "publisher/SelectModel", "domReady!"], function (ko, SelectModel) {
    ko.applyBindings(
        new SelectModel(rootId, stixPackage),
        document.getElementById("content")
    );
});
