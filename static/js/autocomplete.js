var Autocomplete = function (options) {
    this.search_input_class_name = options.search_input_class_name
    this.autocomplete_list_class_name = options.autocomplete_list_class_name
    this.search_form_class_name = options.search_form_class_name
    this.url = options.url || 'search/autocomplete/'
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length || 3)
    this.query_box = null
    this.autocomplete_list = null
    this.search_from = null
}

Autocomplete.prototype.setup = function () {
    let self = this

    this.query_box = document.getElementsByClassName(this.search_input_class_name)[0]
    // Watch the input box.
    this.query_box.addEventListener('keyup', function (event) {
        var query = self.query_box.value

        if (query.length < self.minimum_length) {
            self.autocomplete_list.innerHTML = ''
            return false
        }

        self.fetch(query)
    })

    // On selecting a result, populate the search field.
    this.autocomplete_list = document.getElementsByClassName(this.autocomplete_list_class_name)[0]
    this.autocomplete_list.childNodes.forEach(function (value, key, parent) {
        value.addEventListener('click', function (event) {
            self.list_item_on_click(event)
        })
    })

    this.search_from = document.getElementsByClassName(this.search_form_class_name)[0]
}

Autocomplete.prototype.fetch = function (query) {
    let self = this
    let request = new XMLHttpRequest();
    request.open("GET", this.url + '?q=' + query, true);
    request.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let data = JSON.parse(request.responseText)
            self.show_results(data)
        }
    }
    request.send()
}

Autocomplete.prototype.show_results = function (data) {
    let self = this
    // Remove any existing results.
    this.autocomplete_list.innerHTML = ''

    let results = data.results || []

    if (results.length > 0) {

        let searchExp = this.query_box?.value.trim().replace(' ', '|')

        for (let res_offset in results) {
            let elem = document.createElement('li');
            let filteredText = results[res_offset]

            let regEx = new RegExp(searchExp, "ig")
            let matches = filteredText.match(regEx)
            if (matches)
                matches.forEach(function (match, idx) {
                    filteredText = filteredText.replace(match, "<strong>" + match + "</strong>")
                })

            elem.innerHTML = filteredText

            elem.addEventListener('click', function (event) {
                self.list_item_on_click(event)
            })

            this.autocomplete_list.appendChild(elem)
        }
    }
    // else {
    //     var elem = base_elem.clone()
    //     elem.text("No results found.")
    //     results_wrapper.append(elem)
    // }

    // this.query_box.after(results_wrapper)
}

Autocomplete.prototype.list_item_on_click = function (event) {
    let self = this
    this.query_box.value = event.target.textContent
    this.autocomplete_list.innerHTML = ''
    this.search_from.submit()
    return false
}

document.addEventListener('DOMContentLoaded', function () {
    window.autocomplete = new Autocomplete({
        search_input_class_name: 'search-input',
        autocomplete_list_class_name: 'autocomplete-list',
        search_form_class_name: 'search-form'
    })
    window.autocomplete.setup()
})