
require([
    "cert-ind-build/indicator_builder",
    "cert-ind-build/cert-ind-build-obs-address",
    "domReady!"
], function (indicator_builder, CERTObservableAddress) {
    indicator_builder.ObservableAddress = CERTObservableAddress;
});
