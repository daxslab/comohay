import logging
import re
import sys
import time
from encodings.base64_codec import base64_decode

from fast_autocomplete import autocomplete_factory
from actstream import action
from categories.models import Category
from django.contrib.auth.decorators import login_required
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator

from django_filters.views import FilterView
from fast_autocomplete.loader import populate_redis
from haystack.views import SearchView
from lazysignup.decorators import allow_lazy_user
from meta.views import Meta
from rest_framework.utils import json
from text_unidecode import unidecode

from ads.actions import ACTION_FOLLOW_EXTERNAL_AD, ACTION_VIEW_AD, ACTION_SEARCH_AD
from ads.filters.ad_filter import AdFilter
from ads.forms.adform import AdForm
from ads.forms.adimageform import AdImageForm
from ads.forms.adsearchform import AdSearchForm
from ads.helpers.telegrambot import TelegramBot
from ads.models import UserSearch, Search
from ads.models.ad import Ad
from ads.models.adimages import AdImage
from comohay import settings

logger = logging.getLogger(__name__)


class IndexView(SearchView):
    template = 'ad/index.html'

    def __init__(self, template=None, load_all=True, form_class=None, searchqueryset=None, results_per_page=None):
        super().__init__(template, load_all, form_class, searchqueryset, results_per_page)
        if form_class is None:
            self.form_class = AdSearchForm

    def __call__(self, request):
        cache = caches['search']
        path = request.get_full_path()

        self.request = request
        self.form = self.build_form()
        self.query = self.get_query()
        self.results = self.get_results()

        response = cache.get(path)
        if not response:
            response = self.create_response()
            cache.set(path, response, settings.CACHE_SEARCH_RESPONSE_SECONDS)
        if self.query != '' and not self.request.GET.get('page', False):
            user_search = UserSearch(user=request.user, search=self.query,
                                     autosuggestion=bool(request.GET.get('a', False)))
            user_search.save()
            action.send(request.user, verb=ACTION_SEARCH_AD, target=user_search)
        return response

    def get_context(self):
        context = super().get_context()
        result_count = self.results.count()
        context['index_count'] = result_count if result_count > 0 else Ad.objects.count()

        query_split = self.query.split(' ')

        def find_missing_terms(search_result):
            missing_terms = []
            for term in query_split:
                if not re.search(re.escape(unidecode(term)), unidecode(search_result.text), re.IGNORECASE):
                    missing_terms.append(term)

            search_result.__dict__['missing_terms'] = missing_terms
            return search_result

        context['page'].object_list = map(find_missing_terms, context['page'].object_list)

        meta = Meta(
            keywords=['indexado de clasificados en cuba', 'búsqueda de clasificados en cuba',
                      'cuba indexado de clasificados', 'cuba búsqueda de clasificados',
                      'indexado de anuncios en cuba', 'búsqueda de anuncios en cuba',
                      'cuba indexado de anuncios', 'cuba búsqueda de anuncios'
                      ],
            image=settings.STATIC_URL + 'logo-vertical-adjusted.png',
            image_width=600,
            image_height=600,
            url=self.request.get_full_path(),
            title=settings.META_SITE_NAME,
            description='La manera más eficiente de buscar clasificados en Cuba, rápido y ligero. Indexamos constantemente los sitos más populares de anuncios en nuestro país.',
        )

        if self.query != '':
            meta.title = '{} - {}'.format(self.query, settings.META_SITE_NAME)
            meta.description = "Consulta los resultados para \"{}\" que hemos encontrado. Indexamos constantemente los sitios cubanos de anuncios más populares para ofrecerte los mejores resultados.".format(
                self.query)

        context['meta'] = meta
        return context


def autocomplete(request):
    query = request.GET.get('q', '')

    suggestions = settings.autocomplete.search(query, max_cost=3, size=7)

    for pos in range(len(suggestions)):
        if type(suggestions[pos]) != str:
            suggestions[pos] = ' '.join(suggestions[pos])

    the_data = json.dumps({
        'results': suggestions
    })

    return HttpResponse(the_data, content_type='application/json')


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
# @csrf_exempt
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

            try:
                TelegramBot.broadcast_ad(ad, request)
            except Exception as e:
                logger.error('Error broadcasting AD: ' + str(e))

            if request.user.is_authenticated:
                return HttpResponseRedirect('/my_ads')
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


@login_required
def user_ads(request):
    filter = AdFilter(request.GET, queryset=Ad.objects.filter(created_by=request.user))
    return render(request, 'ad/user_ads.html', {"filter": filter})


@login_required
def edit(request, id):
    ad = get_object_or_404(Ad, id=id)
    ad.price = ad.get_user_price()

    if request.user.id != ad.created_by_id:
        raise ValidationError(u'Permission denied')

    extra = 3 - ad.adimage_set.count()
    image_form_set = inlineformset_factory(Ad, AdImage, form=AdImageForm, extra=extra)

    if request.method == 'POST':
        ad_form = AdForm(request.POST, instance=ad)
        ad_image_formset = image_form_set(
            request.POST,
            request.FILES,
            instance=ad
        )

        if ad_form.is_valid() and ad_image_formset.is_valid():
            ad = ad_form.save()
            ad_image_formset.save()

            if request.user.is_authenticated:
                return HttpResponseRedirect('/my_ads')
            return HttpResponseRedirect('/')
    else:
        ad_form = AdForm(instance=ad)
        ad_image_formset = image_form_set(instance=ad)
    return render(request, 'ad/edit.html', {'ad_form': ad_form, 'ad_image_formset': ad_image_formset})


@login_required
def delete(request, id):
    ad = get_object_or_404(Ad, id=id)

    if request.user.id != ad.created_by_id:
        raise ValidationError(u'Permission denied')

    for ad_image in ad.adimage_set.all():
        ad_image.delete()

    ad.delete()

    return JsonResponse({'success': True})
