require('./registry.js');
var Selectize = require('selectize');
var $ = require('jquery'),
    pass_id_regex = /^\d+$/;


Selectize.define('enter_key_submit', function (options) {
    var self = this;

    this.onKeyDown = (function (e) {
        var original = self.onKeyDown;

        return function(e) {
            // this.items.length MIGHT change after event propagation.
            // We need the initial value as well. See next comment.
            var initialSelection = this.items.length;
            original.apply(this, arguments);
            // Necessary because we don't want this to be triggered when an
            // option is selected with Enter after pressing DOWN key to trigger
            // the dropdown options
            if (e.keyCode === 13 && initialSelection &&
                initialSelection === this.items.length &&
                this.$control_input.val() === '') {
                self.trigger('submit');
            }
        };
    })();
  });


var input = $('.pass-id input').removeClass('form-control');
input.selectize({
    valueField: 'pass_id',
    labelField: 'pass_id',
    searchField: 'full_name',
    create: true,
    createFilter: pass_id_regex,
    maxItems: 1,
    mode: 'multi',
    closeAfterSelect: true,
    plugins: ['enter_key_submit'],
    onInitialize: function () {
        this.on('submit', function () {
            this.$input.closest('form').submit();
        }, this);
        this.$control_input.click().focus();
    },
    load: function load(query, callback) {
        if(!query.length) {
            return callback();
        }

        if(pass_id_regex.test(query)) {
            return callback();
        }

        $.ajax({
            url: '/passport/query',
            type: 'POST',
            data: JSON.stringify({
                query: query
            }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            error: function() {
                callback();
            },
            success: function(response) {
                callback(response.data);
            }
        });
    },
    render: {
        option: function render_option(item, escape) {
            return '<div><span class="pass-id label ' + (item.checked_in ? 'label-success' : 'label-danger') + '">' + item.pass_id + '</span> ' + item.full_name + '</div>';
        },
        option_create: function(data, escape) {
            return '<div class="create"><strong>' + escape(data.input) + '</strong> auswählen…</div>';
        }
    }
});
