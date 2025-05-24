from django.shortcuts import render

def handler403(request, exception=None):
    """Custom 403 (Permission Denied) handler"""
    return render(request, '403.html', status=403)
    
def handler404(request, exception=None):
    """Custom 404 (Not Found) handler"""
    return render(request, '404.html', status=404)
