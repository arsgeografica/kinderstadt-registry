import datetime
import wtforms.fields
import wtforms.widgets
import registry.widgets


class MultiCheckboxField(wtforms.fields.SelectMultipleField):
    widget = registry.widgets.ButtonGroupWidget()
    option_widget = registry.widgets.ButtonCheckboxInput()


class FlagField(MultiCheckboxField):

    def __init__(self, key, start_date, end_date, *args, **kwargs):
        self.key = key
        self.start_date = start_date
        self.end_date = end_date

        choices = []
        for i in range((end_date - start_date).days):
            day = start_date + datetime.timedelta(days=i)
            choices.append((day.isoformat(), day.strftime('%a')))
        kwargs['choices'] = choices

        return super(FlagField, self).__init__(*args, **kwargs)

    def populate_obj(self, obj, name):
        obj[name] = self.data


class MultiPassportField(MultiCheckboxField):
    def __init__(self, passports, *args, **kwargs):
        self.passports = passports

        kwargs['choices'] = [(passport.pass_id,
                              '%(pass_id)d - %(surname)s %(name)s' % passport.__dict__)
                             for passport in passports]

        return super(MultiPassportField, self).__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [int(pass_id) for pass_id in valuelist]
