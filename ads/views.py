from categories.models import Category
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from django.views.generic import ListView
from django_filters.views import FilterView
from haystack.views import SearchView

from ads.forms.adform import AdForm
from ads.forms.adimageform import AdImageForm
from ads.models.ad import Ad
from ads.models.adimages import AdImage


class index(SearchView):
    template = 'ad/index.html'

    def get_context(self):
        context =  super().get_context()
        parent_categories = Category.objects.filter(parent=None).all()
        context['parent_categories'] = parent_categories
        return context


class ads_by_main_category(FilterView):
    paginate_by = 20
    model = Ad
    template_name = 'ad/ads.html'
    filterset_fields = '__all__'

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

class ads_by_categories(ListView):
    paginate_by = 20
    model = Ad
    template_name = 'ad/ads.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.category = get_object_or_404(Category, slug=self.kwargs['category'])
        try:
            self.subcategory = Category.objects.filter(slug=self.kwargs['subcategory'], parent=self.category.id).get()
        except Category.DoesNotExist:
            raise Http404('No categories matches the given query.')

    def get_queryset(self):
        queryset =  super().get_queryset().order_by('-created_at')
        return queryset.filter(category=self.subcategory.id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = self.category
        context['subcategory'] = self.subcategory

        return context


def detail(request, ad_slug):
    ad = get_object_or_404(Ad, slug=ad_slug)
    return render(request, 'ad/detail.html', {'ad': ad})


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
    return render(request, 'ad/create.html', {'ad_form':ad_form, 'ad_image_formset': ad_image_formset})
