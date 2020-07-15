window.addEventListener('load', function () {
    let goToLink = function (event) {
        let url = this.getAttribute('href');
        let currentUrl = window.location.href;
        let ref = btoa(currentUrl);
        let goTo = new URL(this.dataset.goto);
        let ad = btoa(this.dataset.ad);
        goTo.searchParams.append('url', url);
        goTo.searchParams.append('ref', ref);
        goTo.searchParams.append('ad', ad);
        this.href = goTo.href;
    };

    let externalLinks = document.querySelectorAll('a.external');
    Array.from(externalLinks).forEach(link => {
        link.addEventListener('mousedown', goToLink);
    });
});

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function findParentByClass(elem, _class) {
    let parent = elem.parentNode;
    while (parent != null) {
        if (hasClass(parent, _class)) {
            return parent
        }
        parent = parent.parentNode;
    }

    return false;
}

function hasClass(element, className) {
    return element.className.indexOf(className) > -1;

}

function addClass(ele,cls) {
  if (!hasClass(ele,cls)) ele.className += " "+cls;
}

function removeClass(ele,cls) {
  if (hasClass(ele,cls)) {
    let reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
    ele.className=ele.className.replace(reg,' ');
  }
}

