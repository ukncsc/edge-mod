require([
    "extract/visualise/ExtractViewModel",
    "common/modal/show-error-modal",
    "domReady!"
], function (ExtractViewModel, showErrorModal) {
    try {
        new ExtractViewModel(window['root_ids'], window['indicator_information']);
    } catch (e) {
        showErrorModal(e.message, true);
    }
});
