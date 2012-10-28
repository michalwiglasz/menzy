(function () {
    "use strict";

    var list = new WinJS.Binding.List();
    var groupedItems = list.createGrouped(
        function groupKeySelector(item) { return item.group.key; },
        function groupDataSelector(item) { return item.group; }
    );

    // Load list
    Caching.retrieve('list.json', function success(data) {
        for (var id in data) {
            list.push(wakeUp(data[id]));
        }
    }, function error() {
        loadList(list, function store(data) {
            Caching.store('list.json', data, 86400000);
        });
    });


    WinJS.Namespace.define("Data", {
        items: groupedItems,
        groups: groupedItems.groups,
        getItemReference: getItemReference,
        getItemsFromGroup: getItemsFromGroup,
        resolveGroupReference: resolveGroupReference,
        resolveItemReference: resolveItemReference,
        reloadList: function () {
            while (list.length) list.pop();
            loadList(list);
        }
    });

    WinJS.Namespace.define("Converters", {
        todayHours: WinJS.Binding.converter(getTodayHours),
        itemIsOpenClassName: WinJS.Binding.converter(function (x) {
            return "item " + getOpenToClassName(x);
        })
    });

    WinJS.Namespace.define("Utils", {
        getToday: getToday
    });

    // Get a reference for an item, using the group key and item title as a
    // unique reference to the item that can be easily serialized.
    function getItemReference(item) {
        return [item.group.key, item.id];
    }

    // This function returns a WinJS.Binding.List containing only the items
    // that belong to the provided group.
    function getItemsFromGroup(group) {
        return list.createFiltered(function (item) { return item.group.key === group.key; });
    }

    // Get the unique group corresponding to the provided group key.
    function resolveGroupReference(key) {
        for (var i = 0; i < groupedItems.groups.length; i++) {
            if (groupedItems.groups.getAt(i).key === key) {
                return groupedItems.groups.getAt(i);
            }
        }
    }

    // Get a unique item from the provided string array, which should contain a
    // group key and an item title.
    function resolveItemReference(reference) {
        for (var i = 0; i < groupedItems.length; i++) {
            var item = groupedItems.getAt(i);
            if (item.group.key === reference[0] && item.id === reference[1]) {
                return item;
            }
        }
    }

    // Returns an array of sample data that can be added to the application's
    // data list. 
    function loadList(list, responseCallback) {  
        WinJS.xhr({url: "http://localhost:5000/api/list.json"}).then(
            function (result) {
                var parsed = JSON.parse(result.response);
                for (var id in parsed) {
                    var item = parsed[id];
                    list.push(wakeUp(item));
                }

                if (responseCallback) {
                    responseCallback(parsed);
                }
            },
            function (result) {
                var dialog = Windows.UI.Popups.MessageDialog("Bohužel se nepodařilo stáhnout seznam menz.", "Server není dostupný.");
                dialog.commands.append(new Windows.UI.Popups.UICommand("OK"));
                dialog.showAsync()
        });
    }

    function wakeUp(item) {
        //var noImage = 'http://www.kam.vutbr.cz/obr/logo_kam.png';
        var noImage = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXY3B0cPoPAANMAcOba1BlAAAAAElFTkSuQmCC";
        item.group = { key: "all", title: "Všechny menzy" };
        item.hasImg = !!item.img;
        item.img = item.img || noImage;
        return item;
    }

    function getTodayHours(hours) {
        if (hours == null) {
            return null;
        }
        // get today's opening hours
        return 'Dnes ' + hours[getToday()].text.join(' a ');
    }

    function getOpenToClassName(hours) {
        return isOpen(hours) ? 'open' : 'closed';
    }

    function isOpen(hours) {
        if (hours == null)
            return null;

        var today = getToday();
        var from = hours[today].from;
        var to = hours[today].to;
        var now = new Date().getHours();

        for (var i = 0; i < from.length; i++) {
            if (from[i] <= now && to[i] > now)
                return true;
        }

        return false;

    }

    function getToday() {
        return ['sun', 'mon', 'tue', 'wed', 'thu', 'fri'][new Date().getDay()];
    }

})();
