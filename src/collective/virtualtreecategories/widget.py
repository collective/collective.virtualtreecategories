#import types
#from zope.component import ComponentLookupError
#from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.AddRemoveWidget.AddRemoveWidget import AddRemoveWidget
from Products.Archetypes.Registry import registerWidget

RESOURCE = '++resource++collective.virtualtreecategories'


class VirtualTreeCategoriesWidget(AddRemoveWidget):
    _properties = AddRemoveWidget._properties.copy()
    _properties.update({
        'macro': "virtualtreecategories_widget",
        'helper_js': ('widget_addremove_vars.js',
                      'widget_addremove.js',
                      RESOURCE + '.jsTree/css.js',
                      RESOURCE + '.jsTree/jquery.tree_component.js',
                      'virtualtreecategories_widget.js'),
        'helper_css': (RESOURCE + '.jsTree/tree_component.css',
                       RESOURCE + '.resources/virtualtreecategories.css', ),
        })

    security = ClassSecurityInfo()


registerWidget(
    VirtualTreeCategoriesWidget,
    title='Virtual Tree Categories Widget',
    description=('You can filter out unwanted available keywords'),
    used_for=('Products.Archetypes.Field.LinesField', )
    )
