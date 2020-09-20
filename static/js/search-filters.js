let SearchFilterManager = function (options) {
    this.dropdown_button_id = options.dropdown_button_id;
    this.filters_container_id = options.filters_container_id;
    this.dropdown_filters_icon_id = options.dropdown_filters_icon_id;
    this.provinces_filter_id = options.provinces_filter_id;
    this.provinces_selected_container_id = options.provinces_selected_container_id;
    this.prices_filter_id = options.prices_filter_id;
    this.prices_selected_container_id = options.prices_selected_container_id;
};

SearchFilterManager.prototype.setup = function () {
    let self = this;
    this.dropdown_button = document.getElementById(this.dropdown_button_id);
    this.filters_container = document.getElementById(this.filters_container_id);
    this.dropdown_filters_icon = document.getElementById(this.dropdown_filters_icon_id);
    this.provinces_selected_container = document.getElementById(this.provinces_selected_container_id);
    this.prices_filter = document.getElementById(this.prices_filter_id);
    this.prices_selected_container = document.getElementById(this.prices_selected_container_id);

    this.dropdown_button.addEventListener("click", function (event) {
        if (self.areFiltersShown()) {
            self.hideFilters();
            removeClass(self.dropdown_filters_icon, "icon-down-open-big");
            addClass(self.dropdown_filters_icon, "icon-right-open-big");
        } else {
            self.showFilters();
            removeClass(self.dropdown_filters_icon, "icon-right-open-big");
            addClass(self.dropdown_filters_icon, "icon-down-open-big");
        }
    });

    let provinces_select_btns = document.querySelectorAll(`#${this.provinces_filter_id} .custom-select button`);
    provinces_select_btns.forEach(button => button.addEventListener('click', function () {
        let selected = parseInt(this.getAttribute('data-selected'));
        let value = this.getAttribute('data-value');
        if (selected) {
            self.removeProvinceSelection(value);
        } else {
            self.addProvinceSelection(value);
        }
    }));

    let provinces_remove_selection_btns = document.querySelectorAll(`#${this.provinces_selected_container_id} button.remove-filter`);
    provinces_remove_selection_btns.forEach(button => button.addEventListener('click', function () {
        self.removeProvinceSelection(this.getAttribute('data-reference'));
    }));

    let from_price_input = document.querySelector(`#${this.prices_filter_id} input[name="price_from"]`);
    from_price_input.addEventListener('input', function () {
        if (this.value)
            self.setPriceSelection(this.getAttribute('name'));
        else
            self.removePriceSelection(this.getAttribute('name'));
    });

    let to_price_input = document.querySelector(`#${this.prices_filter_id} input[name="price_to"]`);
    to_price_input.addEventListener('input', function () {
        if (this.value)
            self.setPriceSelection(this.getAttribute('name'));
        else
            self.removePriceSelection(this.getAttribute('name'));
    });

    let price_currency_select = document.querySelector(`#${this.prices_filter_id} select[name="price_currency"]`);
    price_currency_select.addEventListener('change', function () {
        let input_event = new Event('input');
        if (from_price_input.value)
            from_price_input.dispatchEvent(input_event);
        if (to_price_input.value)
            to_price_input.dispatchEvent(input_event);
    });
};

SearchFilterManager.prototype.removePriceSelection = function (name) {
    let displayed_price_element_remove_button = document.querySelector(`#${this.prices_selected_container_id} button[data-reference="${name}"]`);
    displayed_price_element_remove_button.parentElement.parentElement.remove();
    let input = document.querySelector(`#${this.prices_filter_id} input[name="${name}"]`);
    input.value = '';
};

SearchFilterManager.prototype.setPriceSelection = function (name) {
    let input = document.querySelector(`#${this.prices_filter_id} input[name="${name}"]`);
    let currency_input = document.querySelector(`#${this.prices_filter_id} select[name="price_currency"]`);
    let display_text = `${input.getAttribute('placeholder')}: ${input.value} ${currency_input.value}`;

    let displayed_price_element_remove_button = document.querySelector(`#${this.prices_selected_container_id} button[data-reference="${name}"]`);
    if (displayed_price_element_remove_button)
        displayed_price_element_remove_button.parentElement.parentElement.remove();

    let display_price_element = this.getDisplayedSelectionElement(name, display_text, 'window.search_filter_manager.removePriceSelection');

    if (name === 'price_from')
        this.prices_selected_container.prepend(display_price_element);
    else
        this.prices_selected_container.append(display_price_element);
}
;

SearchFilterManager.prototype.removeProvinceSelection = function (value) {
    let option = document.querySelector(`#${this.provinces_filter_id} select[name="provinces"] option[value="${value}"]`);
    let select_btn = document.querySelector(`#${this.provinces_filter_id} .custom-select button[data-value="${value}"]`);
    let displayed_selection = document
        .querySelector(`#${this.provinces_selected_container_id} .item-container .item button[data-reference="${value}"]`)
        .parentElement
        .parentElement;
    option.removeAttribute('selected');
    select_btn.setAttribute('data-selected', 0);
    displayed_selection.remove();
};

SearchFilterManager.prototype.addProvinceSelection = function (value) {
    let option = document.querySelector(`#${this.provinces_filter_id} select[name="provinces"] option[value="${value}"]`);
    let select_btn = document.querySelector(`#${this.provinces_filter_id} .custom-select button[data-value="${value}"]`);
    option.setAttribute('selected', '');
    select_btn.setAttribute('data-selected', 1);
    let displayed_selection = this.getDisplayedSelectionElement(value, select_btn.textContent, 'window.search_filter_manager.removeProvinceSelection');
    this.provinces_selected_container.appendChild(displayed_selection);
};

SearchFilterManager.prototype.getDisplayedSelectionElement = function (source_reference, display_text, on_remove_callback_name) {
    let html = `<div class="item-container column column-xs-100 column-sm-50">
                    <div class="item">
                        <button type="button" class="remove-filter button button-sm button-clear" data-reference="${source_reference}"
                        onclick="${on_remove_callback_name}(this.getAttribute('data-reference'))">
                            <span class="icon-cancel-1"></span></button>
                                ${display_text}
                    </div>
                </div>`;

    let temp_elem = document.createElement('div');
    temp_elem.innerHTML = html.trim();

    return temp_elem.firstChild;
};

SearchFilterManager.prototype.showFilters = function () {
    removeClass(this.filters_container, 'd-none');
};

SearchFilterManager.prototype.hideFilters = function () {
    addClass(this.filters_container, 'd-none');
};

SearchFilterManager.prototype.areFiltersShown = function () {
    return !hasClass(this.filters_container, 'd-none');
};

function load_filter_manager() {
    window.search_filter_manager = new SearchFilterManager({
        dropdown_button_id: "dropdown-filters-btn",
        filters_container_id: "filters-container",
        dropdown_filters_icon_id: "dropdown-filters-icon",
        provinces_filter_id: "provinces-filter",
        provinces_selected_container_id: "provinces-selected",
        prices_filter_id: "prices-filter",
        prices_selected_container_id: "prices-selected"
    });
    window.search_filter_manager.setup();
}


if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load_filter_manager); // Document still loading so DomContentLoaded can still fire :)
} else {
    load_filter_manager();
}