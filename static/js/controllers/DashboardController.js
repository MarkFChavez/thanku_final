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
      if( vm.reason.toString().trim() != "" ) {
        ApiService.applyVote(vm, points, id);
      } else {
        alert("You must specify a reason why you are thanking this human being!");
      }
    };

    vm.getMomentTime = function(timestamp) {
      return (moment(timestamp).fromNow());
    };
  };

})();
