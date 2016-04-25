require([
    "knockout",
    "common/modal/ShowErrorModal",
    "activity-log/ActivityLogModel",
    "domReady!"
], function (ko, ShowErrorModal, ActivityLogModel) {
    try {
        var activityLogModel = new ActivityLogModel();
        ko.applyBindings(activityLogModel, document.getElementById("content"));
        activityLogModel.loadLog();
    } catch (e) {
        ShowErrorModal(e.message, true);
    }
});
