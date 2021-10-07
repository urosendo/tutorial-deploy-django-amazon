from django.shortcuts import render

# Create your views here.
def index(request):
    template_name = 'core/index.html'
    message = 'Aplicação Django no ar utilizando uWSGI + NGinx'
    return render(request, template_name, {'message':message})