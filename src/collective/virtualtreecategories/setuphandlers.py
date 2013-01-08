from Products.CMFCore.utils import getToolByName

try:
    from plone.app.upgrade import v40
    v40  # pyflakes
    HAS_PLONE4 = True
except ImportError:
    HAS_PLONE4 = False


class NotInstallable(Exception):
    """ Package is not installable """


def installHandler(self):
    if self.readDataFile('virtualtreecategories-install.txt') is None:
        return

    portal = self.getSite()
    qi = getToolByName(portal, 'portal_quickinstaller')
    setup = getToolByName(portal, 'portal_setup')
    if not qi.isProductInstalled('AddRemoveWidget'):
        # there is no GS profile for AddRemoveWidget.
        qi.installProduct('AddRemoveWidget')

    if not HAS_PLONE4:
        # collective.js.jquery is Plone3 dependency only
        if not qi.isProductInstalled('collective.js.jquery'):
            if not qi.isProductInstallable('collective.js.jquery'):
                raise NotInstallable('Package collective.js.jquery is required. '
                                     'Please specify [plone3] extra in your buildout.cfg')
            else:
                setup.runAllImportStepsFromProfile('profile-collective.js.jquery:default')


def uninstall(self):
    if self.readDataFile('virtualtreecategories-uninstall.txt') is None:
        return

    portal = self.getSite()
    portal_conf = getToolByName(portal, 'portal_controlpanel')
    portal_conf.unregisterConfiglet('VirtualTreeCategories')
