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

The controlpanel contains checkbox, which allows to set the
VirtualTreeCategories widget as default widget for the Subject field of all
Archetypes based content types.

Installation
------------

Install using buildout.cfg. If you want to use this product in Plone3, you
must specify [plone3] extra due to dependency on collective.js.jquery (this
package requires jQuery 1.3+). 

Plone 3::

    eggs = 
        ...
        collective.virtualtreecategories [plone3]

Plone 4::

    eggs = 
        ...
        collective.virtualtreecategories
  
Dexterity::

    eggs = 
        ...
        collective.virtualtreecategories [dexterity]


Control panel
-------------

.. figure:: http://plone.org/products/collective.virtualtreecategories/documentation/manuals/project-description/Control%20panel.png/image_preview

Archetypes widget
-----------------

.. figure:: http://plone.org/products/collective.virtualtreecategories/documentation/manuals/project-description/AT%20Widget.png/image_preview

Dexterity widget
----------------

If you want to use this widget in your dexterity content type, you need to 
specify [dexterity] extra in eggs section of the buildout. You also 
need to use Keyword field from collective.z3cform.keywordwidget for your schema field
and finally set VirtualTreeCategoriesFieldWidget as widget for the field.
**Please note, this feature requires collective.z3cform.keywordwidget > 1.1.1 or svn 
branch currently.**

Example::

    from zope import schema
    from plone.directives import form
    from collective.z3cform.keywordwidget.field import Keywords
    from collective.virtualtreecategories.dexterity.widget import VirtualTreeCategoriesFieldWidget

    class ICustomCategorization(form.Schema):

        subjects = Keywords(
            title=u'Categories',
            value_type=schema.TextLine(),
            required=False,
            missing_value=(),
            index_name='Subject',
            )
        form.widget(subjects=VirtualTreeCategoriesFieldWidget)

        new_subjects = schema.Tuple(
            title=u'New categories',
            description=u'Enter new keywords, one per line.',
            value_type=schema.TextLine(),
            required=False,
            missing_value=(),
            )
