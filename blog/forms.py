from blog.models import Article

from django import forms


class ArticleForm(forms.ModelForm):
    '''
    Форма статьи блога
    '''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Изображение будет сжато до 1200x800'

    class Meta:
        model = Article
        exclude = ('view_count', 'published_data',)
        widgets = {
            'image': forms.FileInput(attrs={'help_text': 'Загрузите изображение для статьи'})
        }
