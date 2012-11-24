(function () {
    "use strict";

    WinJS.Namespace.define('Caching', {
        store: store,
        retrieve: retrieve,
    });

    function store(file, data, expires) {
        expires = expires || 3600000; // 1 hour is default
        var contents = JSON.stringify({ 'stored': new Date(), 'expires': expires, 'data': data });
        var temporaryFolder = Windows.Storage.ApplicationData.current.temporaryFolder;

        temporaryFolder.createFileAsync(file, Windows.Storage.CreationCollisionOption.replaceExisting).then(function (file) {
            data = JSON.stringify({ 'stored': new Date(), 'expires': 86400000, 'data': data });
            Windows.Storage.FileIO.writeTextAsync(file, contents).done();
        });
    }

    function retrieve(file, successCallback, errorCallback) {
        var temporaryFolder = Windows.Storage.ApplicationData.current.temporaryFolder;
        var cached = temporaryFolder.getFileAsync(file).then(function complete(file) {
            Windows.Storage.FileIO.readTextAsync(file).then(function (data) {
                if (data) {
                    var parsed = JSON.parse(data);
                    if (parsed.stored && parsed.expires && parsed.data) {
                        if (new Date() - new Date(parsed.stored) <= parsed.expires) {
                            successCallback(parsed.data);

                        } else {
                            // expired
                            errorCallback();
                        }
                    } else {
                        // unknown cache file format
                        errorCallback();
                    }

                } else {
                    // cache file empty
                    errorCallback();
                }
            }).done();

        }, function _error(e) {
            errorCallback();
        });
    }

})();