(function () {
    "use strict";

    WinJS.UI.Pages.define("/pages/itemDetail/itemDetail.html", {
        // This function is called whenever a user navigates to this page. It
        // populates the page elements with the app's data.
        ready: function (element, options) {
            var item = options && options.item ? Data.resolveItemReference(options.item) : Data.items.getAt(0);
            element.querySelector(".titlearea .pagetitle").textContent = item.name;
            element.querySelector("article .item-subtitle").textContent = item.address;

            if (item.hasImg) {
                element.querySelector("article .item-image").style.display = null;
                element.querySelector("article .item-image").src = item.img;
                element.querySelector("article .item-image").alt = item.name;
            } else {
                element.querySelector("article .item-image").style.display = 'none';
            }

            var el_content = element.querySelector("article .item-content");
            var paragraphs = item.description.split("\n");
            for (var i = 0; i < paragraphs.length; i++) {
                var p = document.createElement('p');
                p.innerText = paragraphs[i];
                el_content.appendChild(p);
            }
            element.querySelector(".content").focus();

            // opening hours
            var days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
            var today = new Date().getDay();

            // 1. find longest list
            var maxLength = 0;
            for (var d = 0; d < days.length; d++) {
                var day = days[d];
                var length = item.hours[day].text.length;
                if (length > maxLength) {
                    maxLength = length;
                }
            }

            // 2. create table cells
            for (var d = 0; d < days.length; d++) {
                var day = days[d];
                var hours = item.hours[day].text;
                var tr = element.querySelector("article .hours-" + day);
                
                if (d == today) {
                    tr.className += ' today';
                }

                for (var i = 0; i < hours.length; i++) {
                    var cell = document.createElement('td');
                    if (!i && hours.length < maxLength) {
                        cell.colSpan = maxLength - hours.length + 1
                    }
                    cell.innerText = hours[i];
                    tr.appendChild(cell);
                }
            }

            // 3. change css styles
            element.querySelector("article .item-hours").className += " item-hours-" + maxLength;
            element.querySelector("article .item-image").className += " item-hours-" + maxLength;
        }
    });
})();
