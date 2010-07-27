from zope.testing import doctest
from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from collective.virtualtreecategories import testing

ptc.setupPloneSite()
ptc.setupPloneSite('plone2')

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def test_suite():
    suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        'tests/multisite.txt',
        package='collective.virtualtreecategories',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    suite.layer = testing.layer
    return suite
