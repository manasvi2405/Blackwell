from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView,DeleteView,ListView,UpdateView
from django.urls import reverse_lazy
from django import forms
from django.core.mail import send_mail
from django.contrib.messages.views import SuccessMessageMixin
from .forms import AddressForm,AccountForm,ProfileForm
from .models import Address,Order
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings


# Create your views here.
def dashboard(request):
    return render(request,'dashboard.html',{})

class SignUp(CreateView):
    success_url = reverse_lazy('login')
    template_name = 'register.html'
    class CustomUserCreationFormWithEmail(UserCreationForm):
        email = forms.EmailField(label="Email")
        class Meta(UserCreationForm.Meta):
            fields = UserCreationForm.Meta.fields + ("email",)
    form_class = CustomUserCreationFormWithEmail
    def form_valid(self, form):
        user = form.save()  # Save the user object
        subject = 'Welcome to BlackWell!'
        message = f'Hi {user.username}, welcome to our community!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list =[user.email]
        send_mail(subject, message, from_email, recipient_list,fail_silently=True)
        return super().form_valid(form)
    
class add_address(SuccessMessageMixin,CreateView):
    model=Address
    success_url = reverse_lazy('listaddress')
    template_name = 'address_form.html'
    form_class = AddressForm
    success_message="Address was added successfully"
    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)
    
class update_address(SuccessMessageMixin,UpdateView):
    model=Address
    success_url = reverse_lazy('listaddress')
    template_name = 'address_form.html'
    form_class = AddressForm
    success_message="Address was updated successfully"

class delete_address(SuccessMessageMixin,DeleteView):
    model=Address
    success_url = reverse_lazy('listaddress')
    template_name = 'address_del.html'
    success_message="Address was updated successfully"

class list_address(SuccessMessageMixin,ListView):
    model=Address
    template_name = 'address.html'
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class EditAccount(SuccessMessageMixin,UpdateView):
    form_class = AccountForm
    template_name = 'dashboard.html'
    success_message="Account Updated Successfully" 
    success_url=reverse_lazy('dashboard')
    def get_object(self, queryset=None):
        return self.request.user

class EditProfile(SuccessMessageMixin,UpdateView):
    form_class = ProfileForm
    template_name = 'profile.html'
    success_message = "Profile Updated Successfully"
    success_url=reverse_lazy('editprofile')
    def get_object(self, queryset=None):
        return self.request.user.profile
    
@login_required
def order_history(request):
    data=Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    p = Paginator(data,2)
    page_num=request.GET.get('page')
    orders=p.get_page(page_num)
    return render(request,'order_history.html',{'orders':orders})


@login_required
def track_order(request):
    data = Order.objects.filter(user=request.user)\
        .exclude(status__in=['Delivered', 'Cancelled'])\
        .prefetch_related('items__product')\
        .order_by('-created_at')

    p = Paginator(data, 2)
    page_num = request.GET.get('page')
    orders = p.get_page(page_num)

    return render(request, 'track.html', {'orders': orders})

