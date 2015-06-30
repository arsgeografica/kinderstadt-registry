from flask import render_template
import wtforms.widgets


class ButtonGroupWidget(object):

    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol', 'ul')
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return render_template('form/button_group.html', field=field,
                               params=wtforms.widgets.html_params(**kwargs),
                               **kwargs)


class ButtonCheckboxInput(wtforms.widgets.Input):
    input_type = 'checkbox'

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
            kwargs['checked'] = True
        kwargs.setdefault('id', field.id)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        params = wtforms.widgets.html_params(name=field.name, **kwargs)
        return render_template('form/button_checkbox.html', field=field,
                               params=params, **kwargs)
