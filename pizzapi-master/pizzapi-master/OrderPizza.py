from tkinter import Y
from pizzapy import Customer, StoreLocator, Order, ConsoleInput, CreditCard

#customer = Customer("Mark", "Triassi", "markjtriassi@gmail.com", "9259890841","406 Eucalyptus Drive, Redlands, CA, 92373" )
#customer = ConsoleInput.get_new_customer()
customer = ConsoleInput.get_customer()

my_local_dominos = StoreLocator.find_closest_store_to_customer(customer)
print("\nClosest Store:")
print(my_local_dominos)
print("\nMenu\n")



def searchMenu(menu):
    print("You are now searching the menu...")
    item = input("Type an item to look for: ").strip().lower()
    if len(item) > 1:
        item = item[0].upper() + item[1:]
        print(f"Results for: {item}\n")
        menu.search(Name = item)
    else:
        print("No Results")


def addToOrder(order):
    print("Please type the codes of the items you'd like to order")
    print("Press ENTER to stop ordering.")
    while True:
        item = input("Code: ").upper()
        try:
            order.add_item(item)
        except:
            if item == "":
                break
            print("Invalid")

menu = my_local_dominos.get_menu()
order = Order.begin_customer_order(customer, my_local_dominos, "us")

while True:
    searchMenu(menu)
    addToOrder(order)
    answer = input("Would you like to add more items (y/n)?")
    if answer.lower() not in ["yes", "y"]:
        break


total = 0
print("\nYour order is as follows: ")
for item in order.data["Products"]:
    price = item["Price"]
    #item['Tags'][u'Toppings'] = u'N=1,P=1,J=1'
    #print(item['Tags'])
    print(item["Name"] + " $" + price)
    total += float(price)
    
print("\nYour order total is: $" + str(total) + " + TAX")

card = ConsoleInput.get_card()

ans = input("Would you like to place this order? (Y/N)")
if ans.lower() in ['y','yes']:
    order.place(card)
    my_local_dominos.place_order(order, card)
    print("Order Placed")
else:
    print("Goodbye")




