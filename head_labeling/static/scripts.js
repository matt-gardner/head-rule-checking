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

$('.delete-annotation').click(function() {
  var $this = $(this);
  var id = $this.attr('id');
  var link = '/ajax/delete/'+id;
  if (confirm("Delete this annotation?")) {
    $.get(link, {}, function(html) {
      $this.parent().parent().remove();
    });
  }
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

$('.examples').hide();
$('.intermediate-examples').hide();

$('.show-examples span').click(function() {
  $(this).parent().parent().children('.examples').toggle();
});
$('.show-debug span').click(function() {
  $(this).parent().parent().children('.intermediate-examples').toggle();
});

});
