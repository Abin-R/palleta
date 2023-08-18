from django import forms
from store.models import *

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('image', 'name')
 # Adjust the fields as per your Category model


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Category")
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Product
        fields = ('name', 'image', 'category', 'artist', 'description', 'medium', 'style', 'created_in', 'seller')

class ProductVariantForm(forms.ModelForm):
    size = forms.ModelChoiceField(queryset=Size.objects.all(), label="Size")
    discount_percentage = forms.IntegerField(label="Discount Percentage", required=False)
    price = forms.DecimalField(label="Price")
    is_active = forms.BooleanField(label="Is Active", required=False)
    stock = forms.IntegerField(label="Stock")
    
    class Meta:
        model = ProductVariant
        fields = ('size', 'discount_percentage', 'price', 'is_active', 'stock')
        
class BannerForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Banner
        fields = ('title', 'artist', 'image', 'link', 'start_date', 'end_date', 'active')

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__' 
