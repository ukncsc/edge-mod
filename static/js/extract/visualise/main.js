require([
    "extract/visualise/ExtractViewModel",
    "domReady!"
], function (ExtractViewModel) {
    new ExtractViewModel(window['root_ids']);
});
