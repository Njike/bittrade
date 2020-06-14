window.onload = function () {
    $('.navbar-toggler-open').on('click', function () {
        $('.navbar-active-overlay').addClass('active')
    })


    $('.navbar-toggler-close').on('click', function () {
        $('.navbar-active-overlay').removeClass('active')
    })
}