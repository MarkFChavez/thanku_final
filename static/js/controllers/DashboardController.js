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

    setInterval(function(){ ApiService.getNewsFeed(vm); }, 2000);
    vm.vote = function(points,id) {
      ApiService.applyVote(vm, points, id);
    };

    vm.getMomentTime = function(timestamp) {
      return (moment(timestamp).fromNow());
    };
  };

})();
