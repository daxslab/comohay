let Autocomplete = function (options) {
    this.search_container_id = options.search_container_id;
    this.search_input_class_name = options.search_input_class_name;
    this.autocomplete_list_class_name = options.autocomplete_list_class_name;
    this.search_form_class_name = options.search_form_class_name;
    this.button_cancel_id = options.button_cancel_id;
    this.url = options.url || 'search/autocomplete/';
    this.delay = parseInt(options.delay || 300);
    this.minimum_length = parseInt(options.minimum_length || 3);
    this.query_box = null;
    this.autocomplete_list = null;
    this.search_from = null;
};

Autocomplete.prototype.setup = function () {
    let self = this;

    this.query_box = document.getElementsByClassName(this.search_input_class_name)[0];
    // Watch the input box.
    this.query_box.addEventListener('keydown', function (event) {
        //check if its a valid key and the query box has some string as value
        let key = event.key;
        if ((key.length === 1 || key === 'Backspace' || key === 'Process') && this.value.trim() !== '') {
            self.show();

            let query = self.query_box.value;

            if (query.length < self.minimum_length) {
                self.autocomplete_list.innerHTML = '';
                return false
            }

            self.fetch(query);
        } else if (key === 'Escape') {
            event.preventDefault();
            self.hide();
        }
    });


    // On selecting a result, populate the search field.
    this.autocomplete_list = document.getElementsByClassName(this.autocomplete_list_class_name)[0]
    this.autocomplete_list.childNodes.forEach(function (value, key, parent) {
        value.addEventListener('click', function (event) {
            self.list_item_on_click(event);
        });
    });

    window.addEventListener('click', function (e) {
        if (!document.getElementById(self.search_container_id).contains(e.target)) {
            self.hide();
        } else {
            self.show();
        }
    });

    let button_cancel = document.getElementById(this.button_cancel_id);
    button_cancel.addEventListener('click', function (e) {
        e.preventDefault();
        self.clear_results();
        self.query_box.value = '';
        self.query_box.focus();
    });

    this.search_from = document.getElementsByClassName(this.search_form_class_name)[0];
};

Autocomplete.prototype.clear_results = function () {
    this.autocomplete_list.innerHTML = '';
};

Autocomplete.prototype.hide = function () {
    this.autocomplete_list.style.display = 'none';
};

Autocomplete.prototype.show = function () {
    this.autocomplete_list.style.display = null;
};

Autocomplete.prototype.fetch = function (query) {
    let self = this;

    let cached_response = this.get_cached_response(query);

    if (cached_response) {
        self.show_results(cached_response.results);
    } else {
        let request = new XMLHttpRequest();
        request.open("GET", this.url + '?q=' + query, true);
        request.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                self.save_response(query, request.responseText);
                let data = JSON.parse(request.responseText);
                self.show_results(data.results);
            }
        };
        request.send();
    }
};

Autocomplete.prototype.save_response = function (query, response) {
    // Check for browser support
    if (typeof Storage === "undefined")
        return false;

    sessionStorage.setItem(query.toLowerCase(), response);
    return true;
};

Autocomplete.prototype.get_cached_response = function (query) {
    // Check for browser support
    if (typeof Storage === "undefined")
        return false;

    query = query.toLowerCase();

    if (!sessionStorage.getItem(query))
        return false;

    return JSON.parse(sessionStorage.getItem(query));
};

Autocomplete.prototype.show_results = function (results) {
    let self = this;

    // Remove any existing results.
    this.clear_results();

    if (results.length > 0) {

        let searchExp = this.query_box.value.trim().replace(' ', '|').replace('\\', "\\\\");

        for (let res_offset in results) {
            let elem = document.createElement('li');
            let filteredText = results[res_offset];

            let regEx = new RegExp(searchExp, "ig");
            let matches = filteredText.match(regEx);

            if (matches)
                matches.forEach(function (match, idx) {
                    filteredText = filteredText.replace(match, "%%%%" + match + "&&&&")
                });

            filteredText = filteredText.replace(/%%%%/gi, "<span style='font-weight: initial'>");
            filteredText = filteredText.replace(/&&&&/gi, "</span>");

            elem.innerHTML = `<strong>${filteredText}</strong>`;
            elem.style.cursor = 'default';
            elem.addEventListener('click', function (event) {
                self.list_item_on_click(event);
            });

            this.autocomplete_list.appendChild(elem);
        }
    }
};

Autocomplete.prototype.list_item_on_click = function (event) {
    let self = this;
    this.query_box.value = event.target.textContent;
    this.clear_results();
    this.search_from.submit();
    return false;
};

document.addEventListener('DOMContentLoaded', function () {
    window.autocomplete = new Autocomplete({
        search_input_class_name: 'search-input',
        autocomplete_list_class_name: 'autocomplete-list',
        search_form_class_name: 'search-form',
        search_container_id: 'search-container',
        button_cancel_id: 'button-cancel'
    });
    window.autocomplete.setup();
});
