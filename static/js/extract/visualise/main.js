require([
    "extract/visualise/ExtractViewModel",
    "common/modal/show-error-modal",
    "domReady!"
], function (ExtractViewModel, showErrorModal) {
    try {
        new ExtractViewModel(window['root_ids']);
    } catch (e) {
        showErrorModal(e.message, true);
    }
});
