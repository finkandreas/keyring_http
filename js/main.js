function htmlEscape(str) {
    return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}

function fill_table(keystore) {
  $('#main_table tbody').empty();
  allElements = []
  $.each(keystore, function(idx, collection) {
    $.each(collection, function(idx, item) {
      allElements.push('<tr>')
      allElements.push('<td><span class="keyring_label">'+htmlEscape(item.label)+'</span></td>');
      allElements.push('<td><span class="password">'+htmlEscape(item.password)+'</span></td>');
      allElements.push('<td><span class="dbus_path">'+htmlEscape(item.dbus_path)+'</span></td>');
      allElements.push('<td>');
      $.each(item.attributes, function(key,val) {
        allElements.push('<div class="key_val"><span class="key">'+htmlEscape(key)+'</span><span class="val">'+htmlEscape(val)+'</span></div>');
      });
      allElements.push('<div class="key_val"><span class="key">new_attrib</span><span class="val"></span></div></td></tr>');
    });
  });
  $('#main_table tbody').html(allElements.join(""));

  // update attributes
  var update_values = function() {
    var el = $(this).replaceWith('<input id="changing_el"></input>');
    $('#changing_el').val(el.text()).attr("size", el.text().length).focus().focusout(function() {
      if (el.text() != this.value) {
        $(this).closest("tr").addClass("changed");
        $('#save_button').show();
      }
      $(this).replaceWith(el.text(this.value).click(update_values));
    });
  };
  $('#main_table .val, #main_table .keyring_label, #main_table .password, #main_table .key').click(update_values);
}


$(function() {
  $.getJSON("cgi-bin/keyring.py", fill_table);
  $('#save_button').hide();

  // save changed elements
  $('#save_button').click(function() {
    var data = [];
    $.each($('tr.changed'), function(idx, el) {
      var dbus_path = $(".dbus_path", el).text();
      var label = $(".keyring_label", el).text();
      var password = $(".password", el).text();
      var attributes = {};
      $.each($('.key_val', el), function(idx, keyVal) {
        var key = $('.key', keyVal).text();
        var val = $('.val', keyVal).text();
        if (key.length > 0 && val.length > 0) attributes[key] = val;
      });
      var data = {"label" : label, "password" : password, "attributes" : attributes, "dbus_path" : dbus_path};
      console.log("Sending data: ", JSON.stringify(data));
      $.post("/cgi-bin/accept_post.py", {'json': JSON.stringify(data)}, function(recvData, textStatus, jqXHR) {
        console.log("Successfully posted data", recvData, jqXHR);
      }, "json");
    });
    $.getJSON("cgi-bin/keyring.py", fill_table);
  });
});
