require([
    "knockout",
    "common/modal/Modal",
    "activity-log/ActivityLogModel",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (ko, Modal, ActivityLogModel, errorContentTemplate) {
    try {
        var activityLogModel = new ActivityLogModel();
        ko.applyBindings(activityLogModel, document.getElementById("content"));
        activityLogModel.loadLog();
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
