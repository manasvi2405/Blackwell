from .models import ProductCategory


def productCategory(request):
    return {'categories':ProductCategory.objects.all()}
