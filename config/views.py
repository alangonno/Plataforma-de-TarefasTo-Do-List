from django.shortcuts import render
from django.http import JsonResponse

def home(request):
    return render(request, 'home.html')

def page_not_found_view(request, exception):
    status_code = 404
    # AJAX request caso 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Not Found'}, status=status_code)
    
    # Pagina template request.
    context = {
        'status_code': status_code,
        'message': 'Page Not Found.',
    }
    response = render(request, 'error.html', context)
    response.status_code = status_code
    return response

def server_error_view(request):
    status_code = 500
    # AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Internal Server Error'}, status=status_code)
        
    # Pagina template request
    context = {
        'status_code': status_code,
        'message': 'Internal Server Error.',
    }
    response = render(request, 'error.html', context)
    response.status_code = status_code
    return response