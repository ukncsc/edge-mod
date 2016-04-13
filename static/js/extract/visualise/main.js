require([
    "extract/visualise/ExtractViewModel",
    "domReady!"
], function (ExtractViewModel) {
    try {
        new ExtractViewModel(window['root_ids']);
    } catch (e) {
        var errorModal = new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: e.message,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        });

        errorModal.getButtonByLabel("OK").callback = history.back.bind(history);
        errorModal.show();
    }
});
