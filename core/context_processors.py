def theme(request):
    return {
        'theme': request.session.get('theme', 'light')
    }
