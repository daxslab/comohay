let Autocomplete = function (options) {
    this.search_container_id = options.search_container_id;
    this.search_input_class_name = options.search_input_class_name;
    this.autocomplete_list_class_name = options.autocomplete_list_class_name;
    this.search_form_class_name = options.search_form_class_name;
    this.button_cancel_id = options.button_cancel_id;
    this.autosuggestion_indicator_id = options.autosuggestion_indicator_id;
    this.url = options.url || 'search/autocomplete/';
    this.delay = parseInt(options.delay || 300);
    this.minimum_length = parseInt(options.minimum_length || 3);
    this.query_box = null;
    this.autocomplete_list = null;
    this.search_from = null;
    this.cache_version = options.cache_version || 1;
    this.cache_name = options.cache_name || 'comohay_autocomplete';
    this.cache_full_name = this.cache_name + '-' + this.cache_version;
    this.cache_time = 30;

    if (typeof (Storage) !== "undefined") {
        if (localStorage.cache_timestamp) {
            let current_date = Date.now();
            if (current_date - (this.cache_time * 1000) > localStorage.cache_timestamp) {
                // deleteOldCaches(this.cache_full_name, this.cache_name);
                this.deleteOldCaches();
                localStorage.setItem("cache_timestamp", Date.now());
            }
        } else {
            localStorage.setItem("cache_timestamp", Date.now());
        }

    } else {
        // Sorry! No Web Storage support..
    }

};

Autocomplete.prototype.getCachedData = async function (url) {
    cacheName = this.cache_full_name;
    const cacheStorage = await caches.open(cacheName);
    const cachedResponse = await cacheStorage.match(url);

    if (!cachedResponse || !cachedResponse.ok) {
        return false;
    }

    return await cachedResponse.json();
};

Autocomplete.prototype.deleteOldCaches = async function () {
    let currentCache = this.cache_full_name;
    let cache_key_prefix = this.cache_name;
    const keys = await caches.keys();

    for (const key of keys) {
        const isOurCache = cache_key_prefix === key.substr(0, cache_key_prefix.length);

        if (currentCache === key || !isOurCache) {
            caches.delete(key);
        }
    }
};

Autocomplete.prototype.setup = function () {
    let self = this;

    this.autocomplete_list = document.getElementsByClassName(this.autocomplete_list_class_name)[0];
    this.query_box = document.getElementsByClassName(this.search_input_class_name)[0];
    this.autosuggestion_indicator = document.getElementById(this.autosuggestion_indicator_id);

    // Watch the input box.
    this.query_box.addEventListener('input', function (event) {

        // remove query as an autosuggestion
        self.autosuggestion_indicator.disabled = true;

        self.show();

        let query = this.value;

        if (query.length < self.minimum_length) {
            self.autocomplete_list.innerHTML = '';
            return false
        }

        self.fetch(query);
    });

    this.query_in_process = null;

    // Close suggestion list on Escape and on Tab
    this.query_box.addEventListener('keydown', function (event) {
        let key = event.key;
        if (key === 'Escape' || key === 'Tab') {
            self.hide();
            // Removing default behaviour specially for Chrome
            if (event.key === 'Escape') {
                event.preventDefault();
            }
        } else if ((key === 'ArrowDown' || key === 'ArrowUp') && self.autocomplete_list.childNodes.length > 0) {
            event.preventDefault();

            let to_highlight = null;

            let highlighted_li = self.find_highlighted_list_item();

            if (highlighted_li) {
                self.clear_highlighted_list_item(highlighted_li);
                let next_or_prev = key === 'ArrowDown' ? highlighted_li.nextElementSibling : highlighted_li.previousElementSibling;
                to_highlight = next_or_prev ? next_or_prev : to_highlight;
            } else {
                to_highlight = key === 'ArrowDown' ? self.autocomplete_list.childNodes[0] : self.autocomplete_list.childNodes[self.autocomplete_list.childNodes.length - 1]
                self.query_in_process = this.value;
            }

            if (to_highlight) {
                self.highlight_list_item(to_highlight);
                this.value = to_highlight.textContent;
                // set query as an autosuggestion
                self.autosuggestion_indicator.disabled = false;
            } else {
                this.value = self.query_in_process;
                // remove query as an autosuggestion
                self.autosuggestion_indicator.disabled = true;
            }
        }
    });

    let search_container = document.getElementById(this.search_container_id);

    // show autocomplete list on focus in
    search_container.addEventListener('focusin', function (event) {
        self.show();
    });

    // hide autocomplete list  on click outside the box
    window.addEventListener('click', function (e) {
        if (!search_container.contains(e.target)) {
            self.hide();
        } else {
            self.show();
        }
    });

    // clear query on cancel button click
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
    let url = this.url + '?q=' + query;
    let cacheName = self.cache_full_name;
    self.getCachedData(url)
        .then((cachedData) => {
            if (cachedData) {
                self.show_results(cachedData);
            } else {
                caches.open(cacheName).then((cacheStorage) => {
                    cacheStorage.add(url).then(() => {
                        self.getCachedData(url).then((cachedData) => {
                            self.show_results(cachedData);
                        });
                    });
                });
            }

        });
};

Autocomplete.prototype.show_results = function (data) {
    let self = this;
    // Remove any existing results.
    this.clear_results();

    let results = data.results || [];

    if (results.length > 0) {

        let searchExp = this.query_box.value.trim().replace(' ', '|').replace('\\', "\\\\");

        for (let res_offset in results) {
            let elem = document.createElement('li');
            elem.setAttribute('tabindex', '-1');
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
                self.list_item_on_click(this);
            });

            elem.addEventListener('mouseover', function (event) {
                let to_clear = self.find_highlighted_list_item();

                if (to_clear)
                    self.clear_highlighted_list_item(to_clear);

                self.highlight_list_item(this);
            });

            elem.addEventListener('mouseout', function (event) {
                self.clear_highlighted_list_item(this);
            });

            this.autocomplete_list.appendChild(elem);
        }
    }
};

Autocomplete.prototype.find_highlighted_list_item = function () {
    let elems = document.getElementsByClassName('autocomplete-highlight');

    if (elems.length > 0)
        return elems[0];

    return false
};

Autocomplete.prototype.clear_highlighted_list_item = function (li) {
    removeClass(li, 'autocomplete-highlight');
};

Autocomplete.prototype.highlight_list_item = function (li) {
    addClass(li, 'autocomplete-highlight')
};

Autocomplete.prototype.list_item_on_click = function (list_item) {
    let self = this;

    this.query_box.value = list_item.textContent;

    // set query as an autosuggestion
    this.autosuggestion_indicator.disabled = false;

    this.clear_results();

    this.search_from.submit();

    return false;
};

let input = document.getElementById('id_q');
let cache_time = parseInt(input.dataset.autocompleteCache);
document.addEventListener('DOMContentLoaded', function () {
    window.autocomplete = new Autocomplete({
        search_input_class_name: 'search-input',
        autocomplete_list_class_name: 'autocomplete-list',
        search_form_class_name: 'search-form',
        search_container_id: 'search-container',
        button_cancel_id: 'button-cancel',
        cache_time: cache_time,
        autosuggestion_indicator_id: 'autosuggestion-hi'
    });
    window.autocomplete.setup();
});

