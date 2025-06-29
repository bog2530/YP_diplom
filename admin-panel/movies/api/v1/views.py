from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ["get"]

    def get_queryset(self):
        return FilmWork.objects

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

    def serialize_filmwork(self, filmwork):
        return {
            "id": filmwork["id"],
            "title": filmwork["title"],
            "description": filmwork["description"],
            "creation_date": filmwork["creation_date"],
            "rating": filmwork.get("rating", 0),
            "type": filmwork["type"],
            "genres": filmwork.get("genre_names", []),
            "actors": filmwork.get("actors", []),
            "directors": filmwork.get("directors", []),
            "writers": filmwork.get("writers", []),
        }


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = (
            self.get_queryset()
            .prefetch_related("genres", "persons")
            .annotate(
                genre_names=ArrayAgg("genres__name", distinct=True),
                actors=ArrayAgg("persons__full_name", filter=Q(personfilmwork__role="actor"), distinct=True),
                directors=ArrayAgg("persons__full_name", filter=Q(personfilmwork__role="director"), distinct=True),
                writers=ArrayAgg("persons__full_name", filter=Q(personfilmwork__role="writer"), distinct=True),
            )
            .values()
        )

        paginator, page, queryset, _ = self.paginate_queryset(queryset, self.paginate_by)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "next": page.next_page_number() if page.has_next() else None,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "results": [self.serialize_filmwork(filmwork) for filmwork in queryset],
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_object(self, queryset=None):
        queryset = self.get_queryset().select_related()
        return super().get_object(queryset=queryset)

    def get_context_data(self, **kwargs):
        filmwork = kwargs.get("object")
        return self.serialize_filmwork(filmwork) if filmwork else None
