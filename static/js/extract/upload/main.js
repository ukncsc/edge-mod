require([
    "knockout",
    "extract/upload/ExtractUploadModel",
    "domReady!"
], function (ko, ExtractUploadModel) {
    try {
        ko.applyBindings(new ExtractUploadModel(), document.getElementById("content"));
    }
    catch (e) {
        console.log(e);
    }
});
