#from zope import schema
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class IVirtualTreeCategoriesSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class IVirtualTreeCategoryWidgetAware(Interface):
    """ Marker interface for schemamodifier which replaces KeywordWidget of
        the Subject field with VTC widget"""


class IVirtualTreeCategoryConfiguration(Interface):
    """ Configuration adapter which allows to set/read categories
        from the stroage """

    def set(category_path, keywords):
        """ Set (assing) keywords to the category.
            @category_path: string in form Level1/Level11/Level111 or
                            list ['Level1', 'Level11', 'Level111']
            @keywords: List of keywords to be assigned to this category
            Returns True/False
            """

    def get(category_path):
        """ Returns list of keywords assigned to the category.
            @category_path: string in form Level1/Level11/Level111 or
                            list ['Level1', 'Level11', 'Level111']
            """

    def category_tree():
        """ Returns categories in the tree form suitable for serializing using XML or JSON.
            This is JSON format accepted by the jsTree component:
            http://www.jstree.com/reference/_examples/1_datasources.html
                [
                 {
                  attributes: { id: "category1", [attribute: "attribute_value"] },
                  state: "closed" or "open",
                  data: "Category 1"
                 },
                 {
                  attributes: { id: "category2", [attribute: "attribute_value"] },
                  state: "closed" or "open",
                  data: "Category 2",
                  children: [
                                 {
                                  attributes: { id: "category2a", [attribute: "attribute_value"] },
                                  state: "closed" or "open",
                                  data: "Category 2-A"
                                 }
                            ]
                 },
               ]

            Implementation note: There must be exactly one root node in the
            default (empty) jsTree to be able to create new nodes from the root
            using right-click. The root node should be added by controlpanel
            component, because it is not stored in the storage and it is jsTree
            requirement. Another JS component may allow creation of nodes
            without root category or it is possible to show button "Create new
            node". Another option is to store root level node and generate tree
            including this node..
        """

    def add_category(category_path, category_name):
        """ Create new category node as child of the category_path
            Returns new category id.
        """

    def remove_category(category_path):
        """ Remove node at the end of category path including all child
            nodes
            Returns True/False
        """

    def rename_category(category_path, old_category_id, new_name):
        """ Rename category.
            @category_path contains path to the category node (last component
                           is renamed node).
            @old_category_id is id="" attribute of the renamed node
            @new_name is new title supplied by the user.
            Storage is expected to:
                - find old node by category_path and old_category_id
                - change category title
                - change category id to new generated id

            Returns new category id.
        """

    def list_categories(path):
        """ List categories on the specified path only. """

    def list_keywords(path):
        """ List keywords assigned to the specified path. """

    def by_keyword(keyword=None):
        """ Returns dictionary with keywords as keys
            and list of category paths as values.
            If keyword is in more than one category,
            all paths are returned as separate items.
            If keyword is in two categories within the same tree, all
            categories are returned as separate items.
            Example:
            {'kw1': ['C11', 'C1'], ['D1']}
            If kw1 would be directly assigned to C1 as well, result is:
            {'kw1': ['C11', 'C1'], ['C1'], ['D1']}

            WARNING: this method may be expensive to call with large number of
            categories and/or keywords.
            If keyword parameter is None, all keywords are returnend,
            otherwise just dict with one key is returned.
        """


class VirtualTreeCategoriesError(Exception):
    """ """
