
INGREDIENTS = [
    'baking powder', 'beans', 'beef', 'butter', 'carrot', 'cheese', 'chicken', 
    'cream', 'eggplant', 'eggs', 'garlic', 'flour', 'mayonnaise', 'milk', 
    'mushrooms', 'olive oil', 'onion', 'pasta', 'pork', 'potato', 'rice', 
    'sugar', 'tomato', 'zucchini']


# Check if user searched by name, if yes query database
name = ""
if name == "":
    dishes = [{'id': 36, 'name': 'bigos', 'user': '4', 'dish_id': 36, 'baking_powder': 0, 'beans': 0, 'beef': 0, 'butter': 0, 'carrot': 1, 'cheese': 0, 'chicken': 0, 'cream': 0, 'eggplant': 0, 'eggs': 0, 'garlic': 1, 'flour': 0, 'mayonnaise': 0, 'milk': 0, 'mushrooms': 0, 'olive_oil': 0, 'onion': 1, 'pasta': 0, 'pork': 1, 'potato': 0, 'rice': 0, 'sugar': 0, 'tomato': 0, 'zucchini': 0, 'morning': None, 'noon': None, 'evening': 1}, {'id': 37, 'name': 'ryż', 'user': '4', 'dish_id': 37, 'baking_powder': 0, 'beans': 0, 'beef': 0, 'butter': 0, 'carrot': 0, 'cheese': 0, 'chicken': 0, 'cream': 0, 'eggplant': 0, 'eggs': 0, 'garlic': 0, 'flour': 0, 'mayonnaise': 0, 'milk': 0, 'mushrooms': 0, 'olive_oil': 0, 'onion': 0, 'pasta': 0, 'pork': 0, 'potato': 0, 'rice': 1, 'sugar': 0, 'tomato': 0, 'zucchini': 0, 'morning': 1, 'noon': None, 'evening': None}]
else:
    dishes = "Bigos"

dishes_avilable = []

# Check for checked(checkbox) time
times = []
if len(times) > 0:
    for time in times:
        for dish in dishes:
            if dish[time] == None:
                dishes.remove(dish)

# Check for checked ingredients
ingredients_avilable = ["carrot", "garlic", "onion", "pork"]
if len(ingredients_avilable) > 0:
    ingredients_unavilable = INGREDIENTS.copy()
    for ingredient in ingredients_avilable:
            ingredients_unavilable.remove(ingredient)    

    #loop over dishes, checking if ingredients needed for the dish are avilable
    for dish in dishes:
        #check is a variable to determine if a recipe had an ingredient that is unavilable
        check = True
        for info in dish:
            if dish[info] == 1:
                if info in ingredients_unavilable:
                    check = False
                    continue
        if check:
            dishes_avilable.append(dish["name"])

print(dishes_avilable)
'''if len(dishes) == 0:
    print("empty list")

for dish in dishes:
    print(dish["name"])'''
