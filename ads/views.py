from encodings.base64_codec import base64_decode

from actstream import action
from categories.models import Category
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

from django_filters.views import FilterView
from haystack.views import SearchView
from lazysignup.decorators import allow_lazy_user

from ads.actions import ACTION_FOLLOW_EXTERNAL_AD, ACTION_VIEW_AD
from ads.forms.adform import AdForm
from ads.forms.adimageform import AdImageForm
from ads.models.ad import Ad
from ads.models.adimages import AdImage


class IndexView(SearchView):
    template = 'ad/index.html'

    def get_context(self):
        context = super().get_context()
        parent_categories = Category.objects.filter(parent=None).all()
        context['parent_categories'] = parent_categories
        return context


class AdsByMainCategoryView(FilterView):
    paginate_by = 20
    model = Ad
    template_name = 'ad/ads.html'
    filterset_fields = '__all__'
    category: Category

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.category = get_object_or_404(Category, slug=self.kwargs['category'], parent=None)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = self.category

        return context

    @method_decorator(allow_lazy_user)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AdsByCategoriesView(FilterView):
    paginate_by = 20
    model = Ad
    template_name = 'ad/ads.html'
    filterset_fields = '__all__'
    category: Category
    subcategory: Category

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.category = get_object_or_404(Category, slug=self.kwargs['category'])
        try:
            self.subcategory = Category.objects.filter(slug=self.kwargs['subcategory'], parent=self.category.id).get()
        except Category.DoesNotExist:
            raise Http404('No categories matches the given query.')

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        return queryset.filter(category=self.subcategory.id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = self.category
        context['subcategory'] = self.subcategory

        return context

    @method_decorator(allow_lazy_user)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@allow_lazy_user
def detail(request, ad_slug):
    ad = get_object_or_404(Ad, slug=ad_slug)
    action.send(request.user, verb=ACTION_VIEW_AD, target=ad)
    return render(request, 'ad/detail.html', {'ad': ad})


@allow_lazy_user
def create(request):

    image_form_set = modelformset_factory(AdImage, form=AdImageForm, extra=3)

    if request.method == 'POST':
        ad_form = AdForm(request.POST)
        ad_image_formset = image_form_set(
            request.POST,
            request.FILES,
            queryset=AdImage.objects.none()
        )

        if ad_form.is_valid() and ad_image_formset.is_valid():
            ad = ad_form.save()
            for form in ad_image_formset.cleaned_data:
                if 'image' in form:
                    image = form['image']
                    ad_image = AdImage(ad=ad, image=image)
                    ad_image.save()

            return HttpResponseRedirect('/')
    else:
        ad_form = AdForm()
        ad_image_formset = image_form_set(queryset=AdImage.objects.none())
    return render(request, 'ad/create.html', {'ad_form': ad_form, 'ad_image_formset': ad_image_formset})


@allow_lazy_user
def to_external_url(request):
    url = request.GET.get('url')
    ref = request.GET.get('ref')
    request_ad = request.GET.get('ad')
    try:
        from_url = base64_decode(bytes(ref, 'utf-8'))[0].decode('utf-8')
        ad_id = base64_decode(bytes(request_ad, 'utf-8'))[0].decode('utf-8')
        ad = Ad.objects.get(id=ad_id)
    except:
        from_url = None
        ad = None
    if not url or not from_url or not from_url.startswith(request.build_absolute_uri('/')) or not ad:
        return HttpResponseBadRequest()
    response = HttpResponseRedirect(url)
    response['Referer'] = from_url
    action.send(request.user, verb=ACTION_FOLLOW_EXTERNAL_AD, target=ad)
    return response
