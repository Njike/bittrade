/*********************************************main-002.js***************************************************/

/**
 * MegaDin v1.0.0 ()
 * Copyright 2017 ThemeBucket
 * Licensed under the ISC license
 */
// import autosize from './js/autosize';
(function ($) {

    'use strict';
    $(function () {

        $('.toggle-btn').on('click', function() {
            $('.ui').toggleClass('ui-aside-compact');
        });

        $('.drop').on('click', function() {
            $('.nav-sub').toggleClass('nav-sub--open');
        });

    });
})(jQuery);