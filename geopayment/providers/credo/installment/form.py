__all__ = ('InstallmentForm',)


class InstallmentForm(object):
    form_fields = None

    def __init__(self, data=None):
        self.value = data

        if self.form_fields and not isinstance(self.form_fields, list):
            raise ValueError('InvalidValue, form_fields must be list.')

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        form = list()
        for field in self.form_fields or list():
            form.append(field)

        form.append(self.input)
        return ''.join(form)

    @property
    def action(self):
        """
        Credo Installment Url
        """
        return 'https://ganvadeba.credo.ge/widget/index.php'

    @property
    def input(self):
        return f'<input type="hidden" name="credoinstallment" value="{self.value}">'
