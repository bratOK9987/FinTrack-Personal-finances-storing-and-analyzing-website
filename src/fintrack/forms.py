from django import forms
from .models import FinancialRecord, Tag

class FinancialRecordForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Comma-separated tags (e.g. groceries, rent, travel)"
    )

    class Meta:
        model = FinancialRecord
        fields = ['description', 'record_type', 'amount', 'date']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            tag_input = self.cleaned_data.get('tags', '')
            tag_names = [name.strip().lower() for name in tag_input.split(',') if name.strip()]

            instance.tags.clear()   # не используеться, на будущее для удаления 

            for name in tag_names:  # создает и назначает теги
                tag, created = Tag.objects.get_or_create(name=name)
                instance.tags.add(tag)

        return instance
