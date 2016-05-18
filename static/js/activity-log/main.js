require([
    "knockout",
    "common/modal/show-error-modal",
    "activity-log/ActivityLogModel",
    "domReady!"
], function (ko, showErrorModal, ActivityLogModel) {
    try {
        var activityLogModel = new ActivityLogModel();
        ko.applyBindings(activityLogModel, document.getElementById("content"));
        activityLogModel.loadLog();
    } catch (e) {
        showErrorModal(e.message, true);
    }
});
