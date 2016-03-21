require([
    "knockout",
    "extract/ExtractModel",
    "domReady!"
], function (ko, ExtractModel) {
    try {
        ko.applyBindings( new ExtractModel(), document.getElementById("content"));
    }
    catch (e) {
        console.log(e);
    }
});
