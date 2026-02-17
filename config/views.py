from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def error_view(request, exception=None, status_code=500):
    message = ''
    if status_code == 404:
        message = 'Page Not Found.'
    elif status_code == 500:
        message = 'Internal Server Error.'

    context = {
        'status_code': status_code,
        'message': message,
        'exception': exception, # Não passado para o usuario
    }

    response = render(request, 'error.html', context)
    response.status_code = status_code # COnfirme que o status vai estar correto
    return response