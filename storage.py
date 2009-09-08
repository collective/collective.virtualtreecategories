from zope.interface import implements
from zope.component import adapts, getUtility
from zope.annotation import IAnnotations
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from persistent import Persistent
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.virtualtreecategories.interfaces import IVirtualTreeCategoryConfiguration, \
                                                        VirtualTreeCategoriesError
                                                        
from collective.virtualtreecategories.config import CATEGORY_SPLITTER, \
                                                    VTC_ANNOTATIONS_KEY, \
                                                    VTC_ENABLED_ANNOTATIONS_KEY
from BTrees.OOBTree import OOBTree
from zope.app.container.ordered import OrderedContainer

from types import ListType, TupleType
ListTypes = (ListType, TupleType)

import logging
logger = logging.getLogger('virtualtreecategories-storage')

class Category(OrderedContainer):
    id    = ''
    title = ''
    keywords = []
    
    def __init__(self, id, title=''):
        # XXX: This depends on implementation detail in OrderedContainer,
        # but it uses a PersistentDict, which sucks :-/
        OrderedContainer.__init__(self)
        self.id = id
        self.title = title or id
        self._data = OOBTree()

class VirtualTreeCategoryConfiguration(object):
    implements(IVirtualTreeCategoryConfiguration)
    adapts(IPloneSiteRoot)
    
    def __init__(self, context):
        self.context = context
        self.ann = IAnnotations(context)
        # category set here as root is not exposed to the public
        self.storage = self.ann.setdefault(VTC_ANNOTATIONS_KEY, Category('root-node', 'Root'))

    def get_enabled(self):
        return self.ann.get(VTC_ENABLED_ANNOTATIONS_KEY, False)

    def set_enabled(self, value):
        self.ann[VTC_ENABLED_ANNOTATIONS_KEY] = value
    enabled = property(get_enabled, set_enabled)

    def _find_node(self, category_path):
        """ Returns node in path or root node """
        if not isinstance(category_path, ListTypes): 
            path = category_path.split(CATEGORY_SPLITTER) 
        else: 
            path = category_path 
        dpath = self.storage
        if category_path and path:
            # category_path may be empty string (root category)
            for item_id in path:
                dpath = dpath.get(item_id, None)
                if dpath is None:
                    return None
        return dpath

    def add_category(self, category_path, category_name):
        node = self._find_node(category_path)
        norm = getUtility(IIDNormalizer)
        category_id = norm.normalize(safe_unicode(category_name))
        if node.get(category_id, None) is not None:
            raise VirtualTreeCategoriesError('Category already exists')
        else:
            node[category_id] = Category(category_id, category_name)
            logger.info('Category %s (%s) added' % (category_name, category_id))
        return category_id

    def category_tree(self):
        def add_subkeys(node):
            res = []
            for k, category in node.items():
                item = dict(attributes = dict(id=category.id, rel='folder'),
                            state = 'closed',
                            data  = category.title,
                            children = add_subkeys(category)
                           )
                res.append(item)
            return res
        return add_subkeys(self.storage)
        
    def remove_category(self, category_path):
        node = self._find_node(category_path)
        if node is not None:
            parent = node.__parent__
            del parent[node.id]
            logger.info('Category %s (%s) removed' % (node.title, node.id))
            del node
            return True
        else:
            return False

    def rename_category(self, category_path, old_category_id, new_name):
        node = self._find_node(category_path)
        if node is not None:
            parent = node.__parent__
            norm = getUtility(IIDNormalizer)
            new_id = norm.normalize(safe_unicode(new_name))
            node.id = new_id
            node.title = new_name

            # Fix order of items (be sure item is on the same position as before)
            # Copy previous order but replace old_category_id with new id
            # Finally updateOrder of the parent's items
            new_order = []
            for item in list(parent.keys()):
                if item == old_category_id:
                    new_order.append(new_id)
                else:
                    new_order.append(item)
            del parent[old_category_id]
            parent[new_id] = node
            parent.updateOrder(new_order)
            logger.info('Category %s renamed to %s (%s)' % (old_category_id, new_name, new_id))
            return new_id
        else:
            return False
            
    def set(self, category_path, keywords):
        node = self._find_node(category_path)
        if node is not None:
            node.keywords = keywords
            logger.info('Keywords for category %s set to %r' % (node.title, keywords))
            return True
        else:
            return False

    def get(self, category_path):
        node = self._find_node(category_path)
        if node is not None:
            return node.keywords
        else:
            # this may happen eg. when new category is created
            return []
