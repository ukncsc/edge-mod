define([
    "dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "ind-build/validation",
    "ind-build/cert-ind-build-ready"
], function (declare, ko, indicator_builder, validation) {
    "use strict";

    var coreFileObservable = indicator_builder.ObservableFile;
    var CERTObservableFile = declare(indicator_builder.AbstractMassObservable, {
            constructor: coreFileObservable,

            getSearchValue: function () {
                coreFileObservable.prototype.getSearchValue.bind(this);
            },

            describeFirstHash: function (hashes) {
                coreFileObservable.prototype.describeFirstHash.bind(this)(hashes);
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
                if (title.length === 0) {
                    title = this.objectType() + " : " + value;
                    title = title.substring(0, 80);
                    title += idx ? (" " + String(idx)) : "";
                }

                var hashes = value.split(';');
                if (hashes.length > 0) {
                    var firstHash = hashes[0]
                    if (firstHash.indexOf('\'') == 0 || firstHash.indexOf('\"') == 0) {
                        title = firstHash.slice(1, -1)
                    }
                }

                return title;
            },

            save: function (idx) {
                if ((typeof idx != 'undefined') && indicator_builder.vm.builderMode().isBatchMode()) {
                    var value = this.getObjectValuesArray()[idx || 0];
                    var childFile = new CERTObservableFile();
                    childFile.objectTitle(this.getOrCreateTitle(value, idx));

                    var hashes = value.split(';');
                    for (var i = 0, len = hashes.length; i < len; i++) {
                        if (this.looksLikeFileName(hashes[i]) && i == 0) {
                            childFile.file_name(hashes[i].replace(/\"/g, "").replace(/\'/g, ""));
                            continue;
                        }
                        childFile.addHashInternal(this.getHashType(hashes[i]), hashes[i]);
                    }

                    return childFile.save();
                } else {
                    return coreFileObservable.prototype.save.bind(this);
                }
            },


            findIndexForHashType: function (hashType, hashes) {
                var idx = -1;
                for (var i = 0, len = hashes.length; i < len; i++) {
                    if (hashes[i].hash_type == hashType) {
                        idx = i;
                        break;
                    }
                }
                return idx;
            },

            addHashInternal: function (hashType, hashValue) {
                if (!(hashType && hashValue)) {
                    alert("Please select a hash type and enter a hash value");
                } else {
                    var newHash = {
                        hash_type: hashType,
                        hash_value: hashValue
                    };
                    var existingHashTypeIndex = this.findIndexForHashType(hashType, this.hashes());
                    if (existingHashTypeIndex >= 0) {
                        this.hashes()[existingHashTypeIndex] = newHash;
                        this.hashes.valueHasMutated();
                    } else {
                        this.hashes.push(newHash);
                    }
                    this.selected_hash("");
                    this.hash_value("");
                }
            },

            addHash: function (observableFile) {
                var hashType = observableFile.selected_hash();
                var hashValue = observableFile.hash_value();
                observableFile.addHashInternal(hashType, hashValue);
            },

            removeHash: function (hash) {
                this.hashes.remove(hash);
            },

            looksLikeFileName : function(value) {
                  return (value.indexOf('\'') == 0 || value.indexOf('\"') == 0 )
            },

            doValidation: declare.superCall(function (sup) {
                return function () {
                    if (indicator_builder.vm.builderMode().isBatchMode()) {
                        var msgs = sup.call(this);
                        ko.utils.arrayForEach(this.getObjectValuesArray(), function (value) {
                            var hashes = value.split(';');
                            for (var i = 0, len = hashes.length; i < len; i++) {
                                if (this.looksLikeFileName(hashes[i]) && i == 0) {
                                    continue;
                                }
                                if (this.getHashType(hashes[i]) === "Other") {
                                    msgs.addError("Unable to parse the following hash:" + hashes[i]);
                                }
                            }
                        }.bind(this));

                        return msgs;
                    }

                    return coreFileObservable.prototype.doValidation.bind(this)
                }
            }),

        });

    indicator_builder.ObservableFile = CERTObservableFile;
    return CERTObservableFile;
});
