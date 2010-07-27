from zope.i18n import MessageFactory
VTCMessageFactory = MessageFactory('collective.virtualtreecategories')

from collective.virtualtreecategories import widget

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
