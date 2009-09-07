import types
from zope.component import ComponentLookupError
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.AddRemoveWidget.AddRemoveWidget import AddRemoveWidget
from Products.Archetypes.Registry import registerWidget

class VirtualTreeCategoriesWidget(AddRemoveWidget):
    _properties = AddRemoveWidget._properties.copy()
    _properties.update({
        'macro'                 : "virtualtreecategories_widget",
        'helper_js'             : ('widget_addremove_vars.js',
                                   'widget_addremove.js',
                                   "++resource++collective.virtualtreecategories.jsTree/css.js",
                                   "++resource++collective.virtualtreecategories.jsTree/tree_component.js",
                                   "virtualtreecategories_widget.js"),
        'helper_css'            : ('++resource++collective.virtualtreecategories.jsTree/tree_component.css',),
        })

    security = ClassSecurityInfo()

registerWidget(VirtualTreeCategoriesWidget,
               title='Virtual Tree Categories Widget',
               description=('You can filter out unwanted available keywords'),
               used_for=('Products.Archetypes.Field.LinesField',)
               )
