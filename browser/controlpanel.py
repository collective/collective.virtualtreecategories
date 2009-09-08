import simplejson
from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility, adapts
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.virtualtreecategories.browser.interfaces import IVirtualTreeCategoriesSettingsView
from collective.virtualtreecategories.interfaces import IVirtualTreeCategoryConfiguration
from collective.virtualtreecategories.interfaces import IVirtualTreeCategoryWidgetAware
from collective.virtualtreecategories.config import CATEGORY_SPLITTER
import logging
from sets import Set

logger = logging.getLogger('vtc-controlpanel')

class VirtualTreeCategoriesSettingsView(BrowserView):
    implements(IVirtualTreeCategoriesSettingsView)
    adapts(IPloneSiteRoot)
    
    template=ViewPageTemplateFile('controlpanel.pt')

    @view.memoize_contextless
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx 
            For example: catalog, membership, url
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/tools.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_tools")

    @view.memoize_contextless
    def portal_state(self):
        """ returns 
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/portal.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_portal_state")

    def all_keywords(self):
        vals =  list(self.tools().catalog().uniqueValuesFor('Subject'))
        vals.sort()
        return vals
        
    def widget_replaced(self):
        """ returns true if widget is currently being replaced """
        storage = IVirtualTreeCategoryConfiguration(self.context)
        return storage.enabled
        
    def __call__(self):
        if self.request.form.get('replace_widget_marker', '0') == '1':
            # form submitted
            value = self.request.form.get('replace_widget', False) == '1'
            storage = IVirtualTreeCategoryConfiguration(self.context)
            storage.enabled = value
            # todo portal message
        return self.template()
        
class CategoryKeywords(BrowserView):
    
    @view.memoize_contextless
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx 
            For example: catalog, membership, url
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/tools.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_tools")

    def _category_path_from_request(self, path=None):
        if path is None:
            category_path = self.request.form.get('category_path')
        else:
            category_path = path
        if not category_path:
            return []
        if isinstance(category_path, basestring):
            category_path = category_path.split(',')
        category_path.reverse()
        # omit root node
        category_path = category_path and category_path[1:]
        return category_path
    
    def get_category_keywords(self):
        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        portal = getUtility(IPloneSiteRoot)
        category_path = self._category_path_from_request()
        if not category_path:
            kws = []
        else:
            kws = IVirtualTreeCategoryConfiguration(portal).get(category_path)
        return simplejson.dumps(dict(keywords = kws))

    def save_category_keywords(self):
        portal = getUtility(IPloneSiteRoot)
        category_path = self._category_path_from_request()
        kws = self.request.form.get('kws', [])
        if isinstance(kws, basestring):
            kws = kws.split(',')
        if not category_path:
            return 'No valid category selected'
        logger.info('Going to save %d keywords to category %r' % (len(kws), category_path))
        IVirtualTreeCategoryConfiguration(portal).set(category_path, kws)
        self.request.response.setHeader('Content-Type', 'text/plain; charset=utf-8')
        return simplejson.dumps(dict(
                                    message='Category %s saved' % category_path[-1],
                                    keywords=kws
                                    ))

    def categories_tree(self):
        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        storage = IVirtualTreeCategoryConfiguration(getUtility(IPloneSiteRoot))
        # inject root node
        root = dict(
          attributes = { 'id' : "root-node", 'rel': 'root' }, 
          state = "open", 
          data = "Root node",
          children = storage.category_tree()
         )
        return simplejson.dumps(root)

    def category_added_renamed(self):
        storage = IVirtualTreeCategoryConfiguration(getUtility(IPloneSiteRoot))
        old_id = self.request.form.get('old_id')
        new_name = self.request.form.get('new_name')
        if not new_name:
            return 'Missing new name.'
        if not old_id:
            # create new node
            # strip last element from category_path, because it is newly created category name which does not exist yet
            category_path = self._category_path_from_request()[:-1]
            new_id = storage.add_category(category_path, new_name)
            if new_id:
                result = simplejson.dumps(dict(
                                           msg = 'Category created',
                                           new_id = new_id,
                                           result = True))
            else:
                result = simplejson.dumps(dict(
                                           msg = 'Category creation error!',
                                           new_id = '',
                                           result = False))
        else:
            # rename old node
            category_path = self._category_path_from_request()
            new_id = storage.rename_category(category_path, old_id, new_name)
            if new_id:
                result = simplejson.dumps(dict(
                                               msg = 'Category renamed',
                                               new_id = new_id,
                                               result = True))
            else:
                result = simplejson.dumps(dict(
                                               msg = 'Could not rename category.',
                                               new_id = '',
                                               result = False))
        return result
        
    def category_removed(self):
        storage = IVirtualTreeCategoryConfiguration(getUtility(IPloneSiteRoot))
        category_path = self._category_path_from_request()
        if not category_path:
           msg = 'You can''t not remove root category. Please reload page.'
        else:
            result = storage.remove_category(category_path)
            if result:
               msg = 'Category removed.'
            else:
               msg = 'Could not remove category. Please reload page.'
        return simplejson.dumps(dict( msg = msg,
                                      result = result))

    def list_keywords_by_categories(self):
        storage = IVirtualTreeCategoryConfiguration(getUtility(IPloneSiteRoot))
        # categories - list of lists where the sublist is category_path
        categories = self.request.form.get('categories', [])
        # list of keywords already assigned to the content
        selected   = self.request.form.get('selected', [])
        if isinstance(categories, basestring):
            categories = [categories]
        if isinstance(selected, basestring):
            selected = [selected]
        result = set()
        if categories:
            for category in categories:
                path = self._category_path_from_request(category)
                result.update(storage.get(path))
        else:
            result =  set(self.tools().catalog().uniqueValuesFor('Subject'))
            sorted(result)
        result = result.difference(selected)
        return simplejson.dumps(dict(keywords=list(result)))
