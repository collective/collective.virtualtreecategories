import zope.component
import zope.interface
from z3c.form.interfaces import IFormLayer, IFieldWidget
from z3c.form.widget import FieldWidget
from collective.z3cform.keywordwidget.widget import InAndOutKeywordWidget
from collective.z3cform.keywordwidget.interfaces import IKeywordCollection
from collective.z3cform.keywordwidget.field import KeywordsDataConverter
from zope.interface import implementsOnly
from collective.virtualtreecategories.dexterity import interfaces


class VirtualTreeCategoriesWidget(InAndOutKeywordWidget):
    implementsOnly(interfaces.IVirtualTreeCategoriesWidget)
    klass = u'virtualtreecategories-widget'


@zope.component.adapter(IKeywordCollection, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def VirtualTreeCategoriesFieldWidget(field, request):
    """ IFieldWidget factory for VirtualTreeCategoriesWidget
    """
    return FieldWidget(field, VirtualTreeCategoriesWidget(request))


class VirtualTreeCategoriesDataConverter(KeywordsDataConverter):
    """A special converter between collections and sequence widgets."""
    zope.component.adapts(IKeywordCollection,
                          interfaces.IVirtualTreeCategoriesWidget)
