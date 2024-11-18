import json

from django.shortcuts import render, redirect
from django.views import View

from django.db.models import Q

from customer.models import MenuItem, Category, OrderModel

from django.core.mail import send_mail

# Create your views here.
class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/pizza-gh-pages/index.html')

class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/pizza-gh-pages/about.html')

class Menu(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/pizza-gh-pages/menu.html')

class Order(View):
    def get(self, request, *args, **kwargs):
        Sides = MenuItem.objects.filter(category__name__contains='Sides')
        Drinks = MenuItem.objects.filter(category__name__contains='Soft Drinks')
        Beer = MenuItem.objects.filter(category__name__contains='Beer, Soda, Ciders')
        Pizza = MenuItem.objects.filter(category__name__contains='Pizza')
        Sandwich = MenuItem.objects.filter(category__name__contains='Breakfast Sandwich')
        Dip = MenuItem.objects.filter(category__name__contains='Dipping Sauce')
        Bagel = MenuItem.objects.filter(category__name__contains='New York Bagel')
        Salad = MenuItem.objects.filter(category__name__contains='Salad')
        Pasta = MenuItem.objects.filter(category__name__contains='Pasta')

        context = {
            'Sides': Sides,
            'Drinks': Drinks,
            'Beer': Beer,
            'Pizza': Pizza,
            'Sandwich': Sandwich,
            'Dip': Dip,
            'Bagel': Bagel,
            'Salad': Salad,
            'Pasta': Pasta
        }

        return render(request, 'customer/pizza-gh-pages/order.html', context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')

        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')

        for item in items:
            menu_item = MenuItem.objects.get(pk=int(item))
            items_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }

            order_items['items'].append(items_data)

            price = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])

        order = OrderModel.objects.create(
            price=price,
            name=name,
            email=email,
            phone=phone,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
        )
        order.items.add(*item_ids)

        #Send mail after everything is done
        body = ('Thank you for your order! Your food is being made and will be delivered soon!\n'
                f'Your total: {price}\n'
                'Thank you again for your order!')

        send_mail(
            'Thank You For Your Order!',
            body,
            'example@example.com',
            [email],
            fail_silently=False,
        )

        context = {
            'items': order_items['items'],
            'price': price
        }

        return redirect('order-confirmation', pk=order.pk)

class OrderConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)

        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
        }

        return render(request, 'customer/pizza-gh-pages/order-confirmation.html', context)

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)
        if data['isPaid']:
            order = OrderModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()
        return redirect('payment-confirmation')

class OrderPayConfirmation(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/pizza-gh-pages/order-pay-confirmation.html')

class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/pizza-gh-pages/menu.html', context)

class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")

        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__contains=query)
        )

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/pizza-gh-pages/menu.html', context)