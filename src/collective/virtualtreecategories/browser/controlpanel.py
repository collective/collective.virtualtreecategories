import simplejson
import urllib
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility, adapts
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.virtualtreecategories.browser import interfaces as binterfaces
from collective.virtualtreecategories import interfaces
from collective.virtualtreecategories import VTCMessageFactory as _
from zope.i18n import translate
import logging

logger = logging.getLogger('vtc-controlpanel')
IVTCC = interfaces.IVirtualTreeCategoryConfiguration


class VirtualTreeCategoriesSettingsView(BrowserView):
    implements(binterfaces.IVirtualTreeCategoriesSettingsView)
    adapts(IPloneSiteRoot)

    template = ViewPageTemplateFile('controlpanel.pt')

    @view.memoize_contextless
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx
            For example: catalog, membership, url
            -> plone.app.layout.globals.tools
        """
        return getMultiAdapter((self.context, self.request),
                               name=u"plone_tools")

    @view.memoize_contextless
    def portal_state(self):
        """ returns
            -> plone.app.layout.globals.portal
        """
        return getMultiAdapter((self.context, self.request),
                               name=u"plone_portal_state")

    def all_keywords(self):
        vals = list(self.tools().catalog().uniqueValuesFor('Subject'))
        vals.sort()
        return vals

    def widget_replaced(self):
        """ returns true if widget is currently being replaced """
        storage = (self.context)
        return storage.enabled

    def unassigned_keywords(self):
        """ list all keywords not assigned to any category """
        vals = list(self.tools().catalog().uniqueValuesFor('Subject'))
        util = IVTCC(self.portal_state().portal())
        for category in util.list_categories("/"):
            for kw in util.list_keywords(category.path, recursive=True):
                if kw in vals:
                    vals.remove(kw)
        return vals

    def __call__(self):
        if self.request.form.get('replace_widget_marker', '0') == '1':
            # form submitted
            value = self.request.form.get('replace_widget', False) == '1'
            storage = IVTCC(self.context)
            storage.enabled = value
            # todo portal message
        return self.template()


class CategoryKeywords(BrowserView):

    @view.memoize_contextless
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx
            For example: catalog, membership, url
            -> plone.app.layout.globals.tools
        """
        return getMultiAdapter((self.context, self.request),
                               name=u"plone_tools")

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
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        portal = getUtility(IPloneSiteRoot)
        category_path = self._category_path_from_request()
        if not category_path:
            kws = []
        else:
            config = IVTCC(portal)
            kws = config.list_keywords(category_path, recursive=False)
        return simplejson.dumps(dict(keywords=kws))

    def save_category_keywords(self):
        portal = getUtility(IPloneSiteRoot)
        category_path = self._category_path_from_request()
        kws = self.request.form.get('kws', [])
        if isinstance(kws, basestring):
            kws = kws.split(',')
        if not category_path:
            return 'No valid category selected'
        logger.info('Going to save %d keywords to category %r' % (len(kws),
                                                              category_path))
        IVTCC(portal).set(category_path, kws)
        self.request.response.setHeader('Content-Type',
                                        'text/plain; charset=utf-8')
        return simplejson.dumps(dict(
                                    message=translate(_('Category saved'),
                                                      context=self.request),
                                    keywords=kws
                                    ))

    def categories_tree(self):
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        storage = IVTCC(getUtility(IPloneSiteRoot))
        # inject root node
        root = dict(
          attributes={'id': "root-node", 'rel': 'root'},
          state="open",
          data=translate(_("Root node"), context=self.request),
          children=storage.category_tree()
         )
        return simplejson.dumps(root)

    def category_added_renamed(self):
        storage = IVTCC(getUtility(IPloneSiteRoot))
        old_id = self.request.form.get('old_id')
        new_name = self.request.form.get('new_name')
        if not new_name:
            return 'Missing new name.'
        if not old_id:
            # create new node
            # strip last element from category_path, because it is newly
            # created category name which does not exist yet
            category_path = self._category_path_from_request()[:-1]
            new_id = storage.add_category(category_path, new_name)
            if new_id:
                result = simplejson.dumps(dict(
                                       msg=translate(_(u'Category created'),
                                                     context=self.request),
                                       new_id=new_id,
                                       result=True))
            else:
                result = simplejson.dumps(dict(
                               msg=translate(_(u'Category creation error!'),
                                             context=self.request),
                               new_id='',
                               result=False))
        else:
            # rename old node
            category_path = self._category_path_from_request()
            new_id = storage.rename_category(category_path, old_id, new_name)
            if new_id:
                result = simplejson.dumps(dict(
                                   msg=translate(_(u'Category renamed'),
                                                 context=self.request),
                                   new_id=new_id,
                                   result=True))
            else:
                result = simplejson.dumps(dict(
                               msg=translate(_(u'Could not rename category.'),
                                             context=self.request),
                               new_id='',
                               result=False))
        return result

    def category_removed(self):
        storage = IVTCC(getUtility(IPloneSiteRoot))
        category_path = self._category_path_from_request()
        if not category_path:
            msgid = _(u"You can't remove root category. Please reload page.")
            msg = translate(msgid, context=self.request),
            result = False
        else:
            result = storage.remove_category(category_path)
            if result:
                msg = translate(_(u'Category removed.'), context=self.request)
            else:
                msgid = _(u'Could not remove category. Please reload page.')
                msg = translate(msgid, context=self.request)
        return simplejson.dumps(dict(msg=msg, result=result))

    def list_keywords_by_categories(self):
        storage = IVTCC(getUtility(IPloneSiteRoot))
        # categories - list of lists where the sublist is category_path
        categories = self.request.form.get('categories', [])
        # list of keywords already assigned to the content
        selected = self.request.form.get('selected', [])

        if isinstance(categories, basestring):
            categories = [categories]
        if isinstance(selected, basestring):
            selected = [selected]
        result = set()
        if categories:
            for category in categories:
                path = self._category_path_from_request(category)
                result.update(storage.list_keywords(path, recursive=False))
        else:
            result = set(self.tools().catalog().uniqueValuesFor('Subject'))
            sorted(result)
        result = result.difference(selected)
        return simplejson.dumps(dict(keywords=list(result)))

    def get_content_count(self, kw):
        kw = urllib.unquote_plus(kw)
        count = len(self.tools().catalog().searchResults(Subject=kw))
#        print kw, count
        return count
