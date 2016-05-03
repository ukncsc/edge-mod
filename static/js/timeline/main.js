require([
    "timeline/timeline",
    "common/modal/Modal",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (TimeLine, Modal, errorContentTemplate) {
    try {
        new TimeLine("incidentTimelineSVG", window['rootId']);
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
