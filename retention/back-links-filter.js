
function excludePackages() {
    var numNonPkg = 0;
    Object.keys(this.value).forEach(function (key) {
        if (this.value[key] !== "pkg") {
            numNonPkg += 1;
        }
    }.bind(this));
    return numNonPkg >= minimumBackLinks;
}
