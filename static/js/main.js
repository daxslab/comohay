window.addEventListener('load', function () {
    let goToLink = function(event){
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