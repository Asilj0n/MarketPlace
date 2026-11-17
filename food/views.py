from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Item
from django.template import loader
from .forms import ItemForm

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# def index(request):
#     item_list = Item.objects.all()
#     context = {
#         'item_list':item_list
#     }
#     return render(request, 'food/index.html', context)

# Class based view
class IndexClassView(ListView):
    model = Item;
    template_name = 'food/index.html'
    context_object_name = 'item_list'


def item(request):
    return HttpResponse('<h1>Items here</h1>')

# def detail(request, item_id):
#     item = Item.objects.get(pk=item_id)
#     context = {
#         'item':item,
#     }
    # return render(request, 'food/detail.html',context )
# Class based detail view

class FoodDetail(DetailView):
    model = Item
    template_name = 'food/detail.html'
    

# def create_item(request):
#     form = ItemForm(request.POST or None)

#     if form.is_valid():
#         form.save()
#         return redirect('food:index')
#     return render(request, 'food/item-form.html', context={'form':form})

# class based create view
class FoodCreate(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'food/item-form.html'
    fields = ['item_name', 'item_desc', 'item_price', 'item_image']
    # success_url = reverse_lazy('food:index')
    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)


def update_item(request, id):
    item = Item.objects.get(id=id)
    form = ItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('food:index')
    return render(request, 'food/item-form.html', context={'form':form, 'item':item})


def delete_item(request, id):
    item = Item.objects.get(id=id)
    if request.method == "POST":
        item.delete()
        return redirect('food:index')
    return render(request, "food/item-delete.html", context={'item':item})

