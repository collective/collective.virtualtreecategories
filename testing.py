from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.PloneTestCase import installPackage

from collective.testcaselayer import ptc as tcl_ptc

class Layer(tcl_ptc.BasePTCLayer):
    """ set up basic testing layer """

    def afterSetUp(self):
        # load zcml for this package and its dependencies
        fiveconfigure.debug_mode = True
        from collective import virtualtreecategories
        zcml.load_config('testing.zcml', package=virtualtreecategories)
        fiveconfigure.debug_mode = False
        # after which the required packages can be initialized
        installPackage('collective.virtualtreecategories', quiet=True)
        # finally load the testing profile
        self.addProfile('collective.virtualtreecategories:default')

from zope.annotation.attribute import AttributeAnnotations
from zope.component import provideAdapter
from collective.testcaselayer import ztc as tcl_ztc

class AttributeAnnotationsLayer(tcl_ztc.BaseZTCLayer):
    """Install annotations """

    def afterSetUp(self):
        provideAdapter(AttributeAnnotations)

layer = Layer(bases=[tcl_ptc.ptc_layer])
annotations_layer = AttributeAnnotationsLayer([tcl_ztc.ztc_layer])
