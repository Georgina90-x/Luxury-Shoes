from django.shortcuts import render


def view_bag(request):
    """
    A view to return the index page (home)
    """
    return render(request, 'bag/bag.html')
