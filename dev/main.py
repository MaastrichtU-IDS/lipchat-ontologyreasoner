from owlready2 import *

if __name__ == "__main__":

    onto_path.append('data/ontology/test/')
    onto = get_ontology("data/ontology/test/pizza_onto.owl").load()
    # onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl")
    onto.load()

    # Create new classes in the ontology, possibly mixing OWL constructs and Python methods:
    class NonVegetarianPizza(onto.Pizza):
        equivalent_to = [
            onto.Pizza
            & (onto.has_topping.some(onto.MeatTopping) | onto.has_topping.some(onto.FishTopping))
        ]

        def eat(self): print("I love meat!")
    class VegetarianPizza(onto.Pizza):
        equivalent_to = [
            onto.Pizza
            & (onto.has_topping.some(onto.CheeseTopping) | onto.has_topping.some(onto.TomatoTopping))
        ]

        def eat(self): print("I'm vegetarian!")

    # Create a vegetarian test pizza
    test_pizza = onto.Pizza("test_pizza_owl_identifier")
    test_pizza.has_topping = [onto.CheeseTopping(),
                              onto.TomatoTopping()]

    # Execute HermiT and reparent instances and classes
    sync_reasoner()
    print(test_pizza.__class__)
    # the correct eat() method should be called; is a vegetarian
    print(test_pizza.eat())

    # add some meat and try again
    test_pizza.has_topping.append(onto.MeatTopping())
    sync_reasoner()
    print(test_pizza.__class__)
    print(test_pizza.eat())

    # Export owl file
    onto.save()