var GUI = GUI || {};

function htmlEscape(str) {
    return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}


function update_values() {
  var el = $(this);
  var input = $('#change_input').show().offset(el.offset());
  input.val(el.text()).attr("size", Math.max(10, el.text().length)).select().one("focusout", function() {
    if (el.text() != this.value) {
      el.closest("tr").addClass("changed");
      $('#save_button').show();
    }
    el.text(this.value);
    input.hide();
  });
};


function fill_table(keystore) {
  $('#main_table tbody').empty();
  allElements = []
  GUI.keystore = keystore;
  $.each(keystore, function(idx, collection) {
    collection.sort(function(a,b) { return a.label > b.label; });
    $.each(collection, function(idx, item) {
      allElements.push('<tr>')
      allElements.push('<td><span class="keyring_label">'+htmlEscape(item.label)+'</span></td>');
      allElements.push('<td><span class="password">'+htmlEscape(item.password)+'</span></td>');
      allElements.push('<td><span class="dbus_path">'+htmlEscape(item.dbus_path)+'</span></td>');
      allElements.push('<td class="key_val_cell">');
      sorted_keys = Object.keys(item.attributes).sort();
      $.each(sorted_keys, function(idx,key) {
        val = item.attributes[key];
        allElements.push('<div class="key_val"><span class="key">'+htmlEscape(key)+'</span><span class="val">'+htmlEscape(val)+'</span></div>');
      });
      allElements.push('</td></tr>');
    });
  });
  $('#main_table tbody').html(allElements.join(""));

  $('#main_table .val, #main_table .keyring_label, #main_table .password, #main_table .key').click(update_values);

  // track mousenter on table rows for deletion
  $('#main_table tr').mouseenter(function() {
    var tr = $(this);
    var trPos = tr.offset();
    trPos.left += tr.width();
    GUI.ItemToDelete = $('.dbus_path', tr).text();
    GUI.CurRow = tr;
    $('#del_button').show().offset(trPos);
    $('#add_attrib_button').show();
    trPos.left -= $('#add_attrib_button').outerWidth();
    trPos.top += tr.height()-$('#add_attrib_button').outerHeight();
    $('#add_attrib_button').offset(trPos);
  });

  $('#save_button, #change_input, #del_button, #add_attrib_button').hide();
}


function save_changes() {
  var data = [];
  var postCount = 0;
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
    postCount++;
    $.post("/cgi-bin/update_item.py", {"json": JSON.stringify(data)}, function(recvData, textStatus) {
      if (--postCount == 0) $.getJSON("cgi-bin/keyring.py", fill_table);
    }, "json");
  });
};


function add_entry() {
  $('#add_entry_modal').modal('show');
  var availableCollections = Object.keys(GUI.keystore);
  $('#collection_chooser').empty();
  $.each(availableCollections, function(idx, collection) {
    $('#collection_chooser').append('<label><input type="radio" name="optionsCollection" value="'+idx+'"> '+collection+'</label>')
  })
  $('#collection_chooser input:first').prop("checked", "true")
  $('#add_entry_modal button.btn-primary').one('click', function() {
    var data = { "collection": availableCollections[$('#collection_chooser input:checked').val()], "label": $('#entry_label').val(), "password": $('#entry_password').val() };
    $.post("/cgi-bin/add_item.py", {"json": JSON.stringify(data)}, function(recvData, textStatus) {
      $.getJSON("cgi-bin/keyring.py", fill_table);
    });
    $('#add_entry_modal').modal('hide');
  });
};


function del_entry() {
  $.post("/cgi-bin/del_item.py", {"json": JSON.stringify({'dbus_path': GUI.ItemToDelete})}, function(recvData, textStatus) {
    $.getJSON("cgi-bin/keyring.py", fill_table);
  });
}


function add_attrib() {
  var keyValPair = $('<div class="key_val"><span class="key">new_key</span><span class="val">new_value</span></div>');
  $('.key, .val', keyValPair).click(update_values);
  $('.key_val_cell', GUI.CurRow).append(keyValPair);
  GUI.CurRow.addClass('changed');
}


$(function() {
  $.getJSON("cgi-bin/keyring.py", fill_table);
  $('#save_button').click(save_changes);
  $('#add_button').click(add_entry);
  $('#del_button').click(del_entry);
  $('#add_attrib_button').click(add_attrib);
});
