# Extends ATFile with video metadata fields and with image thumnails

from zope.component import adapts, getUtility
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Archetypes.Widget import KeywordWidget

from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender

from collective.virtualtreecategories import interfaces, widget


class VirtualTreeCategoriesWidgetModifier(object):
    """VirtualTreeCategories widget modifier"""

    adapts(interfaces.IVirtualTreeCategoryWidgetAware)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)

    layer = interfaces.IVirtualTreeCategoriesSpecific

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        portal = getUtility(IPloneSiteRoot)
        storage = interfaces.IVirtualTreeCategoryConfiguration(portal)
        field = schema.get('subject', None)

        if field:
            if storage.enabled:
                if not isinstance(field.widget,
                                  widget.VirtualTreeCategoriesWidget):
                    oldlabel = field.widget.label
                    olddesc = field.widget.description
                    roleBasedAdd = getattr(field.widget, 'roleBasedAdd', False)
                    new_field = field.copy()
                    new_field.widget = widget.VirtualTreeCategoriesWidget(
                                           label=oldlabel,
                                           description=olddesc,
                                           role_based_add=roleBasedAdd)
                    schema.replaceField('subject', new_field)

            elif isinstance(field.widget, widget.VirtualTreeCategoriesWidget):
                # use KeywordWidget, because someone turned VTC on and then off
                oldlabel = field.widget.label
                olddesc = field.widget.description
                roleBasedAdd = getattr(field.widget, 'role_based_add', False)
                new_field = field.copy()
                new_field.widget = KeywordWidget(
                                       label=oldlabel,
                                       description=olddesc,
                                       roleBasedAdd=roleBasedAdd)
                schema.replaceField('subject', new_field)
