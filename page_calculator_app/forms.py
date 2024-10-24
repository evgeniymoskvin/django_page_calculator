from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    Форма для отправки нескольких файлов одновременно
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class UploadFileForm(forms.Form):
    """
    Форма для отправки на главной странице
    """
    file = MultipleFileField(label="Выберите или переместите файлы в это окно",
                             widget=MultipleFileInput(attrs={'class': 'd-flex, input_my_form',
                                                             'multiple': 'True'
                                                             }))
# class UploadFileForm(forms.Form):
#     file = forms.FileField(label="Выберете файл", widget=forms.FileInput(attrs={'class': 'd-flex, input_my_form',
#                                                                                 }))
