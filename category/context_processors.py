#Will take request as an arguments and will return the dictionary of data as a context :- Use of context processors in django
from .models import Category
def links(request):
    links =  Category.objects.all()
    return dict(links = links)
