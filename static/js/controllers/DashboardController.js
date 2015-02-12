(function() {
  'use strict';

  angular
      .module('thanku')
      .controller('DashboardController', DashboardController);

  DashboardController.$inject = ['$http', 'ApiService'];

  function DashboardController($http, ApiService) {
    /*jshint validthis: true */
    var vm = this;

    vm.init = function(){
      vm.users = ApiService.getUserList(vm);
    };
  };

})();
