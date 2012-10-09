var showText = 'Показать';
var hideText = 'Скрыть';
var users = [];

var ajax_request = function (url, data, token, callback) {
    var recieved_data;
    $.ajax({
               type:'POST',
               url:url,
               dataType:'json',
               data:{
                   data:JSON.stringify(data),
                   csrfmiddlewaretoken: token
               },
               success: function (data) {
                   recieved_data = data;
                   if (callback) {
                       callback(data);
                   }
               }
           });
    return recieved_data
};


var slugify = function (s, num_chars) {
    s = downcode(s);
    var removelist = [];
    var r = new RegExp('\\b(' + removelist.join('|') + ')\\b', 'gi');
    s = s.replace(r, '');
    // if downcode doesn't hit, the char will be stripped here
    s = s.replace(/[^-\w\s]/g, '');  // remove unneeded chars
    s = s.replace(/^\s+|\s+$/g, ''); // trim leading/trailing spaces
    s = s.replace(/[-\s]+/g, '-');   // convert spaces to hyphens
    s = s.toLowerCase();             // convert to lowercase
    return s.substring(0, num_chars);
};

var populate = function () {
    var uid = $('#id_username').val();
    var emails = '';
    var maildir = '';
    if (uid.length > 1) {
        emails = uid + '@education.tomsk.ru';// + uid + '@rcro.tomsk.ru';
        maildir = '/' + uid + '/Maildir/';
    }
    $('#id_email').val(emails);
    $('#id_mailbox').val(maildir);
};

var set_slug = function () {
    var username_field = $('#id_username');
    username_field.val(slugify($('#id_last_name').val(), 50));
    populate();
};

