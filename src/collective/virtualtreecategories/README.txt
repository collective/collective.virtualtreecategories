Virtual tree categories
-----------------------

    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> from zope.interface.verify import verifyClass
    >>> from collective.virtualtreecategories.storage import VirtualTreeCategoryConfiguration
    >>> from collective.virtualtreecategories.interfaces import IVirtualTreeCategoryConfiguration
    >>> from collective.virtualtreecategories.config import VTC_ANNOTATIONS_KEY
    >>> storage = VirtualTreeCategoryConfiguration(self.portal)
    >>> annotations = AttributeAnnotations(self.portal).get(VTC_ANNOTATIONS_KEY)
    >>> verifyClass(IVirtualTreeCategoryConfiguration, VirtualTreeCategoryConfiguration)
    True
    
    >>> len(annotations)
    0
    >>> storage.add_category('', 'Category 1')
    'category-1'
    >>> len(annotations)
    1
    >>> cat1 = annotations['category-1']
    >>> cat1.id
    'category-1'
    >>> cat1.title
    'Category 1'
    >>> cat1.keys()
    []
    >>> storage.add_category('category-1', 'Category 1a')
    'category-1a'
    >>> cat1a = cat1['category-1a']
    >>> cat1a.id
    'category-1a'
    >>> cat1a.title
    'Category 1a'
    >>> len(cat1a)
    0
    >>> len(annotations)
    1
    >>> storage.add_category('', 'Category 1')
    Traceback (most recent call last):
    ...
    VirtualTreeCategoriesError: Category already exists
    >>> storage.add_category('category-1', 'Category 1a')
    Traceback (most recent call last):
    ...
    VirtualTreeCategoriesError: Category already exists

Let's create some additional categories and try how they are serialized for the UI:

    >>> _ = storage.add_category('category-1', 'Category 1b')
    >>> _ = storage.add_category('category-1/category-1a', 'Category 1aa')
    >>> _ = storage.add_category('category-1/category-1a', 'Category 1ab')
    >>> _ = storage.add_category('category-1/category-1b', 'Category 1ba')
    >>> _ = storage.add_category('', 'Category 2')
    >>> _ = storage.add_category('category-2', 'Category 2a')
    >>> storage.category_tree()
    [{'attributes': {'id': 'category-1', 'rel': 'folder'}, 
      'state': 'closed', 
      'data': 'Category 1', 
      'children': [{'attributes': {'id': 'category-1a', 'rel': 'folder'}, 
                    'state': 'closed', 
                    'data': 'Category 1a', 
                    'children': [{'attributes': {'id': 'category-1aa', 'rel': 'folder'}, 
                                  'state': 'closed', 
                                  'data': 'Category 1aa', 
                                  'children': []}, 
                                 {'attributes': {'id': 'category-1ab', 'rel': 'folder'}, 
                                  'state': 'closed', 
                                  'data': 'Category 1ab', 
                                  'children': []}]}, 
                    {'attributes': {'id': 'category-1b', 'rel': 'folder'}, 
                     'state': 'closed', 
                     'data': 'Category 1b', 
                     'children': [{'attributes': {'id': 'category-1ba', 'rel': 'folder'}, 
                                   'state': 'closed', 
                                   'data': 'Category 1ba', 
                                   'children': []}]}]}, 
     {'attributes': {'id': 'category-2', 'rel': 'folder'}, 
      'state': 'closed', 
      'data': 'Category 2', 
      'children': [{'attributes': {'id': 'category-2a', 'rel': 'folder'}, 
                    'state': 'closed', 
                    'data': 'Category 2a', 
                    'children': []}]}]

Remove category
    
    >>> annotations['category-1']['category-1b'].get('category-1ba')
    <collective.virtualtreecategories.storage.Category object at ...>
    >>> storage.remove_category('category-1/category-1b/category-1ba') 
    True
    >>> annotations['category-1']['category-1b'].get('category-1ba', None) is None
    True
    
Can't remove non existing category
    
    >>> storage.remove_category('category-1/category-1b/category-1ba') 
    False

Rename category

    >>> annotations['category-1']['category-1a']
    <collective.virtualtreecategories.storage.Category object at ...>
    >>> storage.rename_category('category-1/category-1a', 'category-1a', 'Fresh category name')
    'fresh-category-name'
    >>> annotations['category-1'].get('category-1a', None) is None
    True
    >>> annotations['category-1']['fresh-category-name']
    <collective.virtualtreecategories.storage.Category object at ...>
    >>> annotations['category-1']['fresh-category-name'].id
    'fresh-category-name'
    >>> annotations['category-1']['fresh-category-name'].title
    'Fresh category name'
    >>> annotations['category-1']['fresh-category-name'].keys()
    ['category-1aa', 'category-1ab']
    
    Be sure category is on the same position as before
    >>> annotations['category-1'].keys()
    ['fresh-category-name', 'category-1b']
    
Set keywords to category

    >>> annotations['category-1']['category-1b'].keywords
    []
    >>> storage.set('category-1/category-1b', ['kw1', 'kw2'])
    True
    >>> storage.get('category-1/category-1b')
    ['kw1', 'kw2']

    >>> storage.get('category-1/dummy')
    []


