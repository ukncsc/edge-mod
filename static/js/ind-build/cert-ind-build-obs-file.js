define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "ind-build/validation",
    "ind-build/cert-ind-build-ready"//ensures that the ViewModel is set up
], function (declare, ko, indicator_builder) {
    "use strict";

    var coreFileObservable = indicator_builder.ObservableFile;
    var CERTObservableFile = declare(indicator_builder.AbstractMassObservable, {
        declaredClass: "CERTObservableFile",

        constructor: coreFileObservable,

        getSearchValue: function () {
            coreFileObservable.prototype.getSearchValue.bind(this)();
        },

        load: function (data) {
            coreFileObservable.prototype.load.bind(this)(data);
        },

        getHashType: function (hashValue) {
            if (!(/^[0-9A-F]+$/i.test(hashValue))) {
                if (/^(\d+):([\w/+]+):([\w/+]+),"([\w/\s\.-]+)"$/.test(hashValue)) {
                    return "SSDeep";
                }
                return "Other";
            }

            switch (hashValue.length) {
                case 32:
                    return "MD5";
                case 40:
                    return "SHA1";
                case 56:
                    return "SHA224";
                case 64:
                    return "SHA256";
                case 96:
                    return "SHA384";
                case 128:
                    return "SHA512";
            }

            if (hashValue.length > 40 && hashValue.length < 128) {
                return "MD6";
            }

            return "Other";
        },

        getOrCreateTitle: function (value, idx) {
            var title = this.objectTitle();
            if (title.length != 0) {
                return title;
            }

            var firstHash = value.split(';')[0];
            if (this.looksLikeFileName(firstHash)) {
                return firstHash.slice(1, -1);
            }

            title = this.objectType() + " : " + value;
            title = title.substring(0, 80);
            title += idx ? (" " + String(idx)) : "";
            return title;
        },

        save: function (idx) {
            if (typeof idx === 'undefined') {
                return coreFileObservable.prototype.save.bind(this)();
            }

            var value = this.getObjectValuesArray()[idx || 0];
            var childFile = new CERTObservableFile();
            childFile.objectTitle(this.getOrCreateTitle(value, idx));

            var hashes = value.split(';');
            for (var i = 0, len = hashes.length; i < len; i++) {
                if (this.looksLikeFileName(hashes[i]) && i == 0) {
                    childFile.file_name(hashes[i].slice(1, -1));
                    if (childFile.file_name().indexOf('.') > -1) {
                        childFile.file_extension(childFile.file_name().split('.')[1]);
                    }
                    continue;
                }

                childFile.hash_value(hashes[i]);
                childFile.selected_hash(this.getHashType(hashes[i]));

                this.addHash(childFile);
            }

            return childFile.save();
        },

        addHash: function (observableFile) {
            coreFileObservable.prototype.addHash.bind(observableFile)(observableFile)
        },

        removeHash: function (hash) {
            coreFileObservable.prototype.removeHash.bind(this)(hash);
        },

        looksLikeFileName: function (value) {
            return (value.indexOf('\'') == 0 || value.indexOf('\"') == 0 )
        },

        doValidation: declare.superCall(function (sup) {
            return function () {

                if (!indicator_builder.vm.builderMode().isBatchMode()) {
                    return coreFileObservable.prototype.doValidation.bind(this)();
                }

                var msgs = sup.call(this);
                ko.utils.arrayForEach(this.getObjectValuesArray(), function (value) {
                    var hashes = value.split(';');
                    for (var i = 0, len = hashes.length; i < len; i++) {
                        if (this.looksLikeFileName(hashes[i]) && i == 0) {
                            continue;
                        }

                        if (this.getHashType(hashes[i]) === "Other") {
                            msgs.addError("Unable to parse the hash:" + hashes[i]);
                        }
                    }
                }.bind(this));

                return msgs;
            }
        })
    });

    indicator_builder.ObservableFile = CERTObservableFile;
    return CERTObservableFile;
});
