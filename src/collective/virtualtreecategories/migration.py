from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger('c.vtc-migration')

try:
    from plone.app.upgrade import v40
    v40  # pyflakes
    HAS_PLONE4 = True
except ImportError:
    HAS_PLONE4 = False


def migrateTo0004(context):
    if not HAS_PLONE4:
        logger.info('Not on Plone4. Ignore collective.virtualtreecategories\
             migration 0004')
    else:
        javascript_tool = getToolByName(context, 'portal_javascripts', None)
        if javascript_tool is not None:
            resource_id = '++resource++jquery-1.3.2.min.js'
            if javascript_tool.getResource(resource_id):
                javascript_tool.unregisterResource(resource_id)
                jq = aq_inner(javascript_tool.getResource('jquery.js'))
                if jq is not None and not jq.getEnabled():
                    # resource exists, but is not enabled
                    jq.setEnabled(True)
                javascript_tool.cookResources()
                logger.info('collective.virtualtreecategories migration\
                   0004 finished.')
