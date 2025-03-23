from django.shortcuts import render, redirect


def view_bag(request):
    """
    A view to return the index page (home)
    """
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """"
    A view to add products to the bag as well as a quantity
    """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    shoesize = None
    if 'product_size' in request.POST:
        shoesize = request.POST['product_size']
    bag = request.session.get('bag', {})

    if shoesize:
        if item_id in list(bag.keys()):
            if shoesize in bag[item_id]['items_by_shoesize'].keys():
                bag[item_id]['items_by_shoesize'][shoesize] += quantity
            else:
                bag[item_id]['items_by_shoesize'][shoesize] = quantity
        else:
            bag[item_id] = {'items_by_shoesize': {shoesize: quantity}}
    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)
