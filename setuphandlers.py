from Products.CMFCore.utils import getToolByName

def installHandler(self):
    if self.readDataFile('virtualtreecategories-install.txt') is None:
        return

    portal = self.getSite()
    qi = getToolByName(portal, 'portal_quickinstaller')
    if not qi.isProductInstalled('AddRemoveWidget'):
        # there is no GS profile for AddRemoveWidget.
        qi.installProduct('AddRemoveWidget')
    
def uninstall(self):
    if self.readDataFile('virtualtreecategories-uninstall.txt') is None:
        return

    portal = self.getSite()
    portal_conf=getToolByName(portal,'portal_controlpanel')
    portal_conf.unregisterConfiglet('VirtualTreeCategories')

