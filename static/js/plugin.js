$(function(){
  $(window).load(function() {
    $("#cards").imagesLoaded(function() {
      $("#cards").masonry({
        columnWidth: 70,
        itemSelector: ".card",
        isOriginLeft: true
      });
    });
  });
  $(".modal-trigger").leanModal();
})
