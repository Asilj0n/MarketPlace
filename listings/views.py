from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from users.models import Campus

from .forms import ListingForm
from .models import Listing


class ListingListView(LoginRequiredMixin, ListView):
    """Browse listings, with search and filters taken from the query string."""
    template_name = 'listings/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12

    def get_queryset(self):
        params = self.request.GET
        listings = Listing.objects.select_related('seller')

        query = params.get('q', '').strip()
        if query:
            listings = listings.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if params.get('category') in Listing.Category.values:
            listings = listings.filter(category=params['category'])
        if params.get('campus') in Campus.values:
            listings = listings.filter(campus=params['campus'])
        if params.get('free'):
            listings = listings.filter(price=0)
        if not params.get('show_sold'):
            listings = listings.exclude(status=Listing.Status.SOLD)
        return listings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        querystring = self.request.GET.copy()
        querystring.pop('page', None)
        context.update({
            'categories': Listing.Category.choices,
            'campuses': Campus.choices,
            'filters': self.request.GET,
            # Keeps the current filters when moving between pages.
            'querystring': querystring.urlencode(),
        })
        return context


class ListingDetailView(LoginRequiredMixin, DetailView):
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'listing'

    def get_queryset(self):
        return Listing.objects.select_related('seller__profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = self.object
        context.update({
            'is_owner': listing.seller == self.request.user,
            'whatsapp_url': listing.whatsapp_url(self.request),
            'statuses': Listing.Status.choices,
        })
        return context


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Buyers contact sellers on WhatsApp, so a seller must have a number first.
        if request.user.is_authenticated and not request.user.profile.whatsapp_number:
            messages.warning(request, 'Add your WhatsApp number before posting, so buyers can contact you.')
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'campus': self.request.user.profile.campus}

    def form_valid(self, form):
        form.instance.seller = self.request.user
        messages.success(self.request, 'Your listing is live!')
        return super().form_valid(form)


class SellerListingMixin(LoginRequiredMixin):
    """Only the seller can edit or delete a listing; anyone else gets a 404."""

    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)


class ListingUpdateView(SellerListingMixin, UpdateView):
    form_class = ListingForm
    template_name = 'listings/listing_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Listing updated.')
        return super().form_valid(form)


class ListingDeleteView(SellerListingMixin, DeleteView):
    template_name = 'listings/listing_confirm_delete.html'
    context_object_name = 'listing'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, f'"{self.object.title}" was deleted.')
        return super().form_valid(form)


@login_required
@require_POST
def update_status(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    status = request.POST.get('status')
    if status in Listing.Status.values:
        listing.status = status
        listing.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Marked as {listing.get_status_display().lower()}.')
    return redirect(listing)
