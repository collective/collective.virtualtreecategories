Introduction
============

This project aims to virtualize Plone default keywords (categories), which are
flat, to the tree. Contains Archetypes widget, based on InAndOut widget, which
replaces Plone's default widget for categories and contains configlet which
allows to assign flat keywords to virtual tree defined in the configlet.

Site manager defines virtual tree nodes and assigns keywords to the nodes. One
keyword may be assigned to any number of nodes (0-all).

Archetypes widget contains javascript based filter which allows to filter out
unwanted nodes and displays keywords in the selected node(s) only. Keywords are
stored in the same way as in Plone default so storage is 100% compatible and
don't require any migrations. You can always remove this package and your
content-keywords assignment stays untouched.

Please note, this package '''does not''' replace AT KeywordWidget of Subject
(Categories) field. It means you may define categories tree but you can't test
keyword selection in the conten type Categorization tab. You may uncomment part
of code in widget.py or use the following example in your custom package::

    from collective.virtualtreecategories.widget import VirtualTreeCategoriesWidget
    from Products.ATContentTypes.content.document import ATDocumentSchema
    old = ATDocumentSchema['subject'].widget
    ATDocumentSchema['subject'].widget = VirtualTreeCategoriesWidget(label=old.label, description=old.description)
    del old

