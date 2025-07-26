from django import forms

class IDCardForm(forms.Form):
    id_card_image = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png'})
    )
    
    def clean_id_card_image(self):
        image = self.cleaned_data.get('id_card_image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Maksimum dosya boyutu 5MB olmalı.')
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError('Sadece .jpg, .jpeg veya .png dosyaları kabul edilir.')
        return image 