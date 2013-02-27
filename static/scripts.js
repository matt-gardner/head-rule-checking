if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

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
  var $area = $(this);
  var name = $(this).attr('name');
  var val = '"'+$(this).val()+'"';
  var link = '/ajax/update/' + name + '/' + val;
  if (name.endsWith("comment")) {
    $.get(link, {value: val}, function(html) {
      $area.attr(html);
    });
  } else {
    $.get(link, {value: val}, function(html) {});
  }
});

});
