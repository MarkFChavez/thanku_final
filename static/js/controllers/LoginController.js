(function() {
    'use strict';

    angular
        .module('thanku')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', 'ApiService'];

    function LoginController($location, ApiService) {
        /*jshint validthis: true */
        var vm = this;

        vm.login = function login() {
            ApiService.login(vm);
        };
    }
})();
