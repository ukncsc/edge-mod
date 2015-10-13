
require([
    "cert-ind-build/indicator_builder",
    "cert-ind-build/cert-ind-build-obs-address",
    "cert-ind-build/cert-ind-build-obs-domain-name",
    "cert-ind-build/cert-ind-build-obs-uri",
    "cert-ind-build/cert-ind-build-obs-email",
    "cert-ind-build/cert-ind-build-obs-file",
    "cert-ind-build/cert-ind-build-obs-artifact",
    "domReady!"
], function (indicator_builder,
             CERTObservableAddress,
             CERTObservableDomainName,
             CERTObservableURI,
             CERTObservableEmail,
             CERTObservableFile,
             CERTObservableArtifact) {
    indicator_builder.ObservableAddress = CERTObservableAddress;
    indicator_builder.ObservableDomainName = CERTObservableDomainName;
    indicator_builder.ObservableURI = CERTObservableURI;
    indicator_builder.ObservableEmail = CERTObservableEmail;
    indicator_builder.ObservableFile = CERTObservableFile;
    indicator_builder.ObservableArtifact = CERTObservableArtifact;
});
