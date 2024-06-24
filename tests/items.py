from flowapi import Media, Item, Component, BoutonText

item = Item(name="test")
print(item)
print(item.get_xml())
print(item.get_item_xml())

item = Component(name="test")
print(item)
print(item.get_xml())
print(item.get_item_xml())

print("Bouton Text")
item = BoutonText()
print(item)
print(item.name)
print(item.nov_component_identifier)
print(item.get_xml())
print(item.get_item_xml())
print("\nMedia")
item = Media(path="test.png")
print(item)
item.set_path("test_2.png")
print(item.name)
print(item.get_xml())
print(item.get_item_xml())
Media.get_placeholder()
