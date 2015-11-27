function sightingsReduce(key, values) {
    var count = 0;
    for (var i = 0; i < values.length; i++) {
        count += values[i];
    }
    return count;
}
