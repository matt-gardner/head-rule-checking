$(document).ready(function() {

$('select').change(function() {
  var name = $(this).attr('name');
  var val = $(this).find(':selected').val();
  var link = '/ajax/update/' + name + '/' + val;
  $.get(link, {}, function(html) {});
});

$('.expansion select').change(function() {
  var name = $(this).attr('name');
  var val = $(this).find(':selected').val();
  var link = '/ajax/update/' + name + '/' + val;
  $.get(link, {}, function(html) {});
});

$('.expansion textarea').change(function() {
  var name = $(this).attr('name');
  var val = $(this).val();
  var link = '/ajax/update/' + name + '/' + val;
  $.get(link, {value: val}, function(html) {});
});

});
