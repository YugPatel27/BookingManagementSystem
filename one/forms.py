from one.myapp.models import catagory
import django.forms as forms
from . models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = catagory
        fields = '__all__'
